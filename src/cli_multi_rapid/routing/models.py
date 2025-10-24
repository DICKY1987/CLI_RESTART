from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class RoutingDecision:
    """Result of routing decision for a workflow step."""

    adapter_name: str
    adapter_type: str  # "deterministic" or "ai"
    reasoning: str
    estimated_tokens: int = 0
    complexity_score: float = 0.0
    confidence: float = 1.0
    performance_hint: Optional[str] = None


@dataclass
class ParallelRoutingPlan:
    """Plan for parallel execution of multiple steps."""

    routing_decisions: list[tuple[dict[str, Any], RoutingDecision]]
    execution_groups: list[list[int]]  # Groups of step indices that can run in parallel
    total_estimated_cost: int = 0
    conflicts: list[Any] | None = None
    resource_allocation: dict[str, list[int]] | None = None  # adapter_name -> step indices

    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []
        if self.resource_allocation is None:
            self.resource_allocation = {}


@dataclass
class ComplexityAnalysis:
    """Analysis of step complexity for routing decisions."""

    score: float  # 0.0 (simple) to 1.0 (complex)
    factors: dict[str, float]  # Individual complexity factors
    file_count: int = 0
    estimated_file_size: int = 0  # bytes
    operation_type: str = "unknown"
    deterministic_confidence: float = 0.0


@dataclass
class AllocationPlan:
    """Resource allocation plan for coordinated workflows."""

    assignments: dict[str, dict[str, Any]]  # step_id -> allocation info
    total_estimated_cost: int = 0
    estimated_usd_cost: float = 0.0
    within_budget: bool = True
    parallel_groups: list[list[str]] | None = None

    def __post_init__(self):
        if self.parallel_groups is None:
            self.parallel_groups = []

