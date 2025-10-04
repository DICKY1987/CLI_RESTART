# Determinism Architecture

This orchestrator prioritizes deterministic execution. The Deterministic Engine provides:

- Step analysis to detect likely non-deterministic patterns (random, time, uuid, entropy sources).
- Enforcement modes: `strict` (block) or `warn` (log only). Configure via `DETERM_MODE` env or per-step `policy.determinism_mode`.
- Environment hints applied at execution: `TZ=UTC`, `LC_ALL=C.UTF-8`, `LANG=C.UTF-8`, `PYTHONHASHSEED=0`.

Integration points:
- The workflow runner enforces determinism before adapter execution and applies environment hints.
- Prefer deterministic adapters when `prefer_deterministic: true` is set on steps/workflows.

Common violations:
- Parameters or commands using `random`, `time/date`, `uuid`, or `/dev/urandom`.
- Routing AI adapters while `prefer_deterministic` is enabled.

Resolution:
- Replace non-deterministic inputs, seed appropriately, or switch to deterministic tools.
- Downgrade to `warn` mode if strict enforcement is not feasible for a specific step.
