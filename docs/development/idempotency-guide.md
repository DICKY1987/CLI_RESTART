# Idempotency Guide

The orchestrator enforces idempotency for steps so the same inputs yield the same outcome without re-executing work.

Core APIs (`src/idempotency/storage.py`):
- `make_step_key(step, files)` — produce a deterministic key from a step.
- `get_store()` — obtain the current store (memory by default; Redis if `REDIS_URL` is set).
- `get_cached(key)` / `set_cached(key, value, ttl)` — cache full adapter results with TTL.

Behavior in the runner:
- Before execution: if `with.force` is not set and a cached result exists, the result is returned immediately.
- If a key has been seen but no cache is present, the step is skipped with a note.
- After successful execution: the full result is cached and the key is marked seen.

Configuration:
- `IDEMPOTENCY_TTL_SECONDS` — cache TTL (default: 86400 seconds).
- `with.force: true` — bypass idempotency for a specific step.

Notes:
- Redis backend uses `idem:<key>` for seen flags and `idemc:<key>` for cached payloads.
- Memory backend maintains an in-process TTL cache suitable for tests and local runs.
