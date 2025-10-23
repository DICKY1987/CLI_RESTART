from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.idempotency import storage


@dataclass
class FakeTime:
    current: float = 0.0

    def time(self) -> float:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current += seconds


@pytest.fixture
def reset_store(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "_store", None)
    monkeypatch.setattr(storage, "_cache", {})


def test_make_step_key_is_deterministic(reset_store: None) -> None:
    step_one = {
        "id": "alpha",
        "actor": "planner",
        "with": {"files": "src/**/*.py", "args": {"b": 1, "a": 2}},
    }
    step_two = {
        "with": {"args": {"a": 2, "b": 1}, "files": "src/**/*.py"},
        "actor": "planner",
        "id": "alpha",
    }

    assert storage.make_step_key(step_one) == storage.make_step_key(step_two)


def test_make_step_key_prefers_override(reset_store: None) -> None:
    step = {
        "id": "beta",
        "actor": "builder",
        "with": {"files": "src/**/*.py"},
    }

    default_key = storage.make_step_key(step)
    override_key = storage.make_step_key(step, files="docs/**/*.md")

    assert default_key != override_key


def test_get_cached_respects_ttl(monkeypatch: pytest.MonkeyPatch, reset_store: None) -> None:
    fake_time = FakeTime(current=100.0)
    monkeypatch.setattr(storage, "time", fake_time)

    payload = {"result": "ok"}
    storage.set_cached("step-1", payload, ttl_seconds=5)

    assert storage.get_cached("step-1") == payload

    fake_time.advance(10)

    assert storage.get_cached("step-1") is None
    assert "step-1" not in storage._cache


def test_get_store_returns_memory_store_when_no_redis(
    monkeypatch: pytest.MonkeyPatch, reset_store: None
) -> None:
    monkeypatch.delenv("REDIS_URL", raising=False)

    store = storage.get_store()

    assert isinstance(store, storage.MemoryStore)
    assert storage.get_store() is store


def test_get_store_falls_back_on_redis_error(
    monkeypatch: pytest.MonkeyPatch, reset_store: None
) -> None:
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    class FailingRedisStore:
        def __init__(self, url: str) -> None:  # pragma: no cover - __init__ only
            raise RuntimeError("redis down")

    monkeypatch.setattr(storage, "RedisStore", FailingRedisStore)

    store = storage.get_store()

    assert isinstance(store, storage.MemoryStore)
