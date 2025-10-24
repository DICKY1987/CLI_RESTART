from __future__ import annotations

from datetime import date
from typing import Iterable, Protocol


class CostStoragePort(Protocol):
    """Protocol for cost storage backends (JSONL, DB, etc.)."""

    def save(self, record: dict) -> None:
        """Append a single usage record (serialized dict)."""

    def iter_all(self) -> Iterable[dict]:
        """Iterate all stored usage records as dicts."""

    def iter_by_date(self, target_date: date) -> Iterable[dict]:
        """Iterate usage records for a specific date."""

    def iter_by_coordination(self, coordination_id: str) -> Iterable[dict]:
        """Iterate usage records for a coordination session."""

