from __future__ import annotations

import time
from dataclasses import dataclass

from .dependency_graph import has_cycle


@dataclass
class DeadlockReport:
    cycle_detected: bool
    timed_out: set[str]


def detect_deadlock(graph: dict[str, set[str]], start_times: dict[str, float], timeout_seconds: float) -> DeadlockReport:
    cycle = has_cycle(graph)
    now = time.time()
    timed_out = {k for k, t in start_times.items() if (now - t) > timeout_seconds}
    return DeadlockReport(cycle_detected=cycle, timed_out=timed_out)

