"""Backward-compatibility shim for Router import path.

Router and routing dataclasses have moved to `cli_multi_rapid.routing`.
This module re-exports them to avoid breaking existing imports.
"""

from .routing.router import Router  # noqa: F401
from .routing.models import (  # noqa: F401
    AllocationPlan,
    ComplexityAnalysis,
    ParallelRoutingPlan,
    RoutingDecision,
)

__all__ = [
    "Router",
    "RoutingDecision",
    "ParallelRoutingPlan",
    "ComplexityAnalysis",
    "AllocationPlan",
]

