"""Workflow coordination classes."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class CoordinationMode(str, Enum):
    """Coordination execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    IPT_WT = "ipt_wt"  # Independent Parallel Tasks with Workflow Threading


@dataclass
class CoordinationPlan:
    """Plan for coordinating workflow execution."""
    mode: CoordinationMode
    parallel_groups: list[list[str]] = None
    dependencies: dict[str, list[str]] = None

    def __post_init__(self):
        if self.parallel_groups is None:
            self.parallel_groups = []
        if self.dependencies is None:
            self.dependencies = {}


class WorkflowCoordinator:
    """Coordinates workflow execution across steps."""

    def __init__(self):
        self.active_workflows: dict[str, Any] = {}

    def register_workflow(self, workflow_id: str, plan: CoordinationPlan) -> None:
        """Register a workflow for coordination."""
        self.active_workflows[workflow_id] = plan

    def unregister_workflow(self, workflow_id: str) -> None:
        """Unregister a completed workflow."""
        self.active_workflows.pop(workflow_id, None)

    def get_plan(self, workflow_id: str) -> Optional[CoordinationPlan]:
        """Get coordination plan for a workflow."""
        return self.active_workflows.get(workflow_id)


class FileScopeManager:
    """Manages file scope and locking for workflows."""

    def __init__(self):
        self.file_locks: dict[str, str] = {}  # file_path -> workflow_id

    def acquire_file(self, workflow_id: str, file_path: str) -> bool:
        """Acquire exclusive access to a file."""
        if file_path in self.file_locks:
            return self.file_locks[file_path] == workflow_id
        self.file_locks[file_path] = workflow_id
        return True

    def release_file(self, workflow_id: str, file_path: str) -> None:
        """Release exclusive access to a file."""
        if self.file_locks.get(file_path) == workflow_id:
            del self.file_locks[file_path]

    def release_all(self, workflow_id: str) -> None:
        """Release all files held by a workflow."""
        files_to_release = [
            path for path, wf_id in self.file_locks.items()
            if wf_id == workflow_id
        ]
        for path in files_to_release:
            del self.file_locks[path]
