#!/usr/bin/env python3
"""
Idempotency storage backends and helpers.

Provides a simple in-memory store by default and optional Redis backend
if `REDIS_URL` env var is set and redis-py is available.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Protocol


class IdempotencyStore(Protocol):
    def seen(self, key: str) -> bool: ...
    def mark(self, key: str) -> None: ...


@dataclass
class MemoryStore:
    keys: set[str]

    def __init__(self) -> None:
        self.keys = set()

    def seen(self, key: str) -> bool:
        return key in self.keys

    def mark(self, key: str) -> None:
        self.keys.add(key)


class RedisStore:
    def __init__(self, url: str) -> None:
        import redis  # type: ignore

        self.r = redis.from_url(url)

    def seen(self, key: str) -> bool:
        return bool(self.r.exists(f"idem:{key}"))

    def mark(self, key: str) -> None:
        self.r.set(f"idem:{key}", 1)


_store: IdempotencyStore | None = None
_cache: dict[str, tuple[float, dict]] = {}


def get_store() -> IdempotencyStore:
    global _store
    if _store is not None:
        return _store
    url = os.getenv("REDIS_URL")
    if url:
        try:
            _store = RedisStore(url)
            return _store
        except Exception:
            pass
    _store = MemoryStore()
    return _store


def make_step_key(step: dict, files: str | None = None) -> str:
    """Create a deterministic idempotency key from a step and files pattern."""
    basis = {
        "id": step.get("id"),
        "actor": step.get("actor"),
        "with": step.get("with") or {},
        "files": files or step.get("with", {}).get("files"),
    }
    raw = json.dumps(basis, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def set_cached(key: str, data: dict, ttl_seconds: int) -> None:
    """Store a cached result with a TTL in seconds."""
    expires_at = time.time() + max(0, int(ttl_seconds))
    _cache[key] = (expires_at, data)


def get_cached(key: str) -> dict | None:
    """Retrieve a cached result if not expired; otherwise return None."""
    entry = _cache.get(key)
    if not entry:
        return None
    expires_at, data = entry
    if time.time() >= expires_at:
        # Expired; clean up and return None
        _cache.pop(key, None)
        return None
    return data
