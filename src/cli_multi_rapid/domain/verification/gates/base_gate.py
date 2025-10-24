from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..models import GateResult


class BaseGate(Protocol):
    def check(self, gate_config: dict, artifacts_dir: Path) -> GateResult:  # pragma: no cover - interface
        ...

