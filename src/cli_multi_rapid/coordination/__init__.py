"""Coordination utilities for orchestrator runtime."""

from enum import Enum

from .coordinator import (
    CoordinationMode,
    CoordinationPlan,
    FileScopeManager,
    WorkflowCoordinator,
)


class ScopeMode(str, Enum):
    """File scope coordination modes."""

    EXCLUSIVE = "exclusive"
    SHARED = "shared"


__all__ = [
    "CoordinationMode",
    "CoordinationPlan",
    "WorkflowCoordinator",
    "FileScopeManager",
    "ScopeMode",
]
