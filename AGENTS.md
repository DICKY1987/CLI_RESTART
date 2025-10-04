# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/cli_multi_rapid` (CLI orchestrator). Supporting libs: `src/integrations`, `src/websocket`, `src/observability`, `src/idempotency`.
- Workflows: `.ai/workflows/` (YAML), Schemas: `.ai/schemas/` (JSON).
- Tests: `tests/` (unit/integration/benchmarks). Docs: `docs/`. VS Code extension: `vscode-extension/`. Config: `config/`. Scripts: `scripts/`.

## Build, Test, and Development Commands
- Setup (dev): `pip install -e .[dev]` and `pre-commit install`.
- Quick checks: `task ci` (ruff, mypy, pytest with coverage gate).
- Run tests: `pytest -q --cov=src --cov-fail-under=85`.
- Local compose smoke: `docker compose -f config/docker-compose.yml up -d` then `python scripts/healthcheck.py http://localhost:5055/health`.
- Orchestrator dry-run: `cli-orchestrator run .ai/workflows/CODE_QUALITY.yaml --dry-run`.
- Extension CI: `(cd vscode-extension && npm ci && npm run ci)`.

## Coding Style & Naming Conventions
- Python 3.9+. Use 4-space indents and type hints.
- Naming: snake_case (modules/functions), PascalCase (classes).
- Lint/format/type: `ruff`, `black`, `isort`, `mypy`. Run via `task ci`.
- Keep changes minimal, deterministic, and schema-driven.

## Testing Guidelines
- Framework: `pytest`; coverage gate ≥ 85% (CI enforced).
- Naming: files `tests/test_*.py`, classes `Test*`, functions `test_*`.
- Contract tests: `tests/contracts/` (see `docs/contracts/INTERFACE_GUIDE.md`).

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (e.g., `feat:`, `fix:`, `chore:`) with concise scope.
- Before PR: run `task ci` and the compose smoke test; ensure no secrets in diffs.
- PRs include: clear description, linked issues/milestones, and artifacts (coverage output, logs, screenshots when relevant).

## Security & Configuration Tips
- Never commit secrets. Pre-commit runs `detect-secrets` (baseline: `.secrets.baseline`).
- Copy `.env.template` to `.env` locally; never push `.env`.
- Prefer deterministic tooling and avoid networked calls in tests.

## Agent-Specific Instructions
- Validate workflows with dry-runs, respect schemas, and keep outputs reproducible.
- Obey this AGENTS.md across the repo. Defer to more specific AGENTS.md files in subfolders when present.
- Propose small, reviewable changes; keep style consistent with existing code.
