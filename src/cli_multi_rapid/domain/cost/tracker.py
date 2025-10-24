from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any, Optional

from ...adapters.storage.cost_storage_port import CostStoragePort
from .calculator import CostCalculator
from .models import BudgetLimit, CoordinationBudget, TokenUsage, WorkflowCostSummary


class CostTracker:
    """Pure domain cost tracker that delegates persistence to a storage port."""

    def __init__(
        self,
        storage: CostStoragePort,
        calculator: Optional[CostCalculator] = None,
    ) -> None:
        self.storage = storage
        self.calculator = calculator or CostCalculator()

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
        cost_per_token = self.calculator.per_token(model)
        estimated_cost = tokens_used * cost_per_token
        usage = TokenUsage(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            tokens_used=tokens_used,
            estimated_cost=estimated_cost,
            model=model,
            success=success,
            workflow_id=workflow_id,
            coordination_id=coordination_id,
            phase_id=phase_id,
            adapter_name=adapter_name,
        )
        self.storage.save(usage.to_dict())
        return estimated_cost

    # Compatibility helper (used by executor)
    def add_tokens(self, operation: str, tokens_used: int, model: str = "unknown") -> float:
        return self.record_usage(operation=operation, tokens_used=tokens_used, model=model)

    def get_daily_usage(self, target_date: Optional[date] = None) -> dict[str, Any]:
        if target_date is None:
            target_date = date.today()

        daily_tokens = 0
        daily_cost = 0.0
        operations: list[dict[str, Any]] = []
        for rec in self.storage.iter_by_date(target_date):
            daily_tokens += int(rec.get("tokens_used", 0))
            daily_cost += float(rec.get("estimated_cost", 0.0))
            operations.append(rec)
        return {
            "date": target_date.isoformat(),
            "total_tokens": daily_tokens,
            "total_cost": daily_cost,
            "operations": operations,
            "operation_count": len(operations),
        }

    def check_budget_limits(
        self, budget: Optional[BudgetLimit] = None, tokens_to_spend: int = 0
    ) -> dict[str, Any]:
        from .budget_manager import BudgetManager

        mgr = BudgetManager()
        return mgr.check_limits(self.get_daily_usage, budget, tokens_to_spend)

    def generate_report(self, last_run: bool = False, detailed: bool = False, days: int = 7) -> dict[str, Any]:
        # Minimal viable implementation; same-day aggregation (legacy behavior)
        if last_run:
            last = None
            for rec in self.storage.iter_all():
                last = rec
            if last:
                return {
                    "period": "last_run",
                    "operation": last.get("operation"),
                    "tokens": int(last.get("tokens_used", 0)),
                    "cost": float(last.get("estimated_cost", 0.0)),
                    "timestamp": last.get("timestamp"),
                    "success": bool(last.get("success", True)),
                }
            return {"period": "last_run", "error": "No operations found"}

        today_usage = self.get_daily_usage()
        report = {
            "period": f"last_{days}_days",
            "total_tokens": today_usage["total_tokens"],
            "estimated_cost": today_usage["total_cost"],
            "runs_today": today_usage["operation_count"],
            "average_cost_per_run": today_usage["total_cost"] / max(today_usage["operation_count"], 1),
        }
        if detailed:
            report["daily_breakdown"] = today_usage
        return report

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
        return self.record_usage(
            operation=operation,
            tokens_used=tokens_used,
            model=model,
            workflow_id=workflow_id,
            coordination_id=coordination_id,
            phase_id=phase_id,
            adapter_name=adapter_name,
        )

    def allocate_budget(
        self,
        workflows: list[dict[str, Any]],
        coordination_budget: CoordinationBudget,
    ) -> dict[str, float]:
        allocations: dict[str, float] = {}
        remaining_budget = coordination_budget.total_budget - coordination_budget.emergency_reserve
        workflow_priorities: dict[str, float] = {}
        total_priority_score = 0.0

        for workflow in workflows:
            workflow_id = workflow.get("name", "unnamed_workflow")
            priority = workflow.get("metadata", {}).get("coordination", {}).get("priority", 2)
            priority_multiplier = coordination_budget.priority_multipliers.get(priority, 1.0)  # type: ignore[arg-type]
            complexity_factor = self._estimate_workflow_complexity(workflow)
            score = float(priority_multiplier) * float(complexity_factor)
            workflow_priorities[workflow_id] = score
            total_priority_score += score

        if total_priority_score <= 0:
            # Distribute evenly
            per = remaining_budget / max(len(workflows), 1)
            return {wf.get("name", "unnamed_workflow"): per for wf in workflows}

        for workflow_id, score in workflow_priorities.items():
            share = (score / total_priority_score) * remaining_budget
            allocations[workflow_id] = min(share, coordination_budget.per_workflow_budget)
        return allocations

    def get_coordination_summary(self, coordination_id: str) -> dict[str, Any]:
        workflows = defaultdict(lambda: {
            "total_tokens": 0,
            "total_cost": 0.0,
            "operations": [],
            "phases": defaultdict(lambda: {"tokens": 0, "cost": 0.0, "operations": 0}),
        })
        total_cost = 0.0
        total_tokens = 0
        total_operations = 0

        for usage in self.storage.iter_by_coordination(coordination_id):
            workflow_id = usage.get("workflow_id", "unknown")
            phase_id = usage.get("phase_id")
            workflows[workflow_id]["total_tokens"] += int(usage.get("tokens_used", 0))
            workflows[workflow_id]["total_cost"] += float(usage.get("estimated_cost", 0.0))
            workflows[workflow_id]["operations"].append(usage)
            if phase_id:
                workflows[workflow_id]["phases"][phase_id]["tokens"] += int(usage.get("tokens_used", 0))
                workflows[workflow_id]["phases"][phase_id]["cost"] += float(usage.get("estimated_cost", 0.0))
                workflows[workflow_id]["phases"][phase_id]["operations"] += 1
            total_cost += float(usage.get("estimated_cost", 0.0))
            total_tokens += int(usage.get("tokens_used", 0))
            total_operations += 1

        workflows_dict = {}
        for workflow_id, data in workflows.items():
            workflows_dict[workflow_id] = {
                "total_tokens": data["total_tokens"],
                "total_cost": data["total_cost"],
                "operations_count": len(data["operations"]),
                "phases": dict(data["phases"]),
            }
        return {
            "coordination_id": coordination_id,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_operations": total_operations,
            "workflows": workflows_dict,
            "average_cost_per_workflow": total_cost / max(len(workflows_dict), 1),
            "timestamp": datetime.now().isoformat(),
        }

    def get_workflow_cost_summary(
        self, workflow_id: str, coordination_id: Optional[str] = None
    ) -> WorkflowCostSummary:
        summary = WorkflowCostSummary(workflow_id=workflow_id)
        successful_ops = 0
        total_ops = 0

        for usage in self.storage.iter_all():
            if usage.get("workflow_id") != workflow_id:
                continue
            if coordination_id is not None and usage.get("coordination_id") != coordination_id:
                continue
            summary.total_tokens += int(usage.get("tokens_used", 0))
            summary.total_cost += float(usage.get("estimated_cost", 0.0))
            total_ops += 1
            if usage.get("success", True):
                successful_ops += 1

            phase_id = usage.get("phase_id")
            if phase_id:
                if phase_id not in summary.phases:
                    summary.phases[phase_id] = {"tokens": 0, "cost": 0.0, "operations": 0}
                summary.phases[phase_id]["tokens"] += int(usage.get("tokens_used", 0))
                summary.phases[phase_id]["cost"] += float(usage.get("estimated_cost", 0.0))
                summary.phases[phase_id]["operations"] += 1

        summary.operations_count = total_ops
        summary.success_rate = successful_ops / max(total_ops, 1)
        return summary

    def check_coordination_budget(
        self, coordination_id: str, coordination_budget: CoordinationBudget
    ) -> dict[str, Any]:
        summary = self.get_coordination_summary(coordination_id)
        status = {
            "coordination_id": coordination_id,
            "total_budget": coordination_budget.total_budget,
            "emergency_reserve": coordination_budget.emergency_reserve,
            "available_budget": coordination_budget.total_budget - coordination_budget.emergency_reserve,
            "used_budget": summary["total_cost"],
            "remaining_budget": coordination_budget.total_budget - summary["total_cost"],
            "budget_utilization": summary["total_cost"] / max(coordination_budget.total_budget, 1e-9),
            "within_budget": summary["total_cost"] <= coordination_budget.total_budget,
            "emergency_triggered": summary["total_cost"] > (coordination_budget.total_budget - coordination_budget.emergency_reserve),
            "workflows": {},
        }
        for wf_id, wf_data in summary["workflows"].items():
            allocated = coordination_budget.workflow_allocations.get(wf_id, coordination_budget.per_workflow_budget)
            status["workflows"][wf_id] = {
                "allocated": allocated,
                "used": wf_data["total_cost"],
                "remaining": allocated - wf_data["total_cost"],
                "utilization": (wf_data["total_cost"] / allocated) if allocated > 0 else 0,
                "within_budget": wf_data["total_cost"] <= allocated,
            }
        return status

    def optimize_remaining_allocation(
        self,
        coordination_id: str,
        remaining_workflows: list[str],
        coordination_budget: CoordinationBudget,
    ) -> dict[str, float]:
        current_summary = self.get_coordination_summary(coordination_id)
        remaining_budget = coordination_budget.total_budget - float(current_summary["total_cost"])
        if remaining_budget <= coordination_budget.emergency_reserve:
            per = coordination_budget.emergency_reserve / max(len(remaining_workflows), 1)
            return {wid: per for wid in remaining_workflows}
        available = remaining_budget - coordination_budget.emergency_reserve
        per = available / max(len(remaining_workflows), 1)
        return {wid: min(per, coordination_budget.per_workflow_budget) for wid in remaining_workflows}

    def _estimate_workflow_complexity(self, workflow: dict[str, Any]) -> float:
        complexity = 1.0
        steps = workflow.get("steps", [])
        phases = workflow.get("phases", [])
        if phases:
            complexity += len(phases) * 0.2
            if any(phase.get("role") == "ipt" for phase in phases):
                complexity += 0.5
        elif steps:
            complexity += len(steps) * 0.1
        ai_steps = 0
        for step in steps:
            actor = step.get("actor", "")
            if "ai_" in actor or actor in ["claude", "gemini", "aider"]:
                ai_steps += 1
        complexity += ai_steps * 0.3
        coordination = workflow.get("metadata", {}).get("coordination", {})
        file_scope = coordination.get("file_scope", [])
        if len(file_scope) > 10:
            complexity += 0.4
        return complexity

    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        # Domain layer has no direct file operations; noop in domain
        return 0

