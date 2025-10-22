"""Tests for execution manager."""

import pytest
from pathlib import Path

try:
    from PyQt6 import QtWidgets
    from gui_terminal.core.execution_manager import ExecutionManager, ExecutionState

    PyQt6Available = True
except ImportError:
    PyQt6Available = False


@pytest.mark.skipif(not PyQt6Available, reason="PyQt6 not available")
class TestExecutionManager:
    """Tests for ExecutionManager."""

    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])
        return app

    @pytest.fixture
    def manager(self, app):
        """Create ExecutionManager instance."""
        return ExecutionManager()

    def test_create_execution(self, manager):
        """Test execution creation."""
        exec_id = manager.create_execution("test_workflow.yaml")
        assert exec_id is not None
        assert exec_id.startswith("exec_")

        execution = manager.get_execution(exec_id)
        assert execution is not None
        assert execution.workflow_path == "test_workflow.yaml"
        assert execution.state == ExecutionState.QUEUED

    def test_start_execution(self, manager):
        """Test starting execution."""
        exec_id = manager.create_execution("test_workflow.yaml")
        manager.start_execution(exec_id)

        execution = manager.get_execution(exec_id)
        assert execution.state == ExecutionState.RUNNING
        assert execution.start_time is not None

    def test_update_progress(self, manager):
        """Test progress updates."""
        exec_id = manager.create_execution("test_workflow.yaml")
        manager.start_execution(exec_id)
        manager.update_progress(exec_id, 5, 10)

        execution = manager.get_execution(exec_id)
        assert execution.current_step == 5
        assert execution.total_steps == 10
        assert execution.progress_percentage == 50

    def test_complete_execution(self, manager):
        """Test execution completion."""
        exec_id = manager.create_execution("test_workflow.yaml")
        manager.start_execution(exec_id)
        manager.complete_execution(exec_id, success=True)

        execution = manager.get_execution(exec_id)
        assert execution.state == ExecutionState.COMPLETED
        assert execution.end_time is not None
        assert execution.duration is not None

    def test_cancel_execution(self, manager):
        """Test execution cancellation."""
        exec_id = manager.create_execution("test_workflow.yaml")
        manager.start_execution(exec_id)
        manager.cancel_execution(exec_id)

        execution = manager.get_execution(exec_id)
        assert execution.state == ExecutionState.CANCELLED

    def test_execution_history(self, manager):
        """Test execution history."""
        # Create multiple executions
        for i in range(5):
            exec_id = manager.create_execution(f"workflow_{i}.yaml")
            manager.complete_execution(exec_id, success=True)

        history = manager.get_execution_history(limit=3)
        assert len(history) == 3

    def test_active_executions(self, manager):
        """Test getting active executions."""
        # Create mix of active and completed
        exec1 = manager.create_execution("workflow1.yaml")
        manager.start_execution(exec1)

        exec2 = manager.create_execution("workflow2.yaml")
        manager.start_execution(exec2)
        manager.complete_execution(exec2, success=True)

        active = manager.get_active_executions()
        assert len(active) == 1
        assert active[0].id == exec1

    def test_clear_completed(self, manager):
        """Test clearing completed executions."""
        # Create and complete executions
        for i in range(3):
            exec_id = manager.create_execution(f"workflow_{i}.yaml")
            manager.complete_execution(exec_id, success=True)

        cleared = manager.clear_completed()
        assert cleared == 3
