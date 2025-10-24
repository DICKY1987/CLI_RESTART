from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class TokenUsage:
    """Records token usage for a single operation."""

    timestamp: str
    operation: str
    tokens_used: int
    estimated_cost: float
    model: str = "unknown"
    success: bool = True
    workflow_id: Optional[str] = None
    coordination_id: Optional[str] = None
    phase_id: Optional[str] = None
    adapter_name: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BudgetLimit:
    """Budget enforcement configuration."""

    daily_token_limit: int = 100000
    daily_cost_limit: float = 10.0
    per_workflow_limit: int = 50000
    warn_threshold: float = 0.8


@dataclass
class CoordinationBudget:
    """Budget configuration for coordinated workflows."""

    total_budget: float = 25.0
    per_workflow_budget: float = 10.0
    emergency_reserve: float = 5.0
    workflow_allocations: dict[str, float] | None = None
    priority_multipliers: dict[int, float] | None = None

    def __post_init__(self) -> None:
        if self.workflow_allocations is None:
            self.workflow_allocations = {}
        if self.priority_multipliers is None:
            # Higher priority workflows get more budget
            self.priority_multipliers = {
                1: 0.5,   # Low priority
                2: 1.0,   # Normal priority
                3: 1.5,   # High priority
                4: 2.0,   # Critical priority
                5: 3.0,   # Emergency priority
            }


@dataclass
class WorkflowCostSummary:
    """Summary of costs for a workflow."""

    workflow_id: str
    total_tokens: int = 0
    total_cost: float = 0.0
    operations_count: int = 0
    success_rate: float = 0.0
    budget_allocated: float = 0.0
    budget_used: float = 0.0
    budget_remaining: float = 0.0
    phases: dict[str, dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if self.phases is None:
            self.phases = {}
        self.budget_remaining = self.budget_allocated - self.budget_used

