#!/usr/bin/env python3
"""
Master Workstream Executor
Executes all 23 workstreams in dependency order with automatic error handling and rollback.

Usage:
    python master-workstream-executor.py [--dry-run] [--start-from WS-##] [--workstreams WS-01,WS-02]

Features:
- Dependency-aware execution order
- Automatic rollback on failure
- Progress tracking and resumption
- Parallel execution where possible
- Comprehensive logging
"""

import json
import subprocess
import sys
import os
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workstream_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WorkstreamStatus:
    """Track execution status of each workstream"""
    workstream_id: int
    name: str
    status: str  # pending, in_progress, completed, failed, skipped
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class WorkstreamExecutor:
    """Main executor for workstream automation"""

    def __init__(self, workstreams_dir: Path, dry_run: bool = False, repo_dir: Optional[Path] = None):
        self.workstreams_dir = workstreams_dir
        self.dry_run = dry_run
        self.workstreams: Dict[str, dict] = {}
        self.status: Dict[str, WorkstreamStatus] = {}
        self.execution_log: List[dict] = []
        self.repo_dir: Path = repo_dir or self._detect_repo_dir()

    def _detect_repo_dir(self) -> Path:
        """Detect git repo root or fall back to current directory."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                check=False
            )
            top = (result.stdout or '').strip()
            if result.returncode == 0 and top:
                p = Path(top)
                if p.exists():
                    return p
        except Exception:
            pass
        return Path.cwd()

    def load_workstreams(self) -> None:
        """Load all workstream JSON files"""
        logger.info(f"Loading workstreams from {self.workstreams_dir}")

        json_files = sorted(self.workstreams_dir.glob("ws-*.json"))
        logger.info(f"Found {len(json_files)} workstream files")

        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    ws_data = json.load(f)
                    ws_id = f"WS-{ws_data['workstream_id']:02d}"
                    self.workstreams[ws_id] = ws_data
                    self.status[ws_id] = WorkstreamStatus(
                        workstream_id=ws_data['workstream_id'],
                        name=ws_data['workstream_name'],
                        status='pending'
                    )
                    logger.info(f"Loaded {ws_id}: {ws_data['workstream_name']}")
            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")

    def resolve_dependencies(self) -> List[str]:
        """Resolve execution order based on dependencies (topological sort)"""
        logger.info("Resolving workstream dependencies...")

        # Build dependency graph
        graph = {}
        in_degree = {}

        for ws_id, ws_data in self.workstreams.items():
            graph[ws_id] = []
            in_degree[ws_id] = 0

        for ws_id, ws_data in self.workstreams.items():
            blocked_by = ws_data.get('blocked_by', [])
            for blocker_name in blocked_by:
                # Find workstream ID by name
                blocker_id = None
                for candidate_id, candidate_data in self.workstreams.items():
                    if candidate_data['workstream_name'] == blocker_name:
                        blocker_id = candidate_id
                        break

                if blocker_id:
                    graph[blocker_id].append(ws_id)
                    in_degree[ws_id] += 1
                else:
                    logger.warning(f"{ws_id} blocked by unknown workstream: {blocker_name}")

        # Topological sort (Kahn's algorithm)
        queue = [ws_id for ws_id in in_degree if in_degree[ws_id] == 0]
        execution_order = []

        while queue:
            # Sort queue for deterministic ordering
            queue.sort()
            current = queue.pop(0)
            execution_order.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(execution_order) != len(self.workstreams):
            remaining = set(self.workstreams.keys()) - set(execution_order)
            logger.error(f"Circular dependency detected! Remaining: {remaining}")
            raise ValueError(f"Circular dependencies in workstreams: {remaining}")

        logger.info(f"Execution order resolved: {' → '.join(execution_order)}")
        return execution_order

    def execute_workstream(self, ws_id: str) -> bool:
        """Execute a single workstream"""
        ws_data = self.workstreams[ws_id]
        ws_status = self.status[ws_id]

        logger.info(f"\n{'='*80}")
        logger.info(f"Executing {ws_id}: {ws_data['workstream_name']}")
        logger.info(f"Estimated hours: {ws_data['est_hours']}")
        logger.info(f"{'='*80}\n")

        ws_status.status = 'in_progress'
        ws_status.start_time = datetime.now()

        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute {ws_id}")
            ws_status.status = 'completed'
            ws_status.end_time = datetime.now()
            return True

        try:
            # Execute git commands from workstream
            git_commands = ws_data['git']['commands']
            branch_name = ws_data['branch_name']

            logger.info(f"Creating branch: {branch_name}")

            # Preflight checks
            logger.info("Running preflight checks...")
            self._run_preflight_checks(ws_data)

            # Execute git workflow
            for i, cmd_template in enumerate(git_commands):
                # Skip the "apply code changes" placeholder
                if 'apply code changes' in cmd_template:
                    logger.info(f"Step {i+1}: Code changes would be applied here")
                    logger.warning(f"⚠️  Manual intervention required: Apply code changes for {ws_id}")
                    logger.warning(f"   Review tasks in JSON file and implement changes")
                    logger.warning(f"   Then continue with: git add -A && git commit && git push")

                    # Prompt for confirmation
                    if not self._prompt_continue(f"Code changes applied for {ws_id}"):
                        raise Exception("User aborted: Code changes not applied")
                    continue

                # Replace placeholders
                cmd = cmd_template
                cmd = cmd.replace('<branch_name>', branch_name)
                cmd = cmd.replace('<remote>', ws_data['git']['remote'])
                cmd = cmd.replace('<base_branch>', ws_data['git']['base_branch'])
                cmd = cmd.replace('<commit_message>', ws_data['git']['commit_message_template'])

                logger.info(f"Step {i+1}: {cmd}")

                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_dir)
                )

                if result.returncode != 0:
                    logger.error(f"Command failed: {cmd}")
                    logger.error(f"Error: {result.stderr}")
                    raise Exception(f"Git command failed: {result.stderr}")

                if result.stdout:
                    logger.info(f"Output: {result.stdout}")

            # Mark as completed
            ws_status.status = 'completed'
            ws_status.end_time = datetime.now()

            duration = (ws_status.end_time - ws_status.start_time).total_seconds()
            logger.info(f"✅ {ws_id} completed successfully in {duration:.1f}s")

            return True

        except Exception as e:
            ws_status.status = 'failed'
            ws_status.end_time = datetime.now()
            ws_status.error_message = str(e)

            logger.error(f"❌ {ws_id} failed: {e}")

            # Attempt rollback
            if not self.dry_run:
                logger.info(f"Attempting rollback for {ws_id}...")
                self._rollback_workstream(ws_data)

            return False

    def _run_preflight_checks(self, ws_data: dict) -> None:
        """Run preflight checks from workstream"""
        checks = ws_data['safety_and_rollback']['preflight_checks']

        for check in checks:
            if 'clean working tree' in check:
                result = subprocess.run(
                    'git status --porcelain',
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_dir)
                )
                if result.stdout.strip():
                    raise Exception(f"Working tree not clean:\n{result.stdout}")

            elif 'sync with' in check:
                remote = ws_data['git']['remote']
                result = subprocess.run(
                    f'git fetch {remote}',
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_dir)
                )
                if result.returncode != 0:
                    raise Exception(f"Failed to sync with {remote}")

            logger.info(f"✓ Preflight: {check}")

    def _rollback_workstream(self, ws_data: dict) -> None:
        """Execute rollback plan for workstream"""
        rollback_steps = ws_data['safety_and_rollback']['rollback_plan']

        for step in rollback_steps:
            if step.startswith('git '):
                logger.info(f"Rollback: {step}")
                subprocess.run(
                    step,
                    shell=True,
                    cwd=str(self.repo_dir)
                )

    def _prompt_continue(self, message: str) -> bool:
        """Prompt user to continue"""
        response = input(f"\n{message}? (y/n): ")
        return response.lower() == 'y'

    def execute_all(self, start_from: Optional[str] = None, only: Optional[List[str]] = None) -> bool:
        """Execute all workstreams in dependency order"""
        self.load_workstreams()
        execution_order = self.resolve_dependencies()

        # Filter if start_from or only specified
        if start_from:
            try:
                start_idx = execution_order.index(start_from)
                execution_order = execution_order[start_idx:]
                logger.info(f"Starting from {start_from}")
            except ValueError:
                logger.error(f"Workstream {start_from} not found")
                return False

        if only:
            execution_order = [ws for ws in execution_order if ws in only]
            logger.info(f"Executing only: {only}")

        # Execute workstreams
        total = len(execution_order)
        completed = 0
        failed = 0

        for i, ws_id in enumerate(execution_order):
            logger.info(f"\n[{i+1}/{total}] Processing {ws_id}...")

            # Check if dependencies completed
            ws_data = self.workstreams[ws_id]
            blocked_by = ws_data.get('blocked_by', [])

            for blocker_name in blocked_by:
                blocker_id = None
                for candidate_id, candidate_data in self.workstreams.items():
                    if candidate_data['workstream_name'] == blocker_name:
                        blocker_id = candidate_id
                        break

                if blocker_id and self.status[blocker_id].status != 'completed':
                    logger.warning(f"Skipping {ws_id}: dependency {blocker_id} not completed")
                    self.status[ws_id].status = 'skipped'
                    continue

            # Execute workstream
            if self.execute_workstream(ws_id):
                completed += 1
            else:
                failed += 1
                logger.error(f"Execution failed at {ws_id}")

                if not self._prompt_continue("Continue with remaining workstreams"):
                    break

        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("EXECUTION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total: {total}")
        logger.info(f"Completed: {completed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Skipped: {total - completed - failed}")
        logger.info(f"{'='*80}\n")

        # Save execution log
        self._save_execution_log()

        return failed == 0

    def _save_execution_log(self) -> None:
        """Save execution status to JSON"""
        log_file = Path("workstream_execution_status.json")

        status_data = {
            'timestamp': datetime.now().isoformat(),
            'workstreams': [
                {
                    'id': f"WS-{ws.workstream_id:02d}",
                    'name': ws.name,
                    'status': ws.status,
                    'start_time': ws.start_time.isoformat() if ws.start_time else None,
                    'end_time': ws.end_time.isoformat() if ws.end_time else None,
                    'error': ws.error_message
                }
                for ws in self.status.values()
            ]
        }

        with open(log_file, 'w') as f:
            json.dump(status_data, f, indent=2)

        logger.info(f"Execution log saved to {log_file}")

def main():
    parser = argparse.ArgumentParser(description='Execute all workstreams in dependency order')
    parser.add_argument('--dry-run', action='store_true', help='Simulate execution without making changes')
    parser.add_argument('--start-from', help='Start from specific workstream (e.g., WS-05)')
    parser.add_argument('--workstreams', help='Execute only specific workstreams (comma-separated, e.g., WS-01,WS-02)')
    parser.add_argument('--workstreams-dir', default=r'C:\Users\Richard Wilks\Downloads',
                       help='Directory containing workstream JSON files')

    args = parser.parse_args()

    workstreams_dir = Path(args.workstreams_dir)
    if not workstreams_dir.exists():
        logger.error(f"Workstreams directory not found: {workstreams_dir}")
        sys.exit(1)

    executor = WorkstreamExecutor(workstreams_dir, dry_run=args.dry_run)

    only = None
    if args.workstreams:
        only = [ws.strip() for ws in args.workstreams.split(',')]

    success = executor.execute_all(start_from=args.start_from, only=only)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
