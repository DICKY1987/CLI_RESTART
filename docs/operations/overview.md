# Operations Guide: No-Friction Tooling and Cost Registry

This guide summarizes the recommended flow for a conflict-free setup and introduces the cost/limits single source of truth (SSOT).

## Setup Flow

- Discovery → Config → Verify → Dry-Run
  - Configure tools in `config/tool_adapters.yaml` (this repo ships a baseline).
  - Prepare your shell session:
    - PowerShell: `./scripts/setup_tool_environment.ps1`
      - Adds `.venv/Scripts` to `PATH` (if present)
      - Applies environment variables from `tool_config.*.env`
      - Prints resolved tool locations/versions
  - Verify tools with the orchestrator:
    - `cli-orchestrator tools doctor`
    - `cli-orchestrator tools list`
  - Validate and dry-run workflows:
    - `cli-orchestrator run .ai/workflows/CODE_QUALITY.yaml --dry-run`

## Cost Registry (SSOT)

- Canonical registry: `config/cost_registry.yaml`
  - Schema: `.ai/schemas/cost_registry.schema.json`
  - Validated in workflow `Code Quality Check` via a `yaml_schema_valid` gate.
  - Tracks per-model prices (per 1k tokens) and RPM/TPM limits.

- CostTracker integration
  - `src/cli_multi_rapid/cost_tracker.py` consumes the registry if present.
  - Falls back to conservative defaults when missing.

## CI/Quality

- Run quality checks locally:
  - `cli-orchestrator quality run --paths src,tests`
  - `pytest -q --cov=src --cov-fail-under=85`

## Notes

- Keep changes deterministic and schema-driven.
- Prefer orchestrator adapters over calling tools directly.

