from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional, Set

from .dependency_graph import has_cycle


@dataclass
class DeadlockReport:
    cycle_detected: bool
    timed_out: Set[str]


def detect_deadlock(graph: Dict[str, Set[str]], start_times: Dict[str, float], timeout_seconds: float) -> DeadlockReport:
    cycle = has_cycle(graph)
    now = time.time()
    timed_out = {k for k, t in start_times.items() if (now - t) > timeout_seconds}
    return DeadlockReport(cycle_detected=cycle, timed_out=timed_out)

