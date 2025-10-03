"""Git Snapshot Contract - Comprehensive Git state capture for workflow auditing."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class GitStatus(str, Enum):
    """Git repository status."""
    clean = "clean"
    dirty = "dirty"
    error = "error"


class GitSnapshot(BaseModel):
    """Comprehensive Git state snapshot for workflow execution tracking."""

    branch: str = Field(..., description="Current Git branch")
    commit_hash: str = Field(..., description="Short commit hash (8 chars)")
    last_commit_message: str = Field(..., description="Last commit message")
    last_commit_time: str = Field(..., description="Last commit time (human-readable)")
    recent_commits: int = Field(default=0, description="Number of commits in lookback window")
    unpushed_commits: int = Field(default=0, description="Number of unpushed commits")
    uncommitted_files: List[str] = Field(default_factory=list, description="List of uncommitted file paths")
    status: GitStatus = Field(..., description="Repository status")
    timestamp: str = Field(..., description="Snapshot timestamp (ISO 8601)")


class GitSessionStatistics(BaseModel):
    """Git statistics for a workflow session."""

    commits_since_start: int = Field(default=0, description="Commits created during session")
    unpushed: int = Field(default=0, description="Unpushed commits")
    has_uncommitted: bool = Field(default=False, description="Has uncommitted changes")
    final_branch: str = Field(..., description="Final branch name")
    final_commit: str = Field(..., description="Final commit hash (short)")


__all__ = ["GitSnapshot", "GitStatus", "GitSessionStatistics"]
