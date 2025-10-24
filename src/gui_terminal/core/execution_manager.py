"""
Execution Manager - Manages workflow execution state and coordination.

Provides high-level interface for GUI to execute and monitor workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

try:
    from PyQt6 import QtCore

    PyQt6Available = True
except ImportError:
    PyQt6Available = False
    QtCore = None  # type: ignore


class ExecutionState(Enum):
    """Workflow execution states."""

    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance."""

    id: str
    workflow_path: str
    state: ExecutionState
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_step: int = 0
    total_steps: int = 0
    tokens_used: int = 0
    artifacts: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    dry_run: bool = False

    @property
    def duration(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return None

    @property
    def progress_percentage(self) -> int:
        """Get execution progress as percentage."""
        if self.total_steps > 0:
            return int((self.current_step / self.total_steps) * 100)
        return 0


if PyQt6Available:

    class ExecutionManager(QtCore.QObject):
        """Manages workflow executions with state tracking and monitoring."""

        # Signals
        execution_queued = QtCore.pyqtSignal(str)  # execution_id
        execution_started = QtCore.pyqtSignal(str)  # execution_id
        execution_progress = QtCore.pyqtSignal(str, int, int)  # id, current, total
        execution_completed = QtCore.pyqtSignal(str, bool)  # execution_id, success
        execution_cancelled = QtCore.pyqtSignal(str)  # execution_id
        state_changed = QtCore.pyqtSignal(str, str)  # execution_id, new_state

        def __init__(self, parent: Optional[QtCore.QObject] = None):
            super().__init__(parent)
            self._executions: Dict[str, WorkflowExecution] = {}
            self._execution_history: List[str] = []
            self._max_history = 100

        def create_execution(
            self,
            workflow_path: str,
            files: Optional[str] = None,
            dry_run: bool = False,
        ) -> str:
            """Create a new workflow execution.

            Args:
                workflow_path: Path to workflow YAML file
                files: Optional file pattern for inputs
                dry_run: If True, validate without executing

            Returns:
                Execution ID
            """
            import secrets
            from datetime import datetime

            execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"

            execution = WorkflowExecution(
                id=execution_id,
                workflow_path=workflow_path,
                state=ExecutionState.QUEUED,
                dry_run=dry_run,
            )

            self._executions[execution_id] = execution
            self._execution_history.append(execution_id)

            # Trim history
            if len(self._execution_history) > self._max_history:
                oldest_id = self._execution_history.pop(0)
                if oldest_id in self._executions:
                    del self._executions[oldest_id]

            self.execution_queued.emit(execution_id)
            return execution_id

        def start_execution(self, execution_id: str) -> None:
            """Start a queued execution.

            Args:
                execution_id: ID of execution to start
            """
            if execution_id not in self._executions:
                return

            execution = self._executions[execution_id]
            execution.state = ExecutionState.RUNNING
            execution.start_time = datetime.now()

            self.execution_started.emit(execution_id)
            self.state_changed.emit(execution_id, execution.state.value)

        def update_progress(
            self, execution_id: str, current_step: int, total_steps: int
        ) -> None:
            """Update execution progress.

            Args:
                execution_id: ID of execution
                current_step: Current step number
                total_steps: Total number of steps
            """
            if execution_id not in self._executions:
                return

            execution = self._executions[execution_id]
            execution.current_step = current_step
            execution.total_steps = total_steps

            self.execution_progress.emit(execution_id, current_step, total_steps)

        def complete_execution(
            self, execution_id: str, success: bool, error_message: Optional[str] = None
        ) -> None:
            """Mark execution as completed.

            Args:
                execution_id: ID of execution
                success: Whether execution succeeded
                error_message: Optional error message if failed
            """
            if execution_id not in self._executions:
                return

            execution = self._executions[execution_id]
            execution.state = ExecutionState.COMPLETED if success else ExecutionState.FAILED
            execution.end_time = datetime.now()
            execution.error_message = error_message

            self.execution_completed.emit(execution_id, success)
            self.state_changed.emit(execution_id, execution.state.value)

        def cancel_execution(self, execution_id: str) -> None:
            """Cancel a running execution.

            Args:
                execution_id: ID of execution to cancel
            """
            if execution_id not in self._executions:
                return

            execution = self._executions[execution_id]
            if execution.state in [ExecutionState.RUNNING, ExecutionState.QUEUED]:
                execution.state = ExecutionState.CANCELLED
                execution.end_time = datetime.now()

                self.execution_cancelled.emit(execution_id)
                self.state_changed.emit(execution_id, execution.state.value)

        def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
            """Get execution by ID.

            Args:
                execution_id: ID of execution

            Returns:
                WorkflowExecution or None if not found
            """
            return self._executions.get(execution_id)

        def get_active_executions(self) -> List[WorkflowExecution]:
            """Get all active (running/queued) executions.

            Returns:
                List of active WorkflowExecution instances
            """
            return [
                exec
                for exec in self._executions.values()
                if exec.state in [ExecutionState.RUNNING, ExecutionState.QUEUED]
            ]

        def get_execution_history(self, limit: int = 20) -> List[WorkflowExecution]:
            """Get recent execution history.

            Args:
                limit: Maximum number of executions to return

            Returns:
                List of recent WorkflowExecution instances
            """
            recent_ids = self._execution_history[-limit:]
            return [
                self._executions[exec_id]
                for exec_id in reversed(recent_ids)
                if exec_id in self._executions
            ]

        def clear_completed(self) -> int:
            """Clear completed/failed executions from memory.

            Returns:
                Number of executions cleared
            """
            to_remove = [
                exec_id
                for exec_id, exec in self._executions.items()
                if exec.state in [ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED]
            ]

            for exec_id in to_remove:
                del self._executions[exec_id]
                if exec_id in self._execution_history:
                    self._execution_history.remove(exec_id)

            return len(to_remove)

else:
    # Headless fallback

    class ExecutionManager:
        """Headless execution manager fallback."""

        def __init__(self, parent=None):
            self._executions = {}

        def create_execution(self, workflow_path: str, files: Optional[str] = None, dry_run: bool = False) -> str:
            import secrets
            return f"exec_{secrets.token_hex(8)}"

        def start_execution(self, execution_id: str) -> None:
            pass

        def update_progress(self, execution_id: str, current_step: int, total_steps: int) -> None:
            pass

        def complete_execution(self, execution_id: str, success: bool, error_message: Optional[str] = None) -> None:
            pass

        def cancel_execution(self, execution_id: str) -> None:
            pass

        def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
            return None

        def get_active_executions(self) -> List[WorkflowExecution]:
            return []

        def get_execution_history(self, limit: int = 20) -> List[WorkflowExecution]:
            return []

        def clear_completed(self) -> int:
            return 0
