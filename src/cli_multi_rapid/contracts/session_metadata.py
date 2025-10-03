"""Session Metadata Contract - Workflow session tracking and metrics."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Workflow session status."""
    active = "active"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class SessionMetadata(BaseModel):
    """Metadata for workflow execution session."""

    session_id: str = Field(..., description="Unique session identifier")
    workflow_name: str = Field(..., description="Name of the workflow")
    started_at: str = Field(..., description="Session start timestamp (ISO 8601)")
    ended_at: Optional[str] = Field(None, description="Session end timestamp (ISO 8601)")
    pid: int = Field(..., description="Process ID of the session")
    status: SessionStatus = Field(default=SessionStatus.active, description="Current session status")
    commits_count: int = Field(default=0, description="Number of commits created in session")
    unpushed_count: int = Field(default=0, description="Number of unpushed commits")


__all__ = ["SessionMetadata", "SessionStatus"]
