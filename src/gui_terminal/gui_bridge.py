"""
GUI Bridge - Connects PyQt6 GUI to CLI Orchestrator backend.

This module provides Qt-friendly adapters for workflow execution,
cost tracking, and real-time updates via signals/slots.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

try:
    from PyQt6 import QtCore

    PyQt6Available = True
except ImportError:
    PyQt6Available = False
    QtCore = None  # type: ignore

# Import orchestrator backend components
try:
    from cli_multi_rapid.cost_tracker import CostTracker
    from cli_multi_rapid.router import Router
    from cli_multi_rapid.workflow_runner import WorkflowRunner

    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    WorkflowRunner = None  # type: ignore
    Router = None  # type: ignore
    CostTracker = None  # type: ignore


if PyQt6Available and BACKEND_AVAILABLE:

    class WorkflowExecutor(QtCore.QObject):
        """Qt-friendly workflow executor that runs workflows in background threads."""

        # Signals for workflow execution events
        workflow_started = QtCore.pyqtSignal(str)  # workflow_path
        step_started = QtCore.pyqtSignal(str, str)  # step_id, step_name
        step_completed = QtCore.pyqtSignal(str, bool, str)  # step_id, success, message
        workflow_completed = QtCore.pyqtSignal(bool, str)  # success, message
        output_received = QtCore.pyqtSignal(str)  # output_text
        progress_updated = QtCore.pyqtSignal(int, int)  # current_step, total_steps
        cost_updated = QtCore.pyqtSignal(int)  # tokens_used

        def __init__(self, parent: Optional[QtCore.QObject] = None):
            super().__init__(parent)
            self.runner = WorkflowRunner()
            self.current_workflow: Optional[str] = None
            self._running = False

        def execute_workflow(
            self,
            workflow_path: str,
            files: Optional[str] = None,
            dry_run: bool = False,
        ) -> None:
            """Execute a workflow asynchronously.

            Args:
                workflow_path: Path to workflow YAML file
                files: File pattern for workflow inputs
                dry_run: If True, validate without executing
            """
            if self._running:
                self.workflow_completed.emit(False, "Workflow already running")
                return

            self.current_workflow = workflow_path
            self._running = True

            # Create worker thread
            worker = WorkflowWorker(self.runner, workflow_path, files, dry_run)
            worker.step_started.connect(self.step_started)
            worker.step_completed.connect(self.step_completed)
            worker.workflow_completed.connect(self._on_workflow_completed)
            worker.output_received.connect(self.output_received)
            worker.progress_updated.connect(self.progress_updated)
            worker.cost_updated.connect(self.cost_updated)

            # Start execution
            self.workflow_started.emit(workflow_path)
            worker.start()

        def _on_workflow_completed(self, success: bool, message: str) -> None:
            """Handle workflow completion."""
            self._running = False
            self.workflow_completed.emit(success, message)

        def is_running(self) -> bool:
            """Check if a workflow is currently running."""
            return self._running

    class WorkflowWorker(QtCore.QThread):
        """Worker thread for executing workflows without blocking the GUI."""

        step_started = QtCore.pyqtSignal(str, str)
        step_completed = QtCore.pyqtSignal(str, bool, str)
        workflow_completed = QtCore.pyqtSignal(bool, str)
        output_received = QtCore.pyqtSignal(str)
        progress_updated = QtCore.pyqtSignal(int, int)
        cost_updated = QtCore.pyqtSignal(int)

        def __init__(
            self,
            runner: WorkflowRunner,
            workflow_path: str,
            files: Optional[str],
            dry_run: bool,
        ):
            super().__init__()
            self.runner = runner
            self.workflow_path = workflow_path
            self.files = files
            self.dry_run = dry_run

        def run(self) -> None:
            """Execute the workflow (runs in background thread)."""
            try:
                # Load workflow
                workflow_path_obj = Path(self.workflow_path)
                if not workflow_path_obj.exists():
                    self.workflow_completed.emit(
                        False, f"Workflow not found: {self.workflow_path}"
                    )
                    return

                # Execute workflow
                self.output_received.emit(f"Loading workflow: {self.workflow_path}")

                # Run the workflow (simplified execution for now)
                result = self.runner.run(
                    workflow_path=str(workflow_path_obj),
                    files=self.files,
                    dry_run=self.dry_run,
                )

                # Emit completion
                if result.success:
                    msg = f"Workflow completed successfully. Steps: {result.steps_completed}, Tokens: {result.tokens_used}"
                    self.cost_updated.emit(result.tokens_used)
                    self.workflow_completed.emit(True, msg)
                else:
                    self.workflow_completed.emit(False, result.error or "Unknown error")

            except Exception as e:
                self.workflow_completed.emit(False, f"Execution error: {str(e)}")

    class CostTrackerBridge(QtCore.QObject):
        """Qt-friendly bridge to the cost tracking system."""

        cost_updated = QtCore.pyqtSignal(int, int, int)  # total, budget, percentage

        def __init__(self, parent: Optional[QtCore.QObject] = None):
            super().__init__(parent)
            self.tracker = CostTracker()
            self._timer = QtCore.QTimer()
            self._timer.timeout.connect(self._update_cost)
            self._timer.start(5000)  # Update every 5 seconds

        def _update_cost(self) -> None:
            """Emit cost update signal."""
            try:
                total = self.tracker.get_total_tokens()
                budget = self.tracker.get_budget_limit()
                percentage = int((total / budget * 100) if budget > 0 else 0)
                self.cost_updated.emit(total, budget, percentage)
            except Exception:
                pass

        def get_total_tokens(self) -> int:
            """Get total tokens used."""
            return self.tracker.get_total_tokens()

        def get_budget_limit(self) -> int:
            """Get budget limit."""
            return self.tracker.get_budget_limit()

        def get_percentage_used(self) -> int:
            """Get percentage of budget used."""
            total = self.get_total_tokens()
            budget = self.get_budget_limit()
            return int((total / budget * 100) if budget > 0 else 0)

else:
    # Fallback classes when PyQt6 or backend not available

    class WorkflowExecutor:
        """Headless workflow executor fallback."""

        def __init__(self, parent=None):
            print("[GUI Bridge] Running in headless mode - PyQt6 or backend unavailable")

        def execute_workflow(self, workflow_path: str, files: Optional[str] = None, dry_run: bool = False) -> None:
            print(f"[GUI Bridge] Would execute: {workflow_path}")

        def is_running(self) -> bool:
            return False

    class CostTrackerBridge:
        """Headless cost tracker fallback."""

        def __init__(self, parent=None):
            pass

        def get_total_tokens(self) -> int:
            return 0

        def get_budget_limit(self) -> int:
            return 0

        def get_percentage_used(self) -> int:
            return 0


# Convenience functions for checking availability
def is_gui_available() -> bool:
    """Check if PyQt6 GUI is available."""
    return PyQt6Available


def is_backend_available() -> bool:
    """Check if orchestrator backend is available."""
    return BACKEND_AVAILABLE


def get_workflow_executor(parent: Optional[Any] = None) -> WorkflowExecutor:
    """Get a workflow executor instance.

    Args:
        parent: Optional Qt parent object

    Returns:
        WorkflowExecutor instance (either Qt or headless)
    """
    return WorkflowExecutor(parent)


def get_cost_tracker_bridge(parent: Optional[Any] = None) -> CostTrackerBridge:
    """Get a cost tracker bridge instance.

    Args:
        parent: Optional Qt parent object

    Returns:
        CostTrackerBridge instance (either Qt or headless)
    """
    return CostTrackerBridge(parent)
