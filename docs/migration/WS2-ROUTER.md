# WS2 Migration: Router Decomposition

This guide summarizes changes to the Router system and how to update imports.

## What Changed

- Router code and routing dataclasses moved into `src/cli_multi_rapid/routing/`:
  - `router.py`, `complexity_analyzer.py`, `parallel_planner.py`, `resource_allocator.py`, `models.py`
- A compatibility shim remains at `src/cli_multi_rapid/router.py` that re‑exports `Router` and the model dataclasses.

## Impacted Imports

Old (still supported):
```python
from cli_multi_rapid.router import Router
from cli_multi_rapid.router import RoutingDecision, ParallelRoutingPlan
```

New (preferred):
```python
from cli_multi_rapid.routing import Router
from cli_multi_rapid.routing.models import RoutingDecision, ParallelRoutingPlan
```

## Component Interfaces

- Complexity analysis is provided by `ComplexityAnalyzer.analyze_step(step)`.
- Parallel planning uses `ParallelPlanner.create_parallel_plan(steps, route_step)`.
- Allocation is handled by `ResourceAllocator.create_allocation_plan(workflows, ...)`.

These are dependency-injected into `Router` for testability and isolation.

## Backward Compatibility

No functional changes are required for callers that import `Router` from `cli_multi_rapid.router`. All existing workflows and tests should continue to work.

