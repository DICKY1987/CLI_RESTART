from __future__ import annotations

from typing import Any, Optional

from .models import AllocationPlan, RoutingDecision


class ResourceAllocator:
    """Allocate adapters and estimate costs across workflows."""

    def __init__(self, route_step_func):
        self._route_step = route_step_func

    def create_allocation_plan(
        self,
        workflows: list[dict[str, Any]],
        budget: Optional[float] = None,
        max_parallel: int = 3,
    ) -> AllocationPlan:
        adapter_assignments: dict[str, dict[str, Any]] = {}
        total_cost = 0

        for workflow in workflows:
            workflow_name = workflow.get("name", "unnamed_workflow")
            phases = workflow.get("phases", [])
            steps = workflow.get("steps", [])

            if phases:
                for phase in phases:
                    phase_id = phase.get("id", "unknown_phase")
                    tasks = phase.get("tasks", [])
                    for task in tasks:
                        task_id = (
                            f"{workflow_name}_{phase_id}_{task}"
                            if isinstance(task, str)
                            else f"{workflow_name}_{phase_id}_{task.get('id', 'unknown')}"
                        )
                        step = task if isinstance(task, dict) else {"id": task, "actor": "unknown", "name": task}
                        decision: RoutingDecision = self._route_step(step)
                        cost = decision.estimated_tokens
                        adapter_assignments[task_id] = {
                            "adapter": decision.adapter_name,
                            "adapter_type": decision.adapter_type,
                            "estimated_cost": cost,
                            "priority": phase.get("priority", 1),
                            "workflow": workflow_name,
                            "phase": phase_id,
                        }
                        total_cost += cost
            elif steps:
                for step in steps:
                    step_id = f"{workflow_name}_{step.get('id', 'unknown_step')}"
                    decision: RoutingDecision = self._route_step(step)
                    cost = decision.estimated_tokens
                    adapter_assignments[step_id] = {
                        "adapter": decision.adapter_name,
                        "adapter_type": decision.adapter_type,
                        "estimated_cost": cost,
                        "priority": step.get("priority", 1),
                        "workflow": workflow_name,
                    }
                    total_cost += cost

        parallel_groups = self._create_workflow_parallel_groups(workflows)
        estimated_usd_cost = total_cost * 0.0005  # rough: $0.50 per 1k tokens
        within_budget = budget is None or estimated_usd_cost <= budget

        return AllocationPlan(
            assignments=adapter_assignments,
            total_estimated_cost=total_cost,
            estimated_usd_cost=estimated_usd_cost,
            within_budget=within_budget,
            parallel_groups=parallel_groups,
        )

    def _create_workflow_parallel_groups(self, workflows: list[dict[str, Any]]) -> list[list[str]]:
        priority_groups: dict[int, list[str]] = {}
        for workflow in workflows:
            name = workflow.get("name", "unnamed_workflow")
            priority = workflow.get("metadata", {}).get("coordination", {}).get("priority", 1)
            priority_groups.setdefault(int(priority), []).append(name)
        groups: list[list[str]] = []
        for priority in sorted(priority_groups.keys(), reverse=True):
            groups.append(priority_groups[priority])
        return groups

