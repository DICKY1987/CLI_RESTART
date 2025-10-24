#!/usr/bin/env python3
"""
CLI Orchestrator Workflow Runner - Backward-Compatible Facade

DEPRECATED: This module is maintained for backward compatibility.
New code should use core.coordinator.WorkflowCoordinator directly.

This facade delegates to the new core modules:
- core.executor.StepExecutor for step execution
- core.coordinator.WorkflowCoordinator for workflow orchestration
- core.gate_manager.GateManager for verification gates
- core.artifact_manager.ArtifactManager for artifact tracking

Migration Guide: docs/guides/WORKFLOW-RUNNER-MIGRATION.md
"""

import time
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

# Legacy coordination imports (maintained for backward compatibility)
from .coordination import (
    FileScopeManager,
)
from .coordination import WorkflowCoordinator as LegacyWorkflowCoordinator
from .core.artifact_manager import ArtifactManager
from .core.coordinator import WorkflowCoordinator as CoreWorkflowCoordinator
from .core.coordinator import WorkflowResult as CoreWorkflowResult

# New core modules
from .core.executor import StepExecutor
from .core.gate_manager import GateManager

console = Console()


# ============================================================================
# Backward-Compatible Data Classes
# ============================================================================

@dataclass
class WorkflowResult:
    """
    Result from workflow execution.

    DEPRECATED: Use core.coordinator.WorkflowResult instead.
    Maintained for backward compatibility.
    """

    success: bool
    error: Optional[str] = None
    artifacts: list[str] = None
    tokens_used: int = 0
    steps_completed: int = 0
    coordination_id: Optional[str] = None
    execution_time: Optional[float] = None
    parallel_groups: Optional[list[list[str]]] = None

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []
        if self.parallel_groups is None:
            self.parallel_groups = []


@dataclass
class CoordinatedWorkflowResult:
    """
    Result from coordinated multi-workflow execution.

    DEPRECATED: Will be refactored in Phase 2 Week 4.
    """

    success: bool
    coordination_id: str
    workflow_results: dict[str, WorkflowResult]
    total_tokens_used: int = 0
    total_execution_time: float = 0.0
    conflicts_detected: list[str] = None
    parallel_efficiency: float = 0.0

    def __post_init__(self):
        if self.conflicts_detected is None:
            self.conflicts_detected = []


# ============================================================================
# Workflow Runner - Backward-Compatible Facade
# ============================================================================

class WorkflowRunner:
    """
    DEPRECATED: Use core.coordinator.WorkflowCoordinator instead.

    This class is maintained for backward compatibility and will be
    removed in version 2.0 (estimated 6 months).

    Migration:
        # Old way
        runner = WorkflowRunner()
        result = runner.run(workflow_file)

        # New way
        from cli_multi_rapid.core.coordinator import WorkflowCoordinator
        from cli_multi_rapid.core.executor import StepExecutor
        from cli_multi_rapid.router import Router

        router = Router()
        executor = StepExecutor(router)
        coordinator = WorkflowCoordinator(executor)
        result = coordinator.execute_workflow(str(workflow_file))
    """

    def __init__(self):
        """Initialize workflow runner (deprecated)."""
        warnings.warn(
            "WorkflowRunner is deprecated. Use core.coordinator.WorkflowCoordinator instead. "
            "See migration guide in docs/guides/WORKFLOW-RUNNER-MIGRATION.md",
            DeprecationWarning,
            stacklevel=2
        )

        self.console = Console()

        # Initialize core modules
        try:
            from .cost_tracker import CostTracker
            from .router import Router

            self.router = Router()
            self.cost_tracker = CostTracker()
            self.executor = StepExecutor(self.router, self.cost_tracker)
            self.coordinator = CoreWorkflowCoordinator(self.executor)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to initialize core modules: {e}[/yellow]")
            self.router = None
            self.executor = None
            self.coordinator = None

        # Initialize managers
        self.gate_manager = GateManager()
        self.artifact_manager = ArtifactManager()

        # Legacy coordination (maintained for backward compatibility)
        self.legacy_coordinator = LegacyWorkflowCoordinator()
        self.scope_manager = FileScopeManager()
        self._state_base = Path("state/coordination")

        # Lazy-loaded components
        self.git_ops = None
        self.activity_logger = None

    # ========================================================================
    # Utility Methods
    # ========================================================================

    @staticmethod
    def generate_run_id() -> str:
        """Generate human-readable run ID."""
        import secrets
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_hex = secrets.token_hex(3)
        return f"{timestamp}-{random_hex}"

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

    # ========================================================================
    # Main Execution Methods (Facade Pattern)
    # ========================================================================

    def run(
        self,
        workflow_file: Path,
        dry_run: bool = False,
        files: Optional[str] = None,
        lane: Optional[str] = None,
        max_tokens: Optional[int] = None,
        coordination_mode: str = "sequential",
    ) -> WorkflowResult:
        """
        Run a workflow with the given parameters.

        DEPRECATED: Use WorkflowCoordinator.execute_workflow() instead.
        """
        try:
            # Set dry-run mode
            if self.executor:
                self.executor.dry_run = dry_run

            # Generate run ID
            run_id = self.generate_run_id()
            start_time = datetime.now()

            # Execute via core coordinator
            if self.coordinator:
                core_result: CoreWorkflowResult = self.coordinator.execute_workflow(
                    str(workflow_file),
                    files=files,
                    extra_context={"lane": lane, "max_tokens": max_tokens}
                )

                # Convert to legacy format
                result = self._convert_core_result_to_legacy(core_result)
                result.execution_time = (datetime.now() - start_time).total_seconds()

                # Register artifacts
                for artifact_path in result.artifacts:
                    self.artifact_manager.register_artifact(
                        artifact_path,
                        step_id="unknown"
                    )

                return result
            else:
                return WorkflowResult(
                    success=False,
                    error="Core modules not initialized"
                )

        except Exception as e:
            return WorkflowResult(
                success=False,
                error=f"Workflow execution error: {str(e)}"
            )

    def execute_workflow(
        self,
        workflow: dict[str, Any],
        files: Optional[str] = None,
        dry_run: bool = False
    ) -> dict[str, Any]:
        """
        Execute workflow and return a legacy dict structure for compatibility.

        DEPRECATED: Use WorkflowCoordinator.execute_workflow_from_dict() instead.
        """
        warnings.warn(
            "execute_workflow() is deprecated. Use WorkflowCoordinator.execute_workflow_from_dict()",
            DeprecationWarning,
            stacklevel=2
        )

        if self.executor:
            self.executor.dry_run = dry_run

        if self.coordinator:
            core_result = self.coordinator.execute_workflow_from_dict(
                workflow,
                files=files
            )

            return {
                "execution_id": f"exec-{int(time.time())}",
                "success": core_result.success,
                "steps": core_result.steps_executed,
                "tokens_used": core_result.total_tokens_used,
                "artifacts": core_result.artifacts,
                "error": core_result.error,
            }
        else:
            return {
                "execution_id": f"exec-{int(time.time())}",
                "success": False,
                "error": "Core modules not initialized",
                "steps": 0,
                "tokens_used": 0,
                "artifacts": []
            }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _convert_core_result_to_legacy(self, core_result: CoreWorkflowResult) -> WorkflowResult:
        """Convert core WorkflowResult to legacy WorkflowResult format."""
        return WorkflowResult(
            success=core_result.success,
            error=core_result.error,
            artifacts=core_result.artifacts,
            tokens_used=core_result.total_tokens_used,
            steps_completed=core_result.steps_executed,
            execution_time=core_result.total_execution_time_seconds
        )

    # ========================================================================
    # Legacy Complex Methods (Maintained for Backward Compatibility)
    # NOTE: These will be refactored in Phase 2 Week 4
    # ========================================================================

    def run_coordinated_workflows(
        self,
        workflow_files: list[Path],
        coordination_mode: str = "parallel",
        max_parallel: int = 3,
        total_budget: Optional[float] = None,
        dry_run: bool = False,
    ) -> CoordinatedWorkflowResult:
        """
        Run multiple workflows with coordination.

        NOTE: This method maintains legacy coordination logic.
        Will be refactored to use core modules in Phase 2 Week 4.
        """
        # Import on-demand to avoid circular dependencies
        from .workflow_runner_legacy import LegacyWorkflowRunner

        legacy_runner = LegacyWorkflowRunner()
        return legacy_runner.run_coordinated_workflows(
            workflow_files,
            coordination_mode,
            max_parallel,
            total_budget,
            dry_run
        )

    def execute_400_atom_pipeline(
        self,
        atom_catalog_path: str,
        classification_config: dict[str, Any],
        execution_mode: str = "production",
    ) -> CoordinatedWorkflowResult:
        """
        Execute the 400-atom pipeline.

        NOTE: This method maintains legacy pipeline logic.
        Will be refactored in Phase 3.
        """
        from .workflow_runner_legacy import LegacyWorkflowRunner

        legacy_runner = LegacyWorkflowRunner()
        return legacy_runner.execute_400_atom_pipeline(
            atom_catalog_path,
            classification_config,
            execution_mode
        )

    def run_ipt_wt_workflow(
        self,
        workflow_file: Path,
        request: Optional[str] = None,
        budget: Optional[int] = None,
    ) -> WorkflowResult:
        """
        Execute a lightweight IPT/WT-style workflow.

        NOTE: This method maintains legacy IPT/WT logic.
        Will be refactored in Phase 3.
        """
        from .workflow_runner_legacy import LegacyWorkflowRunner

        legacy_runner = LegacyWorkflowRunner()
        return legacy_runner.run_ipt_wt_workflow(
            workflow_file,
            request,
            budget
        )


# ============================================================================
# Convenience Functions (Deprecated)
# ============================================================================

def run_workflow(workflow_path: str, **kwargs) -> dict[str, Any]:
    """
    DEPRECATED: Use WorkflowCoordinator.execute_workflow() instead.

    Convenience function maintained for backward compatibility.
    """
    warnings.warn(
        "run_workflow() is deprecated. Use WorkflowCoordinator.execute_workflow() instead.",
        DeprecationWarning,
        stacklevel=2
    )

    runner = WorkflowRunner()
    result = runner.run(Path(workflow_path), **kwargs)

    return {
        "success": result.success,
        "error": result.error,
        "artifacts": result.artifacts,
        "tokens_used": result.tokens_used,
        "steps_completed": result.steps_completed,
    }
