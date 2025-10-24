# Router System

This document describes the decomposed Router system introduced by WS2.

## Overview

Routing is split into focused modules under `src/cli_multi_rapid/routing/`:
- `router.py` – Orchestrates routing decisions with DI for components
- `complexity_analyzer.py` – Scores step complexity and infers operation type
- `parallel_planner.py` – Creates parallel execution groups with conflict awareness
- `resource_allocator.py` – Builds cross-workflow allocation/budget plans
- `models.py` – Dataclasses: `RoutingDecision`, `ComplexityAnalysis`, `ParallelRoutingPlan`, `AllocationPlan`

The legacy import path `src/cli_multi_rapid/router.py` remains as a shim that re‑exports `Router` and the model dataclasses to avoid breaking existing imports.

## Usage

```python
from cli_multi_rapid.routing import Router

router = Router()  # uses default components
decision = router.route_step({"id": "1", "name": "Edit", "actor": "ai_editor"})
plan = router.route_parallel_steps([{"id": "1", "name": "Edit", "actor": "ai_editor"}])
alloc = router.create_allocation_plan([{"name": "wf", "steps": [{"id": "1", "name": "Edit", "actor": "ai_editor"}]}])
```

Dependency injection is supported for testing and customization:

```python
from cli_multi_rapid.routing import Router
from cli_multi_rapid.routing.complexity_analyzer import ComplexityAnalyzer
from cli_multi_rapid.routing.parallel_planner import ParallelPlanner

router = Router(
    complexity_analyzer=ComplexityAnalyzer(),
    parallel_planner=ParallelPlanner(scope_manager=your_scope_manager),
)
```

## Backward Compatibility

- `from cli_multi_rapid.router import Router` still works via shim
- Dataclasses can be imported from `cli_multi_rapid.router` or `cli_multi_rapid.routing.models`

## Notes

- Deterministic engine is imported lazily to avoid circular imports during package initialization.
- The planner limits AI steps in parallel batches to avoid overwhelming external services.

