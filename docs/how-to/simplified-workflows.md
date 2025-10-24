# Simplified Workflow Guide

This guide describes the simplified, configuration-driven workflow mode that executes 25 sequential operations and routes them using a compact 5-role system.

## Overview

- Role-based routing via `RoleManager`
- Decision-matrix based tool selection via `SimplifiedRouter`
- Token estimation and logging through `CostTracker`
- Backward compatible and opt-in using `simplified: true` or `operations:`

## Running the Demo

Dry run:

```
cli-orchestrator run .ai/workflows/SIMPLIFIED_25_OPERATION.yaml --dry-run
```

With token limit enforcement:

```
cli-orchestrator run .ai/workflows/SIMPLIFIED_25_OPERATION.yaml --max-tokens 5000
```

Artifacts are written to `artifacts/simplified/summary.json`. Estimated token usage is logged to `logs/token_usage.jsonl`.

Execute via Router/adapters:

Add `execute: true` at the top level of the workflow to convert operations into steps and run them through the existing Router and adapters (e.g., `ai_analyst`, `ai_editor`, `vscode_diagnostics`, `pytest_runner`, `git_ops`). Omit or set to `false` to perform estimate-only dry calculations.

## Schema

Simplified workflows validate against `.ai/schemas/workflow.schema.json`. The simplified operation shape is inlined under `$defs` to avoid external `$ref` resolution. The schemas are intentionally permissive to avoid breaking existing workflows.

## Extending

- Add new operation types by updating the `operation->role` mapping in `src/cli_multi_rapid/roles/role_manager.py`.
- Adjust decision thresholds in `src/cli_multi_rapid/routing/simplified_router.py`.
- Integrate deeper with existing adapters by converting operations into traditional steps.
