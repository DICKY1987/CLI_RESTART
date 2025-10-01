from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Protocol, Iterator


class LockBackend(Protocol):
    def acquire(self, name: str, *, timeout: float | None = None, ttl: float | None = None, retry_interval: float = 0.1) -> bool:
        """Acquire a distributed lock by name. Returns True on success."""

    def release(self, name: str) -> None:
        """Release a previously acquired lock."""


@contextmanager
def lock(backend: LockBackend, name: str, *, timeout: float | None = None, ttl: float | None = None, retry_interval: float = 0.1) -> Iterator[None]:
    start = time.time()
    while True:
        if backend.acquire(name, timeout=timeout, ttl=ttl, retry_interval=retry_interval):
            break
        if timeout is not None and (time.time() - start) >= timeout:
            raise TimeoutError(f"Timed out acquiring lock {name}")
        time.sleep(retry_interval)
    try:
        yield
    finally:
        try:
            backend.release(name)
        except Exception:
            pass

