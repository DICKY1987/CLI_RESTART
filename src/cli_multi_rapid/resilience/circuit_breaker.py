from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class CircuitState:
    failures: int = 0
    opened_at: float | None = None


class SimpleCircuitBreaker:
    def __init__(self, *, failure_threshold: int = 5, reset_timeout: float = 10.0) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = CircuitState()

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if self.is_open():
            raise RuntimeError("circuit_open")
        try:
            result = func(*args, **kwargs)
            self.state.failures = 0
            self.state.opened_at = None
            return result
        except Exception:
            self.state.failures += 1
            if self.state.failures >= self.failure_threshold:
                self.state.opened_at = time.time()
            raise

    def is_open(self) -> bool:
        if self.state.opened_at is None:
            return False
        if (time.time() - self.state.opened_at) >= self.reset_timeout:
            # half-open: allow one try
            self.state.opened_at = None
            self.state.failures = 0
            return False
        return True

