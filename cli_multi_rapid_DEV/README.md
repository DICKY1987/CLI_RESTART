# CLI Multi-Rapid: Git Automation + Deterministic Pipeline

This repository integrates two complementary systems:

- Git Workflow Automation: repo_flow CLI, safety hooks, and repo hygiene CI.
- Deterministic Pipeline: deterministic execution wrapper, conflict detection, manifest validation, adaptive config, and CI gates.

## Quick Start

- Install hooks: `bash ./.det-tools/scripts/install_hooks.sh`
- Begin work: `./repo_flow begin` (or PowerShell: `pwsh ./.det-tools/scripts/repo_flow.ps1 begin`)
- Save work and open/refresh PR: `./repo_flow save "message"`
- Deterministic run: `bash scripts/deterministic.sh echo "hello"`

## CI Workflows

- Repo Hygiene: `.github/workflows/repo-hygiene.yml`
- Production CI: `.github/workflows/ci.yml`

## Tools

- Conflict detector: `tools/detect_conflicts.py`
- Manifest validator: `tools/validate_manifests.py`
- Lockfile (tools): `agentic/agentic.lock.json` (schema: `schemas/agentic_lock.schema.json`)
- Adaptive config: `.ai/parallelization_config.yaml`

See `docs/IMPLEMENTATION_GUIDE.md` for full details.

