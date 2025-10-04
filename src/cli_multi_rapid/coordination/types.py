"""Coordination type definitions used by routing and planning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class ScopeMode(str, Enum):
    EXCLUSIVE = "exclusive"
    SHARED = "shared"


@dataclass
class FileClaim:
    workflow_id: str
    file_patterns: List[str]
    mode: ScopeMode = ScopeMode.EXCLUSIVE


@dataclass
class ScopeConflict:
    claim_a: FileClaim
    claim_b: FileClaim
    conflicting_files: List[str]
