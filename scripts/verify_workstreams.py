#!/usr/bin/env python3
"""
Workstream Implementation Verification Tool

This tool verifies if workstreams defined in JSON specifications have been fully
implemented in the repository. It checks:
- File existence and content
- Git branch status and merges
- Test execution and coverage
- Acceptance criteria validation
- Generates comprehensive reports

Usage:
    python scripts/verify_workstreams.py [--workstreams-dir PATH] [--output-format json|html|markdown|all]
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Tuple

try:
    from rich.console import Console
    from rich.progress import Progress
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' not installed. Install with: pip install rich")

# Cross-platform safe symbols
def _symbol(ok: bool) -> str:
    """Return safe symbol for cross-platform output"""
    import sys
    enc = (getattr(sys.stdout, "encoding", None) or "").lower()
    if "utf" in enc:
        return "✓" if ok else "✗"
    return "OK" if ok else "X"


class Status(Enum):
    """Verification status levels"""
    COMPLETED = "completed"
    PARTIAL = "partial"
    MISSING = "missing"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class FileVerification:
    """File verification result"""
    file_path: str
    exists: bool
    status: Status
    details: str = ""


@dataclass
class TaskVerification:
    """Task verification result"""
    task_id: str
    description: str
    status: Status
    files: List[FileVerification] = field(default_factory=list)
    tests_passed: bool = False
    acceptance_criteria_met: int = 0
    acceptance_criteria_total: int = 0
    details: str = ""


@dataclass
class WorkstreamVerification:
    """Workstream verification result"""
    workstream_id: int
    name: str
    branch_name: str
    branch_exists: bool
    branch_merged: bool
    status: Status
    tasks: List[TaskVerification] = field(default_factory=list)
    completion_percentage: float = 0.0
    files_implemented: int = 0
    files_total: int = 0
    tests_passed: int = 0
    tests_total: int = 0


class WorkstreamParser:
    """Parse workstream JSON specifications"""

    def __init__(self, workstreams_dir: Path):
        self.workstreams_dir = workstreams_dir
        self.workstreams: Dict[str, dict] = {}

    def load_workstreams(self) -> Dict[str, dict]:
        """Load all workstream JSON files"""
        json_files = sorted(self.workstreams_dir.glob("ws-*.json"))

        for json_file in json_files:
            try:
                with open(json_file, encoding='utf-8') as f:
                    ws_data = json.load(f)
                    ws_id = f"WS-{ws_data['workstream_id']:02d}"
                    self.workstreams[ws_id] = ws_data
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        return self.workstreams


class FileVerifier:
    """Verify file existence and implementation"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def verify_file(self, file_path: str, task_description: str = "") -> FileVerification:
        """Verify if a file exists and check basic implementation"""
        full_path = self.repo_root / file_path

        exists = full_path.exists()
        status = Status.COMPLETED if exists else Status.MISSING
        details = ""

        if exists:
            # Check if file has content (not just empty)
            try:
                content = full_path.read_text(encoding='utf-8')
                if len(content.strip()) < 10:
                    status = Status.PARTIAL
                    details = "File exists but appears empty or minimal"
                else:
                    # Check for key patterns based on task description
                    details = f"File exists ({len(content)} chars)"
            except Exception as e:
                status = Status.FAILED
                details = f"Error reading file: {e}"
        else:
            details = "File not found"

        return FileVerification(
            file_path=file_path,
            exists=exists,
            status=status,
            details=details
        )

    def verify_files(self, files: List[str], task_description: str = "") -> List[FileVerification]:
        """Verify multiple files"""
        return [self.verify_file(f, task_description) for f in files]


class GitVerifier:
    """Verify git branch status"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self._cached_branches = None
        self._cached_merged_branches = None

    def _run_git(self, args: List[str]) -> Tuple[bool, str]:
        """Run git command"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    def get_all_branches(self) -> Set[str]:
        """Get all branches (local and remote)"""
        if self._cached_branches is None:
            success, output = self._run_git(['branch', '-a'])
            if success:
                branches = set()
                for line in output.split('\n'):
                    branch = line.strip().lstrip('* ').replace('remotes/origin/', '')
                    if branch and not branch.startswith('HEAD'):
                        branches.add(branch)
                self._cached_branches = branches
            else:
                self._cached_branches = set()
        return self._cached_branches

    def get_merged_branches(self) -> Set[str]:
        """Get branches merged to main"""
        if self._cached_merged_branches is None:
            success, output = self._run_git(['branch', '--merged', 'main'])
            if success:
                branches = set()
                for line in output.split('\n'):
                    branch = line.strip().lstrip('* ')
                    if branch and branch != 'main':
                        branches.add(branch)
                self._cached_merged_branches = branches
            else:
                self._cached_merged_branches = set()
        return self._cached_merged_branches

    def verify_branch(self, branch_name: str) -> Tuple[bool, bool]:
        """Verify if branch exists and is merged

        Returns:
            (exists, is_merged)
        """
        all_branches = self.get_all_branches()
        merged_branches = self.get_merged_branches()

        exists = branch_name in all_branches
        is_merged = branch_name in merged_branches

        return exists, is_merged


class TestVerifier:
    """Verify test execution and coverage"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def verify_test_file(self, test_file: str) -> Tuple[bool, str]:
        """Verify if test file exists and can be run"""
        test_path = self.repo_root / test_file

        if not test_path.exists():
            return False, f"Test file not found: {test_file}"

        # Try to run the test
        try:
            result = subprocess.run(
                ['pytest', str(test_path), '-v', '--tb=short'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return True, "Tests passed"
            else:
                # Extract failure info
                failures = result.stdout.count('FAILED')
                return False, f"Tests failed ({failures} failures)"
        except subprocess.TimeoutExpired:
            return False, "Test execution timeout"
        except Exception as e:
            return False, f"Error running tests: {e}"

    def extract_test_files_from_plan(self, test_plan: List[str]) -> List[str]:
        """Extract test file paths from test plan steps"""
        test_files = []
        for step in test_plan:
            # Look for pytest commands with file paths
            if 'pytest' in step:
                # Extract file paths from pytest commands
                match = re.search(r'pytest\s+([^\s]+\.py)', step)
                if match:
                    test_files.append(match.group(1))
        return test_files


class AcceptanceCriteriaValidator:
    """Validate acceptance criteria"""

    def __init__(self, repo_root: Path, file_verifier: FileVerifier, git_verifier: GitVerifier):
        self.repo_root = repo_root
        self.file_verifier = file_verifier
        self.git_verifier = git_verifier

    def validate_criteria(self, criteria: List[str], context: dict) -> Tuple[int, int]:
        """Validate acceptance criteria

        Returns:
            (met_count, total_count)
        """
        met = 0
        total = len(criteria)

        for criterion in criteria:
            if self._check_criterion(criterion, context):
                met += 1

        return met, total

    def _check_criterion(self, criterion: str, context: dict) -> bool:
        """Check if a single criterion is met"""
        criterion_lower = criterion.lower()

        # File-based criteria
        if 'file' in criterion_lower or 'created' in criterion_lower or 'implemented' in criterion_lower:
            # Extract potential file paths
            for file_path in context.get('files', []):
                if self.file_verifier.verify_file(file_path).exists:
                    return True
            return False

        # Test-based criteria
        if 'test' in criterion_lower and ('pass' in criterion_lower or 'achieve' in criterion_lower):
            # If we have test results in context
            return context.get('tests_passed', False)

        # Coverage criteria
        if 'coverage' in criterion_lower:
            # Extract coverage percentage if available
            match = re.search(r'(\d+)%', criterion)
            if match:
                required = int(match.group(1))
                actual = context.get('coverage_percentage', 0)
                return actual >= required
            return False

        # Default: cannot verify automatically
        return False


class WorkstreamVerifier:
    """Main verification orchestrator"""

    def __init__(self, repo_root: Path, workstreams_dir: Path):
        self.repo_root = repo_root
        self.parser = WorkstreamParser(workstreams_dir)
        self.file_verifier = FileVerifier(repo_root)
        self.git_verifier = GitVerifier(repo_root)
        self.test_verifier = TestVerifier(repo_root)
        self.criteria_validator = AcceptanceCriteriaValidator(repo_root, self.file_verifier, self.git_verifier)
        self.console = Console() if RICH_AVAILABLE else None

    def verify_all(self) -> List[WorkstreamVerification]:
        """Verify all workstreams"""
        workstreams = self.parser.load_workstreams()
        results = []

        if self.console:
            with Progress() as progress:
                task = progress.add_task("[cyan]Verifying workstreams...", total=len(workstreams))

                for ws_id, ws_data in sorted(workstreams.items()):
                    result = self.verify_workstream(ws_id, ws_data)
                    results.append(result)
                    progress.update(task, advance=1)
        else:
            for ws_id, ws_data in sorted(workstreams.items()):
                print(f"Verifying {ws_id}...", file=sys.stderr)
                result = self.verify_workstream(ws_id, ws_data)
                results.append(result)

        return results

    def verify_workstream(self, ws_id: str, ws_data: dict) -> WorkstreamVerification:
        """Verify a single workstream"""
        branch_name = ws_data.get('branch_name', '')
        branch_exists, branch_merged = self.git_verifier.verify_branch(branch_name)

        # Verify tasks
        tasks = []
        total_files = 0
        implemented_files = 0
        total_tests = 0
        passed_tests = 0

        for task_data in ws_data.get('tasks', []):
            task_result = self.verify_task(task_data)
            tasks.append(task_result)

            total_files += len(task_result.files)
            implemented_files += sum(1 for f in task_result.files if f.exists)
            total_tests += 1 if task_result.tests_passed else 0
            passed_tests += 1 if task_result.tests_passed else 0

        # Calculate completion
        completion = 0.0
        if total_files > 0:
            completion = (implemented_files / total_files) * 100

        # Determine overall status
        if completion == 100 and branch_merged:
            status = Status.COMPLETED
        elif completion >= 50 or branch_exists:
            status = Status.PARTIAL
        elif completion > 0:
            status = Status.PARTIAL
        else:
            status = Status.MISSING

        return WorkstreamVerification(
            workstream_id=ws_data['workstream_id'],
            name=ws_data['workstream_name'],
            branch_name=branch_name,
            branch_exists=branch_exists,
            branch_merged=branch_merged,
            status=status,
            tasks=tasks,
            completion_percentage=completion,
            files_implemented=implemented_files,
            files_total=total_files,
            tests_passed=passed_tests,
            tests_total=len(tasks)
        )

    def verify_task(self, task_data: dict) -> TaskVerification:
        """Verify a single task"""
        task_id = task_data.get('id', 'unknown')
        description = task_data.get('description', '')
        files = task_data.get('files_to_create_or_modify', [])
        test_plan = task_data.get('test_plan', [])
        acceptance_criteria = task_data.get('acceptance_criteria', [])

        # Verify files
        file_results = self.file_verifier.verify_files(files, description)

        # Verify tests
        test_files = self.test_verifier.extract_test_files_from_plan(test_plan)
        tests_passed = False
        if test_files:
            for test_file in test_files:
                passed, details = self.test_verifier.verify_test_file(test_file)
                if passed:
                    tests_passed = True
                    break

        # Validate acceptance criteria
        context = {
            'files': files,
            'tests_passed': tests_passed
        }
        criteria_met, criteria_total = self.criteria_validator.validate_criteria(
            acceptance_criteria, context
        )

        # Determine task status
        all_files_exist = all(f.exists for f in file_results)
        if all_files_exist and tests_passed and criteria_met == criteria_total:
            status = Status.COMPLETED
        elif any(f.exists for f in file_results):
            status = Status.PARTIAL
        else:
            status = Status.MISSING

        return TaskVerification(
            task_id=task_id,
            description=description,
            status=status,
            files=file_results,
            tests_passed=tests_passed,
            acceptance_criteria_met=criteria_met,
            acceptance_criteria_total=criteria_total
        )


class ReportGenerator:
    """Generate verification reports in multiple formats"""

    def __init__(self, results: List[WorkstreamVerification]):
        self.results = results
        self.console = Console() if RICH_AVAILABLE else None

    def generate_json(self, output_path: Path) -> None:
        """Generate JSON report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(),
            'workstreams': [self._workstream_to_dict(ws) for ws in self.results]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        print(f"JSON report saved to: {output_path}")

    def generate_markdown(self, output_path: Path) -> None:
        """Generate Markdown report"""
        md_lines = [
            "# Workstream Implementation Verification Report",
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Summary\n"
        ]

        summary = self._generate_summary()
        md_lines.extend([
            f"- **Total Workstreams**: {summary['total_workstreams']}",
            f"- **Completed**: {summary['completed']} ({summary['completion_percentage']:.1f}%)",
            f"- **Partial**: {summary['partial']}",
            f"- **Missing**: {summary['missing']}",
            f"- **Overall File Implementation**: {summary['files_implemented']}/{summary['files_total']} ({summary['file_completion_percentage']:.1f}%)",
            "\n## Workstream Details\n"
        ])

        for ws in self.results:
            md_lines.extend(self._format_workstream_markdown(ws))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))

        print(f"Markdown report saved to: {output_path}")

    def generate_html(self, output_path: Path) -> None:
        """Generate HTML report"""
        summary = self._generate_summary()

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Workstream Verification Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary-stat {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .workstream {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .workstream.completed {{ border-left: 5px solid #4caf50; }}
        .workstream.partial {{ border-left: 5px solid #ff9800; }}
        .workstream.missing {{ border-left: 5px solid #f44336; }}
        .status {{ padding: 2px 8px; border-radius: 3px; font-size: 12px; }}
        .status.completed {{ background: #4caf50; color: white; }}
        .status.partial {{ background: #ff9800; color: white; }}
        .status.missing {{ background: #f44336; color: white; }}
        .progress-bar {{ background: #ddd; border-radius: 10px; height: 20px; margin: 10px 0; }}
        .progress-fill {{ background: #4caf50; height: 100%; border-radius: 10px; transition: width 0.3s; }}
        .task {{ background: #f9f9f9; margin: 10px 0; padding: 10px; border-radius: 3px; }}
        .file {{ font-family: monospace; font-size: 12px; padding: 2px 0; }}
        .file.exists {{ color: #4caf50; }}
        .file.missing {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Workstream Implementation Verification Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-stat"><strong>Total Workstreams:</strong> {summary['total_workstreams']}</div>
            <div class="summary-stat"><strong>Completed:</strong> {summary['completed']}</div>
            <div class="summary-stat"><strong>Partial:</strong> {summary['partial']}</div>
            <div class="summary-stat"><strong>Missing:</strong> {summary['missing']}</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {summary['completion_percentage']}%"></div>
            </div>
            <p><strong>Overall Completion:</strong> {summary['completion_percentage']:.1f}%</p>
            <p><strong>Files Implemented:</strong> {summary['files_implemented']}/{summary['files_total']} ({summary['file_completion_percentage']:.1f}%)</p>
        </div>

        <h2>Workstreams</h2>
"""

        for ws in self.results:
            html += self._format_workstream_html(ws)

        html += """
    </div>
</body>
</html>
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"HTML report saved to: {output_path}")

    def print_console(self) -> None:
        """Print report to console"""
        if not self.console:
            self._print_simple_console()
            return

        # Rich console output
        summary = self._generate_summary()

        # Summary table
        summary_table = Table(title="Workstream Verification Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")

        summary_table.add_row("Total Workstreams", str(summary['total_workstreams']))
        summary_table.add_row("Completed", f"{summary['completed']} ({summary['completion_percentage']:.1f}%)")
        summary_table.add_row("Partial", str(summary['partial']))
        summary_table.add_row("Missing", str(summary['missing']))
        summary_table.add_row("File Implementation", f"{summary['files_implemented']}/{summary['files_total']} ({summary['file_completion_percentage']:.1f}%)")

        self.console.print(summary_table)
        self.console.print()

        # Workstream details table
        ws_table = Table(title="Workstream Details")
        ws_table.add_column("ID", style="cyan")
        ws_table.add_column("Name", style="white")
        ws_table.add_column("Status", style="magenta")
        ws_table.add_column("Branch", style="yellow")
        ws_table.add_column("Files", style="green")
        ws_table.add_column("Completion", style="blue")

        for ws in self.results:
            status_color = {
                Status.COMPLETED: "green",
                Status.PARTIAL: "yellow",
                Status.MISSING: "red"
            }.get(ws.status, "white")

            # Use safe symbols
            branch_status = f"{_symbol(True)} Merged" if ws.branch_merged else (f"{_symbol(True)} Exists" if ws.branch_exists else f"{_symbol(False)} Missing")

            ws_table.add_row(
                f"WS-{ws.workstream_id:02d}",
                ws.name[:40],
                f"[{status_color}]{ws.status.value}[/{status_color}]",
                branch_status,
                f"{ws.files_implemented}/{ws.files_total}",
                f"{ws.completion_percentage:.0f}%"
            )

        self.console.print(ws_table)

    def _print_simple_console(self) -> None:
        """Print simple console output without rich"""
        summary = self._generate_summary()

        print("\n" + "=" * 80)
        print("WORKSTREAM VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Workstreams: {summary['total_workstreams']}")
        print(f"Completed: {summary['completed']} ({summary['completion_percentage']:.1f}%)")
        print(f"Partial: {summary['partial']}")
        print(f"Missing: {summary['missing']}")
        print(f"File Implementation: {summary['files_implemented']}/{summary['files_total']} ({summary['file_completion_percentage']:.1f}%)")
        print("=" * 80)
        print()

        for ws in self.results:
            status_symbol = {
                Status.COMPLETED: _symbol(True),
                Status.PARTIAL: "~",
                Status.MISSING: _symbol(False)
            }.get(ws.status, "?")

            print(f"{status_symbol} WS-{ws.workstream_id:02d}: {ws.name} [{ws.status.value}] - {ws.completion_percentage:.0f}%")
            print(f"   Branch: {ws.branch_name} - {'Merged' if ws.branch_merged else 'Exists' if ws.branch_exists else 'Missing'}")
            print(f"   Files: {ws.files_implemented}/{ws.files_total}")
            print()

    def _generate_summary(self) -> dict:
        """Generate summary statistics"""
        total = len(self.results)
        completed = sum(1 for ws in self.results if ws.status == Status.COMPLETED)
        partial = sum(1 for ws in self.results if ws.status == Status.PARTIAL)
        missing = sum(1 for ws in self.results if ws.status == Status.MISSING)

        total_files = sum(ws.files_total for ws in self.results)
        implemented_files = sum(ws.files_implemented for ws in self.results)

        return {
            'total_workstreams': total,
            'completed': completed,
            'partial': partial,
            'missing': missing,
            'completion_percentage': (completed / total * 100) if total > 0 else 0,
            'files_total': total_files,
            'files_implemented': implemented_files,
            'file_completion_percentage': (implemented_files / total_files * 100) if total_files > 0 else 0
        }

    def _workstream_to_dict(self, ws: WorkstreamVerification) -> dict:
        """Convert workstream to dict"""
        # Convert tasks to dict with Status enum values
        tasks_dict = []
        for task in ws.tasks:
            task_dict = asdict(task)
            # Convert Status enum to value
            if isinstance(task_dict.get('status'), Status):
                task_dict['status'] = task_dict['status'].value
            # Convert file statuses
            if 'files' in task_dict:
                for file_dict in task_dict['files']:
                    if isinstance(file_dict.get('status'), Status):
                        file_dict['status'] = file_dict['status'].value
            tasks_dict.append(task_dict)

        return {
            'workstream_id': ws.workstream_id,
            'name': ws.name,
            'branch_name': ws.branch_name,
            'branch_exists': ws.branch_exists,
            'branch_merged': ws.branch_merged,
            'status': ws.status.value,
            'completion_percentage': ws.completion_percentage,
            'files_implemented': ws.files_implemented,
            'files_total': ws.files_total,
            'tasks': tasks_dict
        }

    def _format_workstream_markdown(self, ws: WorkstreamVerification) -> List[str]:
        """Format workstream for markdown"""
        lines = [
            f"### WS-{ws.workstream_id:02d}: {ws.name}",
            f"- **Status**: {ws.status.value}",
            f"- **Branch**: {ws.branch_name} - {'Merged ✓' if ws.branch_merged else 'Exists ✓' if ws.branch_exists else 'Missing ✗'}",
            f"- **Completion**: {ws.completion_percentage:.1f}%",
            f"- **Files**: {ws.files_implemented}/{ws.files_total}",
            ""
        ]

        if ws.tasks:
            lines.append("**Tasks:**")
            for task in ws.tasks:
                lines.append(f"- [{task.status.value}] {task.description}")
            lines.append("")

        return lines

    def _format_workstream_html(self, ws: WorkstreamVerification) -> str:
        """Format workstream for HTML"""
        status_class = ws.status.value

        html = f"""
        <div class="workstream {status_class}">
            <h3>WS-{ws.workstream_id:02d}: {ws.name} <span class="status {status_class}">{ws.status.value}</span></h3>
            <p><strong>Branch:</strong> {ws.branch_name} - {'✓ Merged' if ws.branch_merged else '✓ Exists' if ws.branch_exists else '✗ Missing'}</p>
            <p><strong>Files:</strong> {ws.files_implemented}/{ws.files_total}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {ws.completion_percentage}%"></div>
            </div>
            <p><strong>Completion:</strong> {ws.completion_percentage:.1f}%</p>
"""

        if ws.tasks:
            html += "<h4>Tasks:</h4>"
            for task in ws.tasks:
                html += f"""
            <div class="task">
                <strong>[{task.status.value}]</strong> {task.description}
                <br><small>Files: {sum(1 for f in task.files if f.exists)}/{len(task.files)}</small>
"""
                if task.files:
                    html += "<div style='margin-top: 5px;'>"
                    for file in task.files:
                        file_class = 'exists' if file.exists else 'missing'
                        symbol = '✓' if file.exists else '✗'
                        html += f"<div class='file {file_class}'>{symbol} {file.file_path}</div>"
                    html += "</div>"
                html += "</div>"

        html += "</div>"
        return html


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Verify workstream implementation status')
    parser.add_argument(
        '--workstreams-dir',
        type=Path,
        default=Path(r'C:\Users\Richard Wilks\Downloads\WORKFLOW_VIS_FOLDER_1'),
        help='Directory containing workstream JSON files'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path(r'C:\Users\Richard Wilks'),
        help='Repository root directory'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(r'C:\Users\Richard Wilks\artifacts'),
        help='Output directory for reports'
    )
    parser.add_argument(
        '--output-format',
        choices=['json', 'markdown', 'html', 'all'],
        default='all',
        help='Report output format'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.workstreams_dir.exists():
        print(f"Error: Workstreams directory not found: {args.workstreams_dir}", file=sys.stderr)
        sys.exit(1)

    if not args.repo_root.exists():
        print(f"Error: Repository root not found: {args.repo_root}", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(exist_ok=True, parents=True)

    # Run verification
    print("Starting workstream verification...")
    verifier = WorkstreamVerifier(args.repo_root, args.workstreams_dir)
    results = verifier.verify_all()

    # Generate reports
    generator = ReportGenerator(results)

    # Console output
    generator.print_console()

    # File outputs
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if args.output_format in ['json', 'all']:
        generator.generate_json(args.output_dir / f'workstream_verification_{timestamp}.json')

    if args.output_format in ['markdown', 'all']:
        generator.generate_markdown(args.output_dir / f'workstream_verification_{timestamp}.md')

    if args.output_format in ['html', 'all']:
        generator.generate_html(args.output_dir / f'workstream_verification_{timestamp}.html')

    print("\nVerification complete!")


if __name__ == '__main__':
    main()
