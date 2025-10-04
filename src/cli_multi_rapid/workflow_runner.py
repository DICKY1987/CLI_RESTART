#!/usr/bin/env python3
"""
CLI Orchestrator Workflow Runner

Executes schema-validated YAML workflows with deterministic tool routing
and AI escalation patterns.
"""

import json
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import time
from datetime import datetime

import yaml
from rich.console import Console

from .coordination import (
    CoordinationMode,
    CoordinationPlan,
    WorkflowCoordinator,
    FileScopeManager
)

console = Console()


@dataclass
class WorkflowResult:
    """Result from workflow execution."""

    success: bool
    error: Optional[str] = None
    artifacts: List[str] = None
    tokens_used: int = 0
    steps_completed: int = 0
    coordination_id: Optional[str] = None
    execution_time: Optional[float] = None
    parallel_groups: Optional[List[List[str]]] = None

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []
        if self.parallel_groups is None:
            self.parallel_groups = []


@dataclass
class CoordinatedWorkflowResult:
    """Result from coordinated multi-workflow execution."""

    success: bool
    coordination_id: str
    workflow_results: Dict[str, WorkflowResult]
    total_tokens_used: int = 0
    total_execution_time: float = 0.0
    conflicts_detected: List[str] = None
    parallel_efficiency: float = 0.0

    def __post_init__(self):
        if self.conflicts_detected is None:
            self.conflicts_detected = []


class WorkflowRunner:
    """Executes workflows with schema validation and cost tracking."""

    def __init__(self):
        self.console = Console()
        self.coordinator = WorkflowCoordinator()
        self.scope_manager = FileScopeManager()
        self._state_base = Path("state/coordination")
        self.git_ops = None  # Lazy-loaded
        self.activity_logger = None  # Lazy-loaded
        try:
            from .router import Router

            self.router = Router()
        except Exception:
            self.router = None

    def _get_git_ops(self):
        """Lazy-load GitOpsAdapter."""
        if self.git_ops is None:
            try:
                from .adapters.git_ops import GitOpsAdapter
                self.git_ops = GitOpsAdapter()
            except Exception:
                pass
        return self.git_ops

    def _get_activity_logger(self):
        """Lazy-load ActivityLogger."""
        if self.activity_logger is None:
            try:
                from .logging import ActivityLogger
                log_path = Path("logs/workflow_execution.log")
                self.activity_logger = ActivityLogger(log_path)
            except Exception:
                pass
        return self.activity_logger

    @staticmethod
    def generate_run_id() -> str:
        """Generate human-readable run ID.

        Format: yyyyMMdd-HHmmss-6hex (e.g., 20250930-142455-a1b2c3)
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_hex = secrets.token_hex(3)  # 6 hex chars
        return f"{timestamp}-{random_hex}"

    def display_workflow_banner(self, workflow_name: str, run_id: str, config: Dict[str, Any]) -> None:
        """Display startup banner with workflow info."""
        cost_tracking = config.get("policy", {}).get("max_tokens") is not None
        gates_enabled = len(config.get("gates", [])) > 0

        banner = f"""
+--------------------------------------------------------------+
|                                                              |
|   CLI ORCHESTRATOR - WORKFLOW EXECUTION                      |
|                                                              |
|   Workflow:      {workflow_name:<46}|
|   Run ID:        {run_id:<46}|
|   Cost Tracking: {'ENABLED' if cost_tracking else 'DISABLED':<46}|
|   Verification:  {'ENABLED' if gates_enabled else 'DISABLED':<46}|
|                                                              |
+--------------------------------------------------------------+
"""
        self.console.print(banner)

        # Log to activity logger
        logger = self._get_activity_logger()
        if logger:
            logger.workflow_started(workflow_name, run_id, cost_tracking=cost_tracking, gates=gates_enabled)

    def display_workflow_summary(self, run_id: str, workflow_name: str, result: "WorkflowResult", start_time: datetime) -> None:
        """Display exit summary with statistics."""
        duration = datetime.now() - start_time

        # Get Git statistics if available
        git_stats = {}
        git_ops = self._get_git_ops()
        if git_ops:
            try:
                git_stats = git_ops.get_session_statistics(start_time)
            except Exception:
                pass

        summary = f"""
+--------------------------------------------------------------+
�   ?? WORKFLOW EXECUTION SUMMARY                             �
�                                                              �
�   Duration:          {str(duration).split('.')[0]:<42}�
�   Steps Executed:    {result.steps_completed:<42}�
�   Tokens Used:       {result.tokens_used:<42}�
�                                                              �
"""

        if git_stats:
            summary += f"""�   Git Changes:                                               �
�   - Commits Created: {git_stats.get('commits_since_start', 0):<42}�
�   - Unpushed:        {git_stats.get('unpushed', 0):<42}�
�   - Branch:          {git_stats.get('final_branch', 'unknown'):<42}�
�                                                              �
"""

        status = '? SUCCESS' if result.success else '? FAILED'
        summary += f"""�   Status: {status:<50}�
+--------------------------------------------------------------+
"""
        self.console.print(summary)

        # Log to activity logger
        logger = self._get_activity_logger()
        if logger:
            logger.workflow_completed(
                workflow_name,
                run_id,
                result.success,
                duration_seconds=duration.total_seconds(),
                steps_completed=result.steps_completed,
                tokens_used=result.tokens_used,
                git_stats=git_stats
            )

    def _save_workflow_manifest(
        self,
        run_id: str,
        workflow_name: str,
        result: "WorkflowResult",
        start_time: datetime,
        git_snapshot_start: Optional[Dict[str, Any]],
        git_snapshot_end: Optional[Dict[str, Any]]
    ) -> None:
        """Save workflow manifest with Git snapshots and statistics."""
        manifest_dir = Path("artifacts") / run_id
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "manifest.json"

        duration = datetime.now() - start_time

        manifest = {
            "run_id": run_id,
            "workflow_name": workflow_name,
            "created": start_time.isoformat(),
            "ended": datetime.now().isoformat(),
            "duration_seconds": duration.total_seconds(),
            "git_snapshot_start": git_snapshot_start,
            "git_snapshot_end": git_snapshot_end,
            "statistics": {
                "duration_seconds": duration.total_seconds(),
                "steps_executed": result.steps_completed,
                "tokens_used": result.tokens_used,
                "success": result.success,
                "artifacts_count": len(result.artifacts)
            },
            "artifacts": result.artifacts
        }

        # Add Git statistics if snapshots available
        if git_snapshot_start and git_snapshot_end:
            manifest["statistics"]["commits_created"] = (
                git_snapshot_end.get("recent_commits", 0) -
                git_snapshot_start.get("recent_commits", 0)
            )
            manifest["statistics"]["files_modified"] = len(
                set(git_snapshot_end.get("uncommitted_files", [])) -
                set(git_snapshot_start.get("uncommitted_files", []))
            )

        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            console.print(f"[dim]?? Manifest saved: {manifest_path}[/dim]")
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to save manifest: {e}[/yellow]")

    # --- Coordination state helpers ---
    def _state_dir(self) -> Path:
        self._state_base.mkdir(parents=True, exist_ok=True)
        return self._state_base

    def _state_file(self, coordination_id: str) -> Path:
        return self._state_dir() / f"{coordination_id}.json"

    def _cancel_file(self, coordination_id: str) -> Path:
        return self._state_dir() / f"{coordination_id}.cancel"

    def _persist_coordination_state(self, coordination_id: str, state: Dict[str, Any]) -> None:
        try:
            with self._state_file(coordination_id).open("w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception:
            # Non-fatal if persistence fails
            pass

    def _load_coordination_state(self, coordination_id: str) -> Optional[Dict[str, Any]]:
        path = self._state_file(coordination_id)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _is_cancelled(self, coordination_id: str) -> bool:
        return self._cancel_file(coordination_id).exists()

    # --- 400-atom pipeline integration (scaffolding) ---
    def execute_400_atom_pipeline(
        self,
        atom_catalog_path: str,
        classification_config: Dict[str, Any],
        execution_mode: str = "production",
    ) -> "CoordinatedWorkflowResult":
        """Execute the 400-atom pipeline with deterministic classification.

        Minimal scaffolding: classifies atoms, maps them into 6 phases, and
        computes a coordinated summary without invoking external tools.
        """
        # Local import to avoid heavy dependencies at import time
        from .deterministic_engine import AtomClassifier, PipelineOrchestrator

        classifier = AtomClassifier(classification_config)
        orchestrator = PipelineOrchestrator(self.coordinator, self.scope_manager)

        atoms = self._load_atom_catalog(atom_catalog_path)
        classification_result = classifier.classify_atoms(atoms)

        coordination_id = f"400atom-{int(time.time())}"
        result = orchestrator.execute_phases(
            classification_result,
            coordination_id=coordination_id,
            execution_mode=execution_mode,
        )

        return result

    def _load_atom_catalog(self, catalog_path: str) -> List[Dict[str, Any]]:
        """Load atom catalog from YAML; return list of atoms.

        Expected minimal structure: { atoms: [ { id, type, files?, deterministic? }, ... ] }
        Validates against .ai/schemas/atom_catalog.schema.json when available.
        """
        import yaml

        p = Path(catalog_path)
        if not p.exists():
            raise FileNotFoundError(f"Atom catalog not found: {catalog_path}")
        with p.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Optional schema validation
        schema_path = Path(".ai/schemas/atom_catalog.schema.json")
        if schema_path.exists():
            try:
                import json, jsonschema

                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                jsonschema.validate(instance=data, schema=schema)
            except ImportError:
                console.print(
                    "[yellow]Atom catalog schema validation skipped (jsonschema not installed)[/yellow]"
                )
            except Exception as e:
                raise ValueError(f"Atom catalog schema validation failed: {e}")

        atoms = data.get("atoms") or []
        # Normalize to list[dict]
        norm: List[Dict[str, Any]] = []
        for a in atoms:
            if isinstance(a, dict):
                norm.append(a)
        return norm

    def run(
        self,
        workflow_file: Path,
        dry_run: bool = False,
        files: Optional[str] = None,
        lane: Optional[str] = None,
        max_tokens: Optional[int] = None,
        coordination_mode: str = "sequential",
    ) -> WorkflowResult:
        """Run a workflow with the given parameters."""

        try:
            # Load and validate workflow
            workflow = self._load_workflow(workflow_file)
            if not workflow:
                return WorkflowResult(
                    success=False, error=f"Failed to load workflow: {workflow_file}"
                )

            # Validate schema
            if not self._validate_schema(workflow):
                return WorkflowResult(
                    success=False, error="Workflow schema validation failed"
                )

            # Check coordination mode and execute accordingly
            coordination_mode_enum = CoordinationMode(coordination_mode)

            if coordination_mode_enum == CoordinationMode.PARALLEL:
                return self._execute_parallel_workflow(
                    workflow, dry_run=dry_run, files=files, lane=lane, max_tokens=max_tokens
                )
            elif coordination_mode_enum == CoordinationMode.IPT_WT:
                return self._execute_ipt_wt_workflow(
                    workflow, dry_run=dry_run, files=files, lane=lane, max_tokens=max_tokens
                )
            else:
                # Sequential execution (default)
                return self._execute_workflow(
                    workflow, dry_run=dry_run, files=files, lane=lane, max_tokens=max_tokens
                )

        except Exception as e:
            return WorkflowResult(
                success=False, error=f"Workflow execution error: {str(e)}"
            )

    def _load_workflow(self, workflow_file: Path) -> Optional[Dict[str, Any]]:
        """Load YAML workflow file."""
        try:
            if not workflow_file.exists():
                console.print(f"[red]Workflow file not found: {workflow_file}[/red]")
                return None

            with open(workflow_file, "r", encoding="utf-8") as f:
                workflow = yaml.safe_load(f)

            console.print(
                f"[green]Loaded workflow: {workflow.get('name', 'Unnamed')}[/green]"
            )
            return workflow

        except Exception as e:
            console.print(f"[red]Error loading workflow: {e}[/red]")
            return None

    def _validate_schema(self, workflow: Dict[str, Any]) -> bool:
        """Validate workflow against JSON schema."""
        try:
            # Import jsonschema only when needed
            import jsonschema

            schema_path = Path(".ai/schemas/workflow.schema.json")
            if not schema_path.exists():
                console.print(
                    "[yellow]Schema validation skipped - schema file not found[/yellow]"
                )
                return True

            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)

            jsonschema.validate(workflow, schema)
            console.print("[green]OK Workflow schema validation passed[/green]")
            return True

        except ImportError:
            console.print(
                "[yellow]Schema validation skipped - jsonschema not available[/yellow]"
            )
            return True
        except Exception as e:
            console.print(f"[red]Schema validation failed: {e}[/red]")
            return False

    def _execute_workflow(
        self,
        workflow: Dict[str, Any],
        dry_run: bool = False,
        files: Optional[str] = None,
        lane: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> WorkflowResult:
        """Execute workflow steps with routing and cost tracking."""

        # Generate run ID and display banner
        run_id = self.generate_run_id()
        workflow_name = workflow.get("name", "Unnamed Workflow")
        start_time = datetime.now()

        self.display_workflow_banner(workflow_name, run_id, workflow)

        # Capture Git snapshot at start
        git_snapshot_start = None
        git_ops = self._get_git_ops()
        if git_ops:
            try:
                git_snapshot_start = git_ops.capture_git_snapshot()
                logger = self._get_activity_logger()
                if logger:
                    logger.git_snapshot(git_snapshot_start, event_type="pre-workflow")
                console.print(f"[dim]?? Git snapshot: {git_snapshot_start['branch']} @ {git_snapshot_start['commit_hash']}[/dim]")
            except Exception:
                pass

        steps = workflow.get("steps", [])
        if not steps:
            result = WorkflowResult(success=True, steps_completed=0)
            self.display_workflow_summary(run_id, workflow_name, result, start_time)
            return result

        console.print(f"[blue]Executing {len(steps)} workflow steps[/blue]")

        total_tokens = 0
        artifacts = []
        completed_steps = 0

        # Optional per-phase timeout configuration
        timeouts = (workflow.get("timeouts") or {})
        per_phase_seconds = timeouts.get("per_phase_seconds")

        for i, step in enumerate(steps):
            step_id = step.get("id", f"step-{i+1}")
            step_name = step.get("name", f"Step {i+1}")
            actor = step.get("actor", "unknown")

            console.print(f"[cyan]Step {step_id}: {step_name}[/cyan]")
            console.print(f"[dim]Actor: {actor}[/dim]")

            if dry_run:
                console.print("[yellow]DRY RUN - step skipped[/yellow]")
                completed_steps += 1
                continue

            # Execute step (adapter-backed)
            
            if per_phase_seconds:
                # Soft timeout: if exceeded, mark failure gracefully
                try:
                    step_result = self._execute_step(step, files=files, timeout_seconds=per_phase_seconds)
                except TimeoutError as te:
                    return WorkflowResult(
                        success=False,
                        error=f"Step {step_id} timed out: {te}",
                        tokens_used=total_tokens,
                        steps_completed=completed_steps,
                    )
            else:
                step_result = self._execute_step(step, files=files)

            total_tokens += step_result.get("tokens_used", 0)
            artifacts.extend(step_result.get("artifacts", []))

            if not step_result.get("success", False):
                error = step_result.get("error", "Step execution failed")
                return WorkflowResult(
                    success=False,
                    error=f"Step {step_id} failed: {error}",
                    tokens_used=total_tokens,
                    steps_completed=completed_steps,
                )

            completed_steps += 1

            # Check token limit
            if max_tokens and total_tokens > max_tokens:
                return WorkflowResult(
                    success=False,
                    error=f"Token limit exceeded: {total_tokens} > {max_tokens}",
                    tokens_used=total_tokens,
                    steps_completed=completed_steps,
                )

        console.print(f"[green]OK Workflow completed: {completed_steps} steps[/green]")

        # Capture Git snapshot at end
        git_snapshot_end = None
        if git_ops:
            try:
                git_snapshot_end = git_ops.capture_git_snapshot()
                logger = self._get_activity_logger()
                if logger:
                    logger.git_snapshot(git_snapshot_end, event_type="post-workflow")
                console.print(f"[dim]?? Git snapshot: {git_snapshot_end['branch']} @ {git_snapshot_end['commit_hash']}[/dim]")
            except Exception:
                pass

        # Create result
        result = WorkflowResult(
            success=True,
            artifacts=artifacts,
            tokens_used=total_tokens,
            steps_completed=completed_steps,
        )

        # Display summary
        self.display_workflow_summary(run_id, workflow_name, result, start_time)

        # Save manifest with Git snapshots
        self._save_workflow_manifest(run_id, workflow_name, result, start_time, git_snapshot_start, git_snapshot_end)

        return result

    def _execute_step(
        self, step: Dict[str, Any], files: Optional[str] = None, timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a single workflow step via adapter registry routing."""
        actor = step.get("actor", "unknown")
        console.print(f"[dim]Executing actor: {actor}[/dim]")


        # Idempotency: skip if already executed with same context
        try:
            from src.idempotency.storage import get_store, make_step_key

            store = get_store()
            key = make_step_key(step, files)
            if store.seen(key):
                return {
                    "success": True,
                    "tokens_used": 0,
                    "artifacts": [],
                    "output": f"Skipped (idempotent) {actor}",
                    "metadata": {"skipped": True, "reason": "idempotent"},
                }
        except Exception:
            # Proceed without idempotency if store not available
            store = None
            key = None

        # Resolve adapter
        adapter = None
        if self.router is not None:
            try:
                adapter = self.router.registry.get_adapter(actor)
            except Exception:
                adapter = None
        if adapter is None:
            # Fallback to direct registry import
            try:
                from .adapters.adapter_registry import registry as global_registry

                adapter = global_registry.get_adapter(actor)
            except Exception:
                adapter = None

        if adapter is None:
            return {
                "success": False,
                "error": f"Adapter not found: {actor}",
                "artifacts": [],
                "tokens_used": 0,
            }

        # Validate step
        if hasattr(adapter, "validate_step") and not adapter.validate_step(step):
            return {"success": False, "error": f"Invalid step for adapter {actor}", "artifacts": [], "tokens_used": 0}

        # Cancellation token via file
        cancel_token = None
        try:
            from .cancellation import CancellationToken

            cancel_token = CancellationToken()
        except Exception:
            cancel_token = None

        # Execute with soft timeout
        start = time.time()
        try:
            context = {"cancel_token": cancel_token}
            result_obj = adapter.execute(step, context=context, files=files)
        except Exception as e:
            return {"success": False, "error": str(e), "artifacts": [], "tokens_used": 0}

        elapsed = time.time() - start
        if timeout_seconds and elapsed > timeout_seconds:
            return {"success": False, "error": f"timeout exceeded after {elapsed:.2f}s", "artifacts": [], "tokens_used": 0}

        # Mark idempotency key after success
        try:
            if store and key and getattr(result_obj, "success", False):
                store.mark(key)
        except Exception:
            pass

        # Normalize result
        if hasattr(result_obj, "to_dict"):
            return result_obj.to_dict()
        if isinstance(result_obj, dict):
            return result_obj
        return {"success": True, "tokens_used": 0, "artifacts": [], "output": str(result_obj)}

    # Compatibility wrapper used by some integration tests
    def execute_workflow(self, workflow: Dict[str, Any], files: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Execute workflow and return a legacy dict structure for compatibility."""
        result = self._execute_workflow(workflow, dry_run=dry_run, files=files)
        return {
            "execution_id": f"exec-{int(time.time())}",
            "success": result.success,
            "steps": result.steps_completed,
            "tokens_used": result.tokens_used,
            "artifacts": result.artifacts,
            "error": result.error,
        }

    # --- IPT/WT integration (minimal scaffolding) ---
    def run_ipt_wt_workflow(
        self,
        workflow_file: Path,
        request: Optional[str] = None,
        budget: Optional[int] = None,
    ) -> WorkflowResult:
        """Execute a lightweight IPT/WT-style workflow.

        This scaffolding loads the workflow, checks structure, and performs
        a budget-aware routing decision for a representative step without
        executing external tools.
        """
        try:
            workflow = self._load_workflow(workflow_file)
            if not workflow:
                return WorkflowResult(success=False, error="workflow not found")

            roles = (workflow.get("roles") or {})
            phases = (workflow.get("phases") or [])
            if not roles or not phases:
                return WorkflowResult(success=False, error="invalid IPT/WT workflow structure")

            # Make a simple routing decision to validate configuration
            from .router import Router

            router = Router()
            sample_step = {"actor": "ai_analyst", "with": {"analysis_type": "code_review", "detail_level": "low"}}
            decision = router.route_with_budget_awareness(sample_step, role="ipt", budget_remaining=budget or 0)

            artifact_path = Path("artifacts/ipt-wt/decision.json")
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            with artifact_path.open("w", encoding="utf-8") as f:
                json.dump({
                    "router_decision": {
                        "adapter_name": decision.adapter_name,
                        "adapter_type": decision.adapter_type,
                        "estimated_tokens": decision.estimated_tokens,
                        "reasoning": decision.reasoning,
                    },
                    "request": request,
                }, f, indent=2)

            return WorkflowResult(success=True, artifacts=[str(artifact_path)], steps_completed=len(phases))
        except Exception as e:
            return WorkflowResult(success=False, error=f"ipt/wt workflow error: {e}")

    def run_coordinated_workflows(
        self,
        workflow_files: List[Path],
        coordination_mode: str = "parallel",
        max_parallel: int = 3,
        total_budget: Optional[float] = None,
        dry_run: bool = False,
    ) -> CoordinatedWorkflowResult:
        """Run multiple workflows with coordination."""

        start_time = time.time()
        coordination_id = f"coord-{self.generate_run_id()}"

        try:
            # Load all workflows
            workflows = []
            for workflow_file in workflow_files:
                workflow = self._load_workflow(workflow_file)
                if workflow:
                    workflow['_file_path'] = str(workflow_file)
                    workflows.append(workflow)

            if not workflows:
                return CoordinatedWorkflowResult(
                    success=False,
                    coordination_id=coordination_id,
                    workflow_results={},
                    conflicts_detected=["No valid workflows loaded"]
                )

            # Create coordination plan
            coordination_plan = self.coordinator.create_coordination_plan(workflows)

            if coordination_plan.conflicts:
                conflict_descriptions = [
                    f"Conflict between {', '.join(c.workflow_ids)} on {', '.join(c.conflicting_patterns)}"
                    for c in coordination_plan.conflicts
                ]
                return CoordinatedWorkflowResult(
                    success=False,
                    coordination_id=coordination_id,
                    workflow_results={},
                    conflicts_detected=conflict_descriptions
                )

            # Initialize and persist coordination state
            state: Dict[str, Any] = {
                "coordination_id": coordination_id,
                "status": "running" if not dry_run else "dry_run",
                "started_at": datetime.now().isoformat(),
                "mode": coordination_mode,
                "max_parallel": max_parallel,
                "budget": total_budget,
                "input_files": [str(p) for p in workflow_files],
                "workflow_results": {},
                "conflicts_detected": [],
            }
            self._persist_coordination_state(coordination_id, state)

            if self._is_cancelled(coordination_id):
                return CoordinatedWorkflowResult(
                    success=False,
                    coordination_id=coordination_id,
                    workflow_results={},
                    conflicts_detected=["Coordination cancelled before start"],
                )

            # Execute workflows based on coordination mode
            if coordination_mode == "parallel" and coordination_plan.parallel_groups:
                workflow_results = self._execute_parallel_groups(
                    workflows, coordination_plan, max_parallel, dry_run, coordination_id
                )
            else:
                # Sequential execution
                workflow_results = self._execute_sequential_workflows(
                    workflows, coordination_plan, dry_run, coordination_id
                )

            # Calculate summary metrics
            total_tokens = sum(result.tokens_used for result in workflow_results.values())
            execution_time = time.time() - start_time
            success = all(result.success for result in workflow_results.values())

            final = CoordinatedWorkflowResult(
                success=success,
                coordination_id=coordination_id,
                workflow_results=workflow_results,
                total_tokens_used=total_tokens,
                total_execution_time=execution_time,
                parallel_efficiency=self._calculate_parallel_efficiency(workflow_results, execution_time)
            )
            # Persist final state
            state.update(
                {
                    "status": "completed" if success else "failed",
                    "total_tokens_used": final.total_tokens_used,
                    "total_execution_time": final.total_execution_time,
                    "parallel_efficiency": final.parallel_efficiency,
                    "workflow_results": {
                        k: {
                            "success": v.success,
                            "tokens_used": v.tokens_used,
                            "steps_completed": v.steps_completed,
                            "execution_time": v.execution_time,
                            "error": v.error,
                            "artifacts": v.artifacts,
                        }
                        for k, v in workflow_results.items()
                    },
                }
            )
            self._persist_coordination_state(coordination_id, state)
            return final

        except Exception as e:
            return CoordinatedWorkflowResult(
                success=False,
                coordination_id=coordination_id,
                workflow_results={},
                conflicts_detected=[f"Coordination error: {str(e)}"]
            )

    def _execute_parallel_workflow(
        self,
        workflow: Dict[str, Any],
        dry_run: bool = False,
        files: Optional[str] = None,
        lane: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> WorkflowResult:
        """Execute workflow with parallel phase support."""

        start_time = time.time()

        # Check for parallel phases
        phases = workflow.get('phases', [])
        parallel_phases = [phase for phase in phases if phase.get('parallel', False)]

        if parallel_phases:
            # Execute with parallel coordination
            coordination_plan = self.coordinator.create_coordination_plan([workflow])

            if coordination_plan.conflicts:
                return WorkflowResult(
                    success=False,
                    error=f"File scope conflicts detected: {coordination_plan.conflicts}",
                    execution_time=time.time() - start_time
                )

            # Execute parallel phases
            results = self._execute_parallel_phases(phases, dry_run, files, max_tokens)

            total_tokens = sum(r.get("tokens_used", 0) for r in results)
            total_artifacts = []
            for r in results:
                total_artifacts.extend(r.get("artifacts", []))

            success = all(r.get("success", False) for r in results)

            return WorkflowResult(
                success=success,
                tokens_used=total_tokens,
                artifacts=total_artifacts,
                steps_completed=len(results),
                execution_time=time.time() - start_time,
                parallel_groups=[str(i) for i in range(len(parallel_phases))]
            )
        else:
            # Fall back to sequential execution
            return self._execute_workflow(
                workflow, dry_run=dry_run, files=files, lane=lane, max_tokens=max_tokens
            )

    def _execute_ipt_wt_workflow(
        self,
        workflow: Dict[str, Any],
        dry_run: bool = False,
        files: Optional[str] = None,
        lane: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> WorkflowResult:
        """Execute IPT-WT pattern workflow with enhanced coordination."""

        start_time = time.time()

        # Check for IPT-WT structure
        roles = workflow.get("roles", {})
        phases = workflow.get("phases", [])

        if not roles or not phases:
            return WorkflowResult(
                success=False,
                error="Invalid IPT-WT workflow structure",
                execution_time=time.time() - start_time
            )

        # Execute phases with role-based coordination
        ipt_phases = [p for p in phases if p.get('role') == 'ipt']
        wt_phases = [p for p in phases if p.get('role') == 'wt']

        results = []

        # Execute IPT phases first (planning)
        for phase in ipt_phases:
            phase_result = self._execute_phase(phase, dry_run, files)
            results.append(phase_result)

        # Execute WT phases (potentially in parallel)
        wt_parallel = any(p.get('parallel', False) for p in wt_phases)
        if wt_parallel and not dry_run:
            wt_results = self._execute_parallel_phases(wt_phases, dry_run, files, max_tokens)
            results.extend(wt_results)
        else:
            for phase in wt_phases:
                phase_result = self._execute_phase(phase, dry_run, files)
                results.append(phase_result)

        total_tokens = sum(r.get("tokens_used", 0) for r in results)
        total_artifacts = []
        for r in results:
            total_artifacts.extend(r.get("artifacts", []))

        success = all(r.get("success", False) for r in results)

        return WorkflowResult(
            success=success,
            tokens_used=total_tokens,
            artifacts=total_artifacts,
            steps_completed=len(results),
            execution_time=time.time() - start_time
        )

    def _execute_parallel_groups(
        self,
        workflows: List[Dict[str, Any]],
        coordination_plan: CoordinationPlan,
        max_parallel: int,
        dry_run: bool,
        coordination_id: Optional[str] = None,
    ) -> Dict[str, WorkflowResult]:
        """Execute workflows in parallel groups."""

        workflow_results = {}

        for group in coordination_plan.parallel_groups:
            if coordination_id and self._is_cancelled(coordination_id):
                break
            if len(group) == 1:
                # Single workflow, execute normally
                workflow_name = group[0]
                workflow = next((w for w in workflows if w.get('name') == workflow_name), None)
                if workflow:
                    result = self._execute_workflow(workflow, dry_run=dry_run)
                    workflow_results[workflow_name] = result
                    if coordination_id:
                        self._update_partial_state(coordination_id, workflow_name, result)
            else:
                # Multiple workflows, execute in parallel
                with ThreadPoolExecutor(max_workers=min(max_parallel, len(group))) as executor:
                    future_to_workflow = {}

                    for workflow_name in group:
                        workflow = next((w for w in workflows if w.get('name') == workflow_name), None)
                        if workflow:
                            future = executor.submit(self._execute_workflow, workflow, dry_run)
                            future_to_workflow[future] = workflow_name

                    for future in as_completed(future_to_workflow):
                        workflow_name = future_to_workflow[future]
                        try:
                            result = future.result()
                            workflow_results[workflow_name] = result
                            if coordination_id:
                                self._update_partial_state(coordination_id, workflow_name, result)
                        except Exception as e:
                            workflow_results[workflow_name] = WorkflowResult(
                                success=False,
                                error=f"Parallel execution error: {str(e)}"
                            )
                            if coordination_id:
                                self._update_partial_state(coordination_id, workflow_name, workflow_results[workflow_name])

        return workflow_results

    def _execute_sequential_workflows(
        self,
        workflows: List[Dict[str, Any]],
        coordination_plan: CoordinationPlan,
        dry_run: bool,
        coordination_id: Optional[str] = None,
    ) -> Dict[str, WorkflowResult]:
        """Execute workflows sequentially."""

        workflow_results = {}

        for workflow_name in coordination_plan.execution_order:
            if coordination_id and self._is_cancelled(coordination_id):
                self.console.print("[yellow]Coordination cancelled — stopping sequential execution[/yellow]")
                break
            workflow = next((w for w in workflows if w.get('name') == workflow_name), None)
            if workflow:
                result = self._execute_workflow(workflow, dry_run=dry_run)
                workflow_results[workflow_name] = result
                if coordination_id:
                    self._update_partial_state(coordination_id, workflow_name, result)

                # Stop on failure if configured
                if not result.success:
                    self.console.print(f"[red]Workflow {workflow_name} failed, stopping execution[/red]")
                    break

        return workflow_results

    def _update_partial_state(self, coordination_id: str, workflow_name: str, result: WorkflowResult) -> None:
        state = self._load_coordination_state(coordination_id) or {}
        wf = state.get("workflow_results", {})
        wf[workflow_name] = {
            "success": result.success,
            "tokens_used": result.tokens_used,
            "steps_completed": result.steps_completed,
            "execution_time": result.execution_time,
            "error": result.error,
            "artifacts": result.artifacts,
        }
        state["workflow_results"] = wf
        self._persist_coordination_state(coordination_id, state)

    def resume_coordination(self, coordination_id: str) -> CoordinatedWorkflowResult:
        """Resume a coordination session from persisted state (best-effort)."""
        state = self._load_coordination_state(coordination_id)
        if not state:
            return CoordinatedWorkflowResult(
                success=False,
                coordination_id=coordination_id,
                workflow_results={},
                conflicts_detected=["No persisted state found"],
            )

        try:
            input_files = [Path(p) for p in state.get("input_files", [])]
            completed = set((state.get("workflow_results") or {}).keys())
            # Reload workflows
            workflows = []
            for wf in input_files:
                data = self._load_workflow(wf)
                if data:
                    workflows.append(data)

            if not workflows:
                return CoordinatedWorkflowResult(
                    success=False,
                    coordination_id=coordination_id,
                    workflow_results={},
                    conflicts_detected=["No valid workflows to resume"],
                )

            plan = self.coordinator.create_coordination_plan(workflows)
            # Filter execution order to remaining workflows
            remaining_order = [w for w in plan.execution_order if w not in completed]
            plan.execution_order = remaining_order

            # Execute remaining sequentially for simplicity
            results = self._execute_sequential_workflows(workflows, plan, dry_run=False, coordination_id=coordination_id)
            # Merge with previous results
            merged: Dict[str, WorkflowResult] = {}
            for name, prev in (state.get("workflow_results") or {}).items():
                merged[name] = WorkflowResult(
                    success=bool(prev.get("success")),
                    tokens_used=int(prev.get("tokens_used", 0)),
                    steps_completed=int(prev.get("steps_completed", 0)),
                    execution_time=float(prev.get("execution_time")) if prev.get("execution_time") is not None else 0.0,
                    error=prev.get("error"),
                    artifacts=prev.get("artifacts") or [],
                )
            merged.update(results)

            total_tokens = sum(r.tokens_used for r in merged.values())
            execution_time = sum((r.execution_time or 0.0) for r in merged.values())
            success = all(r.success for r in merged.values())

            final = CoordinatedWorkflowResult(
                success=success,
                coordination_id=coordination_id,
                workflow_results=merged,
                total_tokens_used=total_tokens,
                total_execution_time=execution_time,
                parallel_efficiency=0.0,
            )
            # Persist final
            self._persist_coordination_state(
                coordination_id,
                {
                    **(state or {}),
                    "status": "completed" if success else "failed",
                    "workflow_results": {
                        k: {
                            "success": v.success,
                            "tokens_used": v.tokens_used,
                            "steps_completed": v.steps_completed,
                            "execution_time": v.execution_time,
                            "error": v.error,
                            "artifacts": v.artifacts,
                        }
                        for k, v in merged.items()
                    },
                },
            )
            return final
        except Exception as e:
            return CoordinatedWorkflowResult(
                success=False,
                coordination_id=coordination_id,
                workflow_results={},
                conflicts_detected=[f"Resume error: {e}"],
            )

    def _execute_parallel_phases(
        self,
        phases: List[Dict[str, Any]],
        dry_run: bool,
        files: Optional[str],
        max_tokens: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Execute phases in parallel."""

        if dry_run:
            # Simulate parallel execution for dry run
            results = []
            for phase in phases:
                results.append({
                    "success": True,
                    "tokens_used": 0,
                    "artifacts": [],
                    "output": f"DRY RUN: Phase {phase.get('id', 'unknown')}"
                })
            return results

        # Execute phases in parallel
        with ThreadPoolExecutor(max_workers=min(3, len(phases))) as executor:
            future_to_phase = {
                executor.submit(self._execute_phase, phase, dry_run, files): phase
                for phase in phases
            }

            results = []
            for future in as_completed(future_to_phase):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": f"Phase execution error: {str(e)}",
                        "tokens_used": 0,
                        "artifacts": []
                    })

        return results

    def _execute_phase(
        self,
        phase: Dict[str, Any],
        dry_run: bool,
        files: Optional[str]
    ) -> Dict[str, Any]:
        """Execute a single workflow phase."""

        phase_id = phase.get('id', 'unknown')
        tasks = phase.get('tasks', [])

        if dry_run:
            return {
                "success": True,
                "tokens_used": 0,
                "artifacts": [],
                "output": f"DRY RUN: Phase {phase_id} with {len(tasks)} tasks"
            }

        # Execute tasks in the phase
        total_tokens = 0
        artifacts = []

        for task in tasks:
            # Convert task to step format for execution
            if isinstance(task, str):
                step = {"id": task, "actor": "unknown", "name": task}
            else:
                step = task

            step_result = self._execute_step(step, files=files)
            total_tokens += step_result.get("tokens_used", 0)
            artifacts.extend(step_result.get("artifacts", []))

            if not step_result.get("success", False):
                return {
                    "success": False,
                    "error": f"Task {task} failed",
                    "tokens_used": total_tokens,
                    "artifacts": artifacts
                }

        return {
            "success": True,
            "tokens_used": total_tokens,
            "artifacts": artifacts,
            "output": f"Phase {phase_id} completed successfully"
        }

    def _calculate_parallel_efficiency(
        self,
        workflow_results: Dict[str, WorkflowResult],
        total_time: float
    ) -> float:
        """Calculate parallelization efficiency."""

        if not workflow_results or total_time <= 0:
            return 0.0

        # Sum individual execution times
        individual_times = sum(
            result.execution_time or 0.0 for result in workflow_results.values()
        )

        if individual_times <= 0:
            return 0.0

        # Efficiency = (sum of individual times) / (total parallel time * number of workflows)
        # Values closer to 1.0 indicate better parallel efficiency
        expected_parallel_time = individual_times / len(workflow_results)
        efficiency = expected_parallel_time / total_time if total_time > 0 else 0.0

        return min(efficiency, 1.0)  # Cap at 100% efficiency
