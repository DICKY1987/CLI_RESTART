from __future__ import annotations

import os
import time
from typing import Optional

from .locks import LockBackend


class RedisLockBackend(LockBackend):
    def __init__(self, url: Optional[str] = None) -> None:
        try:
            import redis  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("redis package not available") from e
        self._redis = redis.Redis.from_url(url or os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    def acquire(self, name: str, *, timeout: float | None = None, ttl: float | None = None, retry_interval: float = 0.1) -> bool:
        expires_ms = int((ttl or 10.0) * 1000)
        start = time.time()
        while True:
            ok = self._redis.set(name, "1", nx=True, px=expires_ms)
            if ok:
                return True
            if timeout is not None and (time.time() - start) >= timeout:
                return False
            time.sleep(retry_interval)

    def release(self, name: str) -> None:
        try:
            self._redis.delete(name)
        except Exception:
            pass

