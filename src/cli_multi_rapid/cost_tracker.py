#!/usr/bin/env python3
"""
CLI Orchestrator Cost Tracker (Backward-Compatible Wrapper)

Thin adapter that delegates to domain layer `domain.cost.tracker.CostTracker`
and file storage adapter `adapters.storage.cost_storage.FileCostStorage`.
"""

from datetime import date
from typing import Any, Optional

from rich.console import Console

from .adapters.storage.cost_storage import FileCostStorage
from .domain.cost.models import BudgetLimit, CoordinationBudget, WorkflowCostSummary
from .domain.cost.tracker import CostTracker as DomainCostTracker

console = Console()


class CostTracker:
    """Backward-compatible facade around domain cost tracker."""

    def __init__(self, logs_dir: str = "logs"):
        storage = FileCostStorage(logs_dir=logs_dir)
        self._tracker = DomainCostTracker(storage=storage)

    # Compatibility shim used by executor
    def add_tokens(self, operation: str, tokens_used: int, model: str = "unknown") -> float:
        return self._tracker.add_tokens(operation, tokens_used, model)

    def record_usage(
        self,
        operation: str,
        tokens_used: int,
        model: str = "unknown",
        success: bool = True,
        workflow_id: Optional[str] = None,
        coordination_id: Optional[str] = None,
        phase_id: Optional[str] = None,
        adapter_name: Optional[str] = None,
    ) -> float:
        return self._tracker.record_usage(
            operation=operation,
            tokens_used=tokens_used,
            model=model,
            success=success,
            workflow_id=workflow_id,
            coordination_id=coordination_id,
            phase_id=phase_id,
            adapter_name=adapter_name,
        )

    def get_daily_usage(self, target_date: Optional[date] = None) -> dict[str, Any]:
        return self._tracker.get_daily_usage(target_date)

    def check_budget_limits(
        self, budget: Optional[BudgetLimit] = None, tokens_to_spend: int = 0
    ) -> dict[str, Any]:
        return self._tracker.check_budget_limits(budget, tokens_to_spend)

    def generate_report(self, last_run: bool = False, detailed: bool = False, days: int = 7) -> dict[str, Any]:
        return self._tracker.generate_report(last_run=last_run, detailed=detailed, days=days)

    def track_coordinated_cost(
        self,
        coordination_id: str,
        workflow_id: str,
        operation: str,
        tokens_used: int,
        model: str = "unknown",
        phase_id: Optional[str] = None,
        adapter_name: Optional[str] = None,
    ) -> float:
        return self._tracker.track_coordinated_cost(
            coordination_id=coordination_id,
            workflow_id=workflow_id,
            operation=operation,
            tokens_used=tokens_used,
            model=model,
            phase_id=phase_id,
            adapter_name=adapter_name,
        )

    def allocate_budget(
        self, workflows: list[dict[str, Any]], coordination_budget: CoordinationBudget
    ) -> dict[str, float]:
        return self._tracker.allocate_budget(workflows, coordination_budget)

    def get_coordination_summary(self, coordination_id: str) -> dict[str, Any]:
        return self._tracker.get_coordination_summary(coordination_id)

    def get_workflow_cost_summary(
        self, workflow_id: str, coordination_id: Optional[str] = None
    ) -> WorkflowCostSummary:
        return self._tracker.get_workflow_cost_summary(workflow_id, coordination_id)

    def check_coordination_budget(
        self, coordination_id: str, coordination_budget: CoordinationBudget
    ) -> dict[str, Any]:
        return self._tracker.check_coordination_budget(coordination_id, coordination_budget)

    def optimize_remaining_allocation(
        self,
        coordination_id: str,
        remaining_workflows: list[str],
        coordination_budget: CoordinationBudget,
    ) -> dict[str, float]:
        return self._tracker.optimize_remaining_allocation(
            coordination_id, remaining_workflows, coordination_budget
        )

    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        return self._tracker.cleanup_old_logs(days_to_keep)

