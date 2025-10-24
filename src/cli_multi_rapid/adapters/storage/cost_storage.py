from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable

from .cost_storage_port import CostStoragePort


class FileCostStorage(CostStoragePort):
    """File-based cost storage using JSONL in `logs/token_usage.jsonl`."""

    def __init__(self, logs_dir: str | Path = "logs") -> None:
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.logs_dir / "token_usage.jsonl"

    def save(self, record: dict) -> None:  # type: ignore[override]
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.usage_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def iter_all(self) -> Iterable[dict]:  # type: ignore[override]
        if not self.usage_file.exists():
            return iter(())
        def gen():
            with open(self.usage_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except Exception:
                        # skip malformed lines
                        continue
        return gen()

    def iter_by_date(self, target_date: date) -> Iterable[dict]:  # type: ignore[override]
        iso = target_date.isoformat()
        return (rec for rec in self.iter_all() if str(rec.get("timestamp", ""))[:10] == iso)

    def iter_by_coordination(self, coordination_id: str) -> Iterable[dict]:  # type: ignore[override]
        return (rec for rec in self.iter_all() if rec.get("coordination_id") == coordination_id)

