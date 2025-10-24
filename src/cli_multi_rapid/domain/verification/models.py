from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class GateResult:
    """Result of a quality gate check."""

    gate_name: str
    passed: bool
    message: str
    details: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.details is None:
            self.details = {}

