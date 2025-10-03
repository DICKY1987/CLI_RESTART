"""Contract models for CLI ↔ Extension interactions."""

from .git_snapshot import GitSessionStatistics, GitSnapshot, GitStatus
from .models import (
    EventType,
    Phase,
    WorkflowAccepted,
    WorkflowError,
    WorkflowEvent,
    WorkflowStartRequest,
    WorkflowStatus,
)
from .session_metadata import SessionMetadata, SessionStatus

__all__ = [
    # Legacy models
    "Phase",
    "WorkflowStartRequest",
    "WorkflowAccepted",
    "WorkflowError",
    "WorkflowStatus",
    "EventType",
    "WorkflowEvent",
    # Git snapshot contracts
    "GitSnapshot",
    "GitStatus",
    "GitSessionStatistics",
    # Session metadata contracts
    "SessionMetadata",
    "SessionStatus",
]
