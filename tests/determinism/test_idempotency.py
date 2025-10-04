import os
import time

from src.idempotency.storage import get_cached, get_store, make_step_key, set_cached


def test_make_step_key_stable():
    step = {"id": "s1", "actor": "demo", "with": {"a": 1, "b": 2}}
    k1 = make_step_key(step, files="src/*.py")
    k2 = make_step_key({"actor": "demo", "id": "s1", "with": {"b": 2, "a": 1}}, files="src/*.py")
    assert k1 == k2


def test_memory_store_cache_roundtrip():
    os.environ.pop("REDIS_URL", None)
    store = get_store()
    step = {"id": "s2", "actor": "demo", "with": {"x": 3}}
    key = make_step_key(step)
    assert store.seen(key) is False
    # set cache
    data = {"success": True, "output": "ok"}
    set_cached(key, data, 2)
    cached = get_cached(key)
    assert cached == data
    # expiry
    time.sleep(2)
    assert get_cached(key) is None
