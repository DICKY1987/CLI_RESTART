from __future__ import annotations

import builtins
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class DLQEntry:
    workflow: str
    reason: str
    timestamp: str
    retries: int = 0


class FileDLQ:
    def __init__(self, path: str | Path = ".data/dlq.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, workflow: str, reason: str) -> None:
        items = self._read()
        items.append(
            DLQEntry(workflow=workflow, reason=reason, timestamp=datetime.now(timezone.utc).isoformat())
        )
        self._write(items)

    def list(self) -> builtins.list[DLQEntry]:
        return self._read()

    def _read(self) -> builtins.list[DLQEntry]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text("utf-8"))
        return [DLQEntry(**x) for x in raw]

    def _write(self, items: builtins.list[DLQEntry]) -> None:
        self.path.write_text(json.dumps([asdict(x) for x in items], indent=2), encoding="utf-8")

