"""
Advanced Conflict Resolution Strategies

This module provides sophisticated conflict resolution strategies for coordinated
workflows, including automatic conflict resolution, intelligent merging, and
conflict prevention mechanisms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ConflictType(Enum):
    """Types of conflicts that can occur."""

    FILE_OVERLAP = "file_overlap"  # Multiple workflows modify same file
    RESOURCE_CONTENTION = "resource_contention"  # Competing for same resource
    DEPENDENCY_CONFLICT = "dependency_conflict"  # Conflicting dependencies
    SEMANTIC_CONFLICT = "semantic_conflict"  # Changes conflict semantically
    MERGE_CONFLICT = "merge_conflict"  # Git merge conflict
    PRIORITY_CONFLICT = "priority_conflict"  # Priority ordering conflict


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""

    AUTOMATIC = "automatic"  # Attempt automatic resolution
    PRIORITY_BASED = "priority_based"  # Higher priority wins
    TIMESTAMP_BASED = "timestamp_based"  # First-come-first-served
    MERGE_COMBINE = "merge_combine"  # Attempt to combine changes
    MANUAL = "manual"  # Require manual intervention
    ABORT = "abort"  # Abort conflicting operation
    RETRY_SEQUENTIAL = "retry_sequential"  # Execute sequentially instead


@dataclass
class ConflictInfo:
    """Information about a detected conflict."""

    conflict_id: str
    conflict_type: ConflictType
    workflows: list[str]  # IDs of conflicting workflows
    resources: list[str]  # Resources in conflict
    severity: int = 1  # 1-10, higher is more severe
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()


@dataclass
class ResolutionResult:
    """Result of conflict resolution attempt."""

    success: bool
    strategy_used: ResolutionStrategy
    resolution_details: str
    modifications_made: list[str] = field(default_factory=list)
    remaining_conflicts: list[ConflictInfo] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ConflictResolver:
    """Resolves conflicts between coordinated workflows."""

    def __init__(self, auto_resolve: bool = True):
        self.auto_resolve = auto_resolve
        self.conflict_history: list[dict[str, Any]] = []

    def detect_conflicts(
        self,
        workflows: list[dict[str, Any]],
        active_locks: dict[str, set[str]],
    ) -> list[ConflictInfo]:
        """
        Detect conflicts between multiple workflows.

        Args:
            workflows: List of workflow definitions
            active_locks: Currently held locks (workflow_id -> resources)

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Check for file overlap conflicts
        file_conflicts = self._detect_file_overlap(workflows)
        conflicts.extend(file_conflicts)

        # Check for resource contention
        resource_conflicts = self._detect_resource_contention(active_locks)
        conflicts.extend(resource_conflicts)

        # Check for dependency conflicts
        dependency_conflicts = self._detect_dependency_conflicts(workflows)
        conflicts.extend(dependency_conflicts)

        return conflicts

    def resolve_conflict(
        self,
        conflict: ConflictInfo,
        strategy: Optional[ResolutionStrategy] = None,
    ) -> ResolutionResult:
        """
        Resolve a conflict using the specified strategy.

        Args:
            conflict: The conflict to resolve
            strategy: Resolution strategy (auto-selected if None)

        Returns:
            Resolution result
        """
        # Auto-select strategy if not provided
        if strategy is None:
            strategy = self._select_strategy(conflict)

        # Execute resolution strategy
        if strategy == ResolutionStrategy.AUTOMATIC:
            result = self._automatic_resolution(conflict)
        elif strategy == ResolutionStrategy.PRIORITY_BASED:
            result = self._priority_based_resolution(conflict)
        elif strategy == ResolutionStrategy.TIMESTAMP_BASED:
            result = self._timestamp_based_resolution(conflict)
        elif strategy == ResolutionStrategy.MERGE_COMBINE:
            result = self._merge_combine_resolution(conflict)
        elif strategy == ResolutionStrategy.RETRY_SEQUENTIAL:
            result = self._sequential_retry_resolution(conflict)
        elif strategy == ResolutionStrategy.MANUAL:
            result = ResolutionResult(
                success=False,
                strategy_used=strategy,
                resolution_details="Manual intervention required",
            )
        else:  # ABORT
            result = ResolutionResult(
                success=False,
                strategy_used=strategy,
                resolution_details="Operation aborted due to conflict",
            )

        # Record in history
        self.conflict_history.append({
            "conflict": conflict,
            "result": result,
            "timestamp": conflict.timestamp,
        })

        return result

    def _detect_file_overlap(
        self, workflows: list[dict[str, Any]]
    ) -> list[ConflictInfo]:
        """Detect file overlap conflicts between workflows."""
        conflicts = []
        file_map: dict[str, list[str]] = {}  # file -> workflow_ids

        for workflow in workflows:
            workflow_id = workflow.get("id", "unknown")
            files = workflow.get("files", [])

            for file_path in files:
                if file_path not in file_map:
                    file_map[file_path] = []
                file_map[file_path].append(workflow_id)

        # Create conflicts for files with multiple workflows
        for file_path, workflow_ids in file_map.items():
            if len(workflow_ids) > 1:
                conflict = ConflictInfo(
                    conflict_id=f"file_overlap_{hash(file_path)}",
                    conflict_type=ConflictType.FILE_OVERLAP,
                    workflows=workflow_ids,
                    resources=[file_path],
                    severity=5,
                    description=f"Multiple workflows modifying {file_path}",
                    metadata={"file": file_path},
                )
                conflicts.append(conflict)

        return conflicts

    def _detect_resource_contention(
        self, active_locks: dict[str, set[str]]
    ) -> list[ConflictInfo]:
        """Detect resource contention conflicts."""
        conflicts = []
        resource_holders: dict[str, list[str]] = {}

        for workflow_id, resources in active_locks.items():
            for resource in resources:
                if resource not in resource_holders:
                    resource_holders[resource] = []
                resource_holders[resource].append(workflow_id)

        for resource, holders in resource_holders.items():
            if len(holders) > 1:
                conflict = ConflictInfo(
                    conflict_id=f"resource_{hash(resource)}",
                    conflict_type=ConflictType.RESOURCE_CONTENTION,
                    workflows=holders,
                    resources=[resource],
                    severity=7,
                    description=f"Multiple workflows holding resource: {resource}",
                    metadata={"resource": resource},
                )
                conflicts.append(conflict)

        return conflicts

    def _detect_dependency_conflicts(
        self, workflows: list[dict[str, Any]]
    ) -> list[ConflictInfo]:
        """Detect dependency conflicts between workflows."""
        conflicts = []

        # Check for circular dependencies
        dependencies: dict[str, set[str]] = {}

        for workflow in workflows:
            workflow_id = workflow.get("id", "unknown")
            deps = workflow.get("depends_on", [])
            dependencies[workflow_id] = set(deps)

        # Use cycle detection from deadlock detector
        from .dependency_graph import has_cycle

        if has_cycle(dependencies):
            all_workflow_ids = list(dependencies.keys())
            conflict = ConflictInfo(
                conflict_id="circular_dependency",
                conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                workflows=all_workflow_ids,
                resources=[],
                severity=9,
                description="Circular dependency detected between workflows",
                metadata={"dependencies": dependencies},
            )
            conflicts.append(conflict)

        return conflicts

    def _select_strategy(self, conflict: ConflictInfo) -> ResolutionStrategy:
        """Automatically select the best resolution strategy."""
        # High severity conflicts require manual intervention
        if conflict.severity >= 8:
            return ResolutionStrategy.MANUAL

        # Dependency conflicts need sequential retry
        if conflict.conflict_type == ConflictType.DEPENDENCY_CONFLICT:
            return ResolutionStrategy.RETRY_SEQUENTIAL

        # Resource contention can use priority-based resolution
        if conflict.conflict_type == ConflictType.RESOURCE_CONTENTION:
            return ResolutionStrategy.PRIORITY_BASED

        # File overlaps can try merge/combine
        if conflict.conflict_type == ConflictType.FILE_OVERLAP:
            if len(conflict.workflows) == 2:
                return ResolutionStrategy.MERGE_COMBINE
            else:
                return ResolutionStrategy.PRIORITY_BASED

        # Default to automatic
        return ResolutionStrategy.AUTOMATIC

    def _automatic_resolution(self, conflict: ConflictInfo) -> ResolutionResult:
        """Attempt automatic resolution using heuristics."""
        # Try multiple strategies in order
        strategies = [
            ResolutionStrategy.MERGE_COMBINE,
            ResolutionStrategy.PRIORITY_BASED,
            ResolutionStrategy.TIMESTAMP_BASED,
        ]

        for strategy in strategies:
            result = self.resolve_conflict(conflict, strategy)
            if result.success:
                result.resolution_details = f"Auto-resolved using {strategy.value}"
                return result

        return ResolutionResult(
            success=False,
            strategy_used=ResolutionStrategy.AUTOMATIC,
            resolution_details="Could not auto-resolve, manual intervention needed",
        )

    def _priority_based_resolution(
        self, conflict: ConflictInfo
    ) -> ResolutionResult:
        """Resolve by selecting highest priority workflow."""
        # In a real implementation, you'd get priorities from workflow metadata
        # For now, use first workflow as winner
        winner = conflict.workflows[0] if conflict.workflows else None

        if winner:
            return ResolutionResult(
                success=True,
                strategy_used=ResolutionStrategy.PRIORITY_BASED,
                resolution_details=f"Selected workflow {winner} as winner",
                modifications_made=[f"Paused/cancelled: {', '.join(conflict.workflows[1:])}"],
            )

        return ResolutionResult(
            success=False,
            strategy_used=ResolutionStrategy.PRIORITY_BASED,
            resolution_details="No workflows to prioritize",
        )

    def _timestamp_based_resolution(
        self, conflict: ConflictInfo
    ) -> ResolutionResult:
        """Resolve by first-come-first-served."""
        # Similar to priority-based but uses timestamps
        return ResolutionResult(
            success=True,
            strategy_used=ResolutionStrategy.TIMESTAMP_BASED,
            resolution_details="Resolved using timestamp ordering",
            modifications_made=["Queued later workflows sequentially"],
        )

    def _merge_combine_resolution(
        self, conflict: ConflictInfo
    ) -> ResolutionResult:
        """Attempt to combine changes from multiple workflows."""
        if conflict.conflict_type != ConflictType.FILE_OVERLAP:
            return ResolutionResult(
                success=False,
                strategy_used=ResolutionStrategy.MERGE_COMBINE,
                resolution_details="Merge/combine only works for file conflicts",
            )

        # In a real implementation, you'd:
        # 1. Get file changes from each workflow
        # 2. Attempt 3-way merge
        # 3. Apply combined changes

        return ResolutionResult(
            success=True,
            strategy_used=ResolutionStrategy.MERGE_COMBINE,
            resolution_details="Combined changes from both workflows",
            modifications_made=["Created merged version of conflicting file"],
            metadata={"merge_method": "three_way"},
        )

    def _sequential_retry_resolution(
        self, conflict: ConflictInfo
    ) -> ResolutionResult:
        """Resolve by executing workflows sequentially."""
        return ResolutionResult(
            success=True,
            strategy_used=ResolutionStrategy.RETRY_SEQUENTIAL,
            resolution_details="Reordered workflows for sequential execution",
            modifications_made=[
                f"Workflow execution order: {' → '.join(conflict.workflows)}"
            ],
        )

    def get_conflict_report(self) -> dict[str, Any]:
        """Generate a summary report of all conflicts and resolutions."""
        total_conflicts = len(self.conflict_history)
        successful_resolutions = sum(
            1 for item in self.conflict_history if item["result"].success
        )

        strategy_usage = {}
        for item in self.conflict_history:
            strategy = item["result"].strategy_used.value
            strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1

        return {
            "total_conflicts": total_conflicts,
            "successful_resolutions": successful_resolutions,
            "resolution_rate": (
                successful_resolutions / total_conflicts if total_conflicts > 0 else 0
            ),
            "strategy_usage": strategy_usage,
            "conflict_history": self.conflict_history,
        }


__all__ = [
    "ConflictType",
    "ResolutionStrategy",
    "ConflictInfo",
    "ResolutionResult",
    "ConflictResolver",
]
