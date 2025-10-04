"""Workflow coordination classes and basic file scope types.

Minimal, test-friendly implementations:
- CoordinationMode, CoordinationPlan, WorkflowCoordinator
- ScopeMode, FileClaim, ScopeConflict
- FileScopeManager with simple locking and conflict detection
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class CoordinationMode(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    IPT_WT = "ipt_wt"


class ScopeMode(str, Enum):
    EXCLUSIVE = "exclusive"
    SHARED = "shared"


@dataclass
class FileClaim:
    workflow_id: str
    file_patterns: List[str]
    mode: ScopeMode = ScopeMode.EXCLUSIVE


@dataclass
class ScopeConflict:
    workflow_ids: List[str]
    conflicting_patterns: List[str]


@dataclass
class CoordinationPlan:
    mode: CoordinationMode
    parallel_groups: List[List[str]] = None
    dependencies: Dict[str, List[str]] = None

    def __post_init__(self) -> None:
        if self.parallel_groups is None:
            self.parallel_groups = []
        if self.dependencies is None:
            self.dependencies = {}


class WorkflowCoordinator:
    def __init__(self) -> None:
        self.active_workflows: Dict[str, Any] = {}

    def register_workflow(self, workflow_id: str, plan: CoordinationPlan) -> None:
        self.active_workflows[workflow_id] = plan

    def unregister_workflow(self, workflow_id: str) -> None:
        self.active_workflows.pop(workflow_id, None)

    def get_plan(self, workflow_id: str) -> Optional[CoordinationPlan]:
        return self.active_workflows.get(workflow_id)


class FileScopeManager:
    def __init__(self) -> None:
        self.file_locks: Dict[str, str] = {}  # file_path -> workflow_id

    def acquire_file(self, workflow_id: str, file_path: str) -> bool:
        if file_path in self.file_locks and self.file_locks[file_path] != workflow_id:
            return False
        self.file_locks[file_path] = workflow_id
        return True

    def release_file(self, workflow_id: str, file_path: str) -> None:
        if self.file_locks.get(file_path) == workflow_id:
            del self.file_locks[file_path]

    def release_all(self, workflow_id: str) -> None:
        to_release = [p for p, wf in self.file_locks.items() if wf == workflow_id]
        for p in to_release:
            del self.file_locks[p]

    def detect_conflicts(self, claims: List[FileClaim]) -> List[ScopeConflict]:
        """Detect conflicts among claims by exact pattern equality.

        Two claims conflict if they include the same pattern and at least one
        claim is EXCLUSIVE.
        """
        conflicts: List[ScopeConflict] = []
        pattern_map: Dict[str, List[tuple[str, ScopeMode]]] = {}
        for claim in claims:
            for pat in claim.file_patterns:
                pattern_map.setdefault(pat, []).append((claim.workflow_id, claim.mode))

        for pat, entries in pattern_map.items():
            if len(entries) > 1 and any(mode == ScopeMode.EXCLUSIVE for _, mode in entries):
                conflicts.append(
                    ScopeConflict(
                        workflow_ids=[wf for wf, _ in entries],
                        conflicting_patterns=[pat],
                    )
                )
        return conflicts
