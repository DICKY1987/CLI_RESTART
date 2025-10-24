from __future__ import annotations

from typing import Any, Callable

from .models import ParallelRoutingPlan, RoutingDecision


class ParallelPlanner:
    """Create parallel execution plans with basic conflict awareness."""

    def __init__(self, scope_manager: Any) -> None:
        self.scope_manager = scope_manager

    def create_parallel_plan(
        self,
        steps: list[dict[str, Any]],
        route_step: Callable[[dict[str, Any]], RoutingDecision],
        policy: dict[str, Any] | None = None,
    ) -> ParallelRoutingPlan:
        routing_decisions: list[tuple[dict[str, Any], RoutingDecision]] = []
        file_claims: list[Any] = []

        for i, step in enumerate(steps):
            decision = route_step(step) if policy is None else route_step(step)
            routing_decisions.append((step, decision))

            files = step.get("files", [])
            file_scope = step.get("file_scope", [])
            if files or file_scope:
                patterns: list[str] = []
                if files:
                    patterns.extend(files if isinstance(files, list) else [files])
                if file_scope:
                    patterns.extend(file_scope if isinstance(file_scope, list) else [file_scope])
                if patterns:
                    # Scope types are provided by coordination; build a lightweight claim
                    claim = type("FileClaim", (), {})()
                    claim.workflow_ids = [f"step_{i}_{step.get('id', 'unknown')}"]
                    claim.file_patterns = patterns
                    claim.mode = step.get("scope_mode", "exclusive")
                    file_claims.append(claim)

        conflicts = []
        try:
            conflicts = self.scope_manager.detect_conflicts(file_claims)
        except Exception:
            conflicts = []

        execution_groups = self._create_execution_groups(steps, routing_decisions, conflicts)
        resource_allocation = self._calculate_resource_allocation(routing_decisions)
        total_cost = sum(dec.estimated_tokens for _, dec in routing_decisions)

        return ParallelRoutingPlan(
            routing_decisions=routing_decisions,
            execution_groups=execution_groups,
            total_estimated_cost=total_cost,
            conflicts=conflicts,
            resource_allocation=resource_allocation,
        )

    def _create_execution_groups(
        self,
        steps: list[dict[str, Any]],
        routing_decisions: list[tuple[dict[str, Any], RoutingDecision]],
        conflicts: list[Any],
    ) -> list[list[int]]:
        groups: list[list[int]] = []

        if not conflicts:
            deterministic_steps: list[int] = []
            ai_steps: list[int] = []
            for i, (_step, decision) in enumerate(routing_decisions):
                if decision.adapter_type == "deterministic":
                    deterministic_steps.append(i)
                else:
                    ai_steps.append(i)
            if deterministic_steps:
                groups.append(deterministic_steps)
            while ai_steps:
                batch = ai_steps[:3]
                groups.append(batch)
                ai_steps = ai_steps[3:]
            return groups

        conflicting_step_ids: set[int] = set()
        for conflict in conflicts:
            for workflow_id in getattr(conflict, "workflow_ids", []) or []:
                if isinstance(workflow_id, str) and workflow_id.startswith("step_"):
                    try:
                        step_index = int(workflow_id.split("_")[1])
                        conflicting_step_ids.add(step_index)
                    except Exception:
                        pass

        non_conflicting: list[int] = []
        for i in range(len(steps)):
            if i not in conflicting_step_ids:
                non_conflicting.append(i)
        if non_conflicting:
            groups.append(non_conflicting)
        for sid in conflicting_step_ids:
            groups.append([sid])
        return groups

    def _calculate_resource_allocation(
        self, routing_decisions: list[tuple[dict[str, Any], RoutingDecision]]
    ) -> dict[str, list[int]]:
        allocation: dict[str, list[int]] = {}
        for i, (_step, decision) in enumerate(routing_decisions):
            allocation.setdefault(decision.adapter_name, []).append(i)
        return allocation

