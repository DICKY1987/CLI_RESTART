import datetime as _dt
from dataclasses import asdict
from typing import Iterable

from src.cli_multi_rapid.domain.cost.tracker import CostTracker
from src.cli_multi_rapid.domain.cost.models import BudgetLimit, CoordinationBudget
from src.cli_multi_rapid.domain.cost.calculator import CostCalculator


class _MemoryStorage:
    def __init__(self) -> None:
        self.records: list[dict] = []

    # CostStoragePort methods
    def save(self, record: dict) -> None:
        self.records.append(record)

    def iter_all(self) -> Iterable[dict]:
        return iter(list(self.records))

    def iter_by_date(self, target_date: _dt.date) -> Iterable[dict]:
        iso = target_date.isoformat()
        return (r for r in self.records if str(r.get("timestamp", ""))[:10] == iso)

    def iter_by_coordination(self, coordination_id: str) -> Iterable[dict]:
        return (r for r in self.records if r.get("coordination_id") == coordination_id)


class _FixedCalculator(CostCalculator):
    def __init__(self, per_token: float) -> None:
        self._val = per_token

    def per_token(self, model: str) -> float:  # type: ignore[override]
        return self._val


def test_record_and_daily_usage_counts():
    storage = _MemoryStorage()
    calc = _FixedCalculator(0.001)
    tracker = CostTracker(storage=storage, calculator=calc)

    # Record two operations today
    tracker.record_usage("op1", 100, model="any")
    tracker.record_usage("op2", 50, model="any")

    daily = tracker.get_daily_usage()
    assert daily["total_tokens"] == 150
    # 100*0.001 + 50*0.001
    assert abs(daily["total_cost"] - 0.15) < 1e-9
    assert daily["operation_count"] == 2


def test_allocate_budget_priority_distribution():
    storage = _MemoryStorage()
    tracker = CostTracker(storage=storage)

    workflows = [
        {"name": "wf-low", "metadata": {"coordination": {"priority": 1}}, "steps": [{"actor": "a"}]},
        {"name": "wf-high", "metadata": {"coordination": {"priority": 5}}, "steps": [{"actor": "a"}]},
    ]
    budget = CoordinationBudget(total_budget=10.0, per_workflow_budget=10.0, emergency_reserve=0.0)
    alloc = tracker.allocate_budget(workflows, budget)
    assert set(alloc.keys()) == {"wf-low", "wf-high"}
    assert alloc["wf-high"] > alloc["wf-low"]


def test_check_budget_limits_warn_and_bounds():
    storage = _MemoryStorage()
    tracker = CostTracker(storage=storage)

    # No records yet; spending tokens should reflect projected cost
    result = tracker.check_budget_limits(BudgetLimit(daily_cost_limit=0.002, warn_threshold=0.5), tokens_to_spend=150)
    # projected_cost uses 1e-5 fallback per token => 0.0015
    assert result["within_daily_cost_limit"] is True
    assert result["warn_if_over"] is True

