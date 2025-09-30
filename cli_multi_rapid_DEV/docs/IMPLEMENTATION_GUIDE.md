# Implementation Guide

This guide explains the integrated Git automation and deterministic pipeline.

## Git Workflow Automation

- repo_flow scripts: `.det-tools/scripts/repo_flow.sh` and `.det-tools/scripts/repo_flow.ps1`
- Hooks: `.githooks/pre-commit`, `.githooks/pre-push` (install via `bash ./.det-tools/scripts/install_hooks.sh`)
- Repo hygiene CI: `.github/workflows/repo-hygiene.yml`

### Typical Flow

1. `repo_flow begin` to create/switch to a workstream branch `ws/YYYY-MM-DD-<tool>-<topic>`
2. Make changes
3. `repo_flow save "message"` to commit/push and ensure a PR exists with auto-merge label
4. Let scheduled hygiene workflow rebase and clean

## Deterministic Pipeline

- Deterministic wrapper: `scripts/deterministic.sh`
- Conflict detection: `tools/detect_conflicts.py`
- Manifest validation: `tools/validate_manifests.py`
- Lockfile: `agentic/agentic.lock.json` (schema: `schemas/agentic_lock.schema.json`)
- Adaptive config: `.ai/parallelization_config.yaml`

### Deterministic Wrapper Usage

- Example: `bash scripts/deterministic.sh pytest -q`
- Writes state to `.ai/state.json` and logs to `.ai/logs/<RUN_ID>/`
- Enforces a simple lock via `.ai/pipeline.lock`

### Conflict Detection

- Example: `python tools/detect_conflicts.py C:\\path\\to\\combined_plan.json --output /tmp/analysis.json`
- Outputs JSON with conflicts, safe parallel groups, and sequential constraints

## CI Pipeline

- Quality: ruff, mypy, formatting check
- Tests: matrix across OS and Python versions (cov ≥ 85)
- Validate: JSON manifests via `jsonschema`
- Integration: runs deterministic wrapper and verifies artifacts

## Repository Settings

See `.github/REPO_SETTINGS.md` for branch protection and secrets guidance.

