Scripts Index and De-duplication Guide

- Purpose: provide one canonical entrypoint per task, reduce duplication, and document remaining scripts for discoverability.

Conventions
- Canonical entrypoint: prefer a single script per task. Platform shims may exist as thin wrappers only.
- Make integration: when possible, use `make` targets that call scripts under the hood.
- Wrappers: legacy paths remain as wrappers forwarding to the canonical script to avoid breaking callers.

Canonicalization Decisions
- Git deterministic merge utilities
  - Canonical: `tools/atomic-workflow-system/GIT/deterministic_merge_system/scripts/AutoMerge-Workstream.ps1`
  - Canonical: `tools/atomic-workflow-system/GIT/deterministic_merge_system/scripts/PreFlight-Check.ps1`
  - Canonical: `tools/atomic-workflow-system/GIT/deterministic_merge_system/scripts/setup-merge-drivers.ps1`
  - Legacy wrappers kept at:
    - `scripts/AutoMerge-Workstream.ps1`
    - `scripts/PreFlight-Check.ps1`
    - `scripts/setup-merge-drivers.ps1`

- Desktop shortcut creation
  - Canonical: `scripts/create_desktop_shortcut.ps1`
  - Legacy wrapper kept at: `scripts/shortcuts/create_desktop_shortcut.ps1`

- VS Code launcher
  - Canonical: `scripts/launchers/Launch-Workflow-VSCode.ps1`
  - Legacy wrapper kept at: `scripts/launchers/Launch-Workflow-VSCode-Fixed.ps1`

- Git hooks installation
  - Canonical: `scripts/install_hooks.py`
  - Platform wrappers (kept): `scripts/install_hooks.ps1`, `scripts/install_hooks.sh` (both forward to the Python entrypoint where feasible).

Quick Index (primary entrypoints)
- Orchestration
  - `scripts/run_workflow.ps1` — run a workflow locally.
  - `scripts/run_gui_terminal.ps1` — launch GUI terminal.
  - `scripts/launchers/Launch-Workflow-VSCode.ps1` — open preconfigured VS Code workspace.

- Developer UX
  - `scripts/run_all_tests.ps1` — unified test runner (used by `make test`).
  - `scripts/validate_registry.py` — validate registry files.
  - `scripts/check_schema_compatibility.py` — schema compatibility check.
  - `scripts/check_doc_coverage.py` — docs coverage check.

- Git integration
  - `scripts/create_pr_ws_f.sh` — quick shell wrapper to create PR for ws-f-remaining-mods merge.
  - `scripts/create_pr_ws_f_remaining_mods.py` — Python script to create PR via GitHub API.
  - `scripts/create_github_issues.py` — create GitHub milestones and issues from roadmap docs.
  - `scripts/gh_seed_issues.py` — seed GitHub issues from templates.

- Maintenance
  - `scripts/cleanup_archive_and_obsolete.ps1` — cleanup helpers.
  - `scripts/cleanup_orphans.ps1` — remove orphan artifacts.
  - `scripts/backup_database.ps1` / `scripts/restore_database.ps1` — DB backup/restore.

Notes
- If you rely on a legacy path not listed here, open an issue and we will add a wrapper or restore the entry.
- For CI/local automation prefer `make` targets: `make test`, `make lint`, `make ci`.

