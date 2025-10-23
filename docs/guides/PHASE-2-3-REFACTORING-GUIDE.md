# Phase 2 & 3 Refactoring Guide

## Overview

This guide provides detailed instructions for completing Phase 2 and Phase 3 of the CLI Orchestrator modularization refactoring. Phase 1 (adapter factory, unified logging, GitHub client) has been completed successfully.

**Target Audience:** AI assistants or developers continuing the refactoring work

**Prerequisites:**
- Understanding of Phase 1 changes (see git commit `c2ec201`)
- Familiarity with Python 3.9+, type hints, and pytest
- Knowledge of design patterns (Facade, Template Method, Strategy)

---

## Phase 1 Recap (COMPLETED)

### What Was Achieved

**Week 1: Adapter Factory Pattern**
- ✅ Created `src/cli_multi_rapid/adapters/factory.py` with lazy loading
- ✅ Enhanced `AdapterRegistry` with factory integration
- ✅ Refactored `Router` to eliminate 60+ LOC of direct imports
- ✅ Added plugin discovery system via setuptools entry points
- ✅ 39 tests for factory and registry

**Week 2: Unified Logging & GitHub Client**
- ✅ Created `src/cli_multi_rapid/logging/unified_logger.py` (consolidated 2 loggers)
- ✅ Created `src/cli_multi_rapid/domain/github_client.py` (585 LOC)
- ✅ Migrated `git_ops.py` and `github_integration.py` to use `GitHubClient`
- ✅ Eliminated ~105 LOC of duplicate GitHub API code
- ✅ 72 tests for logging and GitHub client
- ✅ Created migration guide

### Key Patterns Established

1. **Lazy Loading**: `factory.register_module("adapter_name", "module.path:ClassName")`
2. **Deprecation Warnings**: 6-month sunset timeline with clear migration paths
3. **Backward Compatibility**: Facade pattern + deprecation warnings
4. **Domain-Driven Design**: Business logic in `domain/` layer
5. **Test Coverage**: ≥85% required, comprehensive fixtures

### Metrics

- **Circular Dependencies Fixed:** 3
- **Code Eliminated:** ~305 LOC
- **Test Coverage:** 111 tests (all passing)
- **Net Change:** +3,303 LOC (including tests and docs)

---

## Phase 2: Core Architecture Refactoring (Weeks 3-4)

### Goals

Decompose the monolithic `workflow_runner.py` (1,404 LOC) into focused, single-responsibility modules in a new `core/` layer. This phase addresses:

1. **Separation of Concerns**: Step execution, orchestration, verification, and artifacts
2. **Testability**: Smaller modules are easier to test and mock
3. **Extensibility**: Clear interfaces for future enhancements
4. **Backward Compatibility**: Existing code continues to work via facade

### Architecture Overview

```
src/cli_multi_rapid/
├── core/                          # NEW: Core workflow execution modules
│   ├── __init__.py
│   ├── executor.py                # Step execution logic (~300 LOC)
│   ├── coordinator.py             # Workflow orchestration (~350 LOC)
│   ├── gate_manager.py            # Verification gates (~200 LOC)
│   └── artifact_manager.py        # Artifact tracking (~250 LOC)
├── workflow_runner.py             # REFACTOR: Facade over core/ modules (~200 LOC)
└── coordination/                  # CONSOLIDATE: 13 files → 5 modules
    ├── __init__.py
    ├── plan_manager.py            # Planning logic
    ├── progress_tracker.py        # Progress tracking
    ├── error_handler.py           # Error handling
    ├── lane_manager.py            # Lane management
    └── context_manager.py         # Context management
```

---

## Week 3: Core Module Creation

### Task 1: Create `core/executor.py`

**Purpose:** Execute individual workflow steps through adapters

**Responsibilities:**
- Validate step definitions against schema
- Route steps to appropriate adapters via Router
- Execute steps with proper context and error handling
- Collect execution results and metadata
- Track token usage and costs

**Key Classes:**

```python
#!/usr/bin/env python3
"""
Step Executor - Execute individual workflow steps

Handles step validation, routing, execution, and result collection.
Isolated from orchestration logic for better testability.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import AdapterResult
from ..router import Router
from ..cost_tracker import CostTracker


@dataclass
class StepExecutionResult:
    """Result of executing a single step."""

    step_id: str
    success: bool
    output: str
    artifacts: List[str]
    tokens_used: int
    execution_time_seconds: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StepExecutor:
    """
    Execute individual workflow steps through adapters.

    Responsibilities:
    - Validate step definitions
    - Route to appropriate adapters
    - Execute with error handling
    - Collect results and metadata
    """

    def __init__(
        self,
        router: Router,
        cost_tracker: Optional[CostTracker] = None,
        dry_run: bool = False
    ):
        """
        Initialize step executor.

        Args:
            router: Router for adapter selection and execution
            cost_tracker: Optional cost tracker for token usage
            dry_run: If True, simulate execution without making changes
        """
        self.router = router
        self.cost_tracker = cost_tracker
        self.dry_run = dry_run

    def execute_step(
        self,
        step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        files: Optional[str] = None
    ) -> StepExecutionResult:
        """
        Execute a single workflow step.

        Args:
            step: Step definition from workflow YAML
            context: Execution context (previous results, config, etc.)
            files: File pattern for step execution

        Returns:
            StepExecutionResult with execution details
        """
        import time

        step_id = step.get("id", "unknown")
        start_time = time.time()

        try:
            # Validate step definition
            self._validate_step(step)

            # Get adapter
            actor = step.get("actor")
            if not actor:
                raise ValueError(f"Step {step_id} missing 'actor' field")

            adapter = self.router.get_adapter(actor)
            if not adapter:
                raise ValueError(f"Adapter '{actor}' not found")

            # Check adapter availability
            if not adapter.is_available():
                raise RuntimeError(f"Adapter '{actor}' is not available")

            # Dry run mode
            if self.dry_run:
                return StepExecutionResult(
                    step_id=step_id,
                    success=True,
                    output=f"[DRY RUN] Would execute {actor}",
                    artifacts=step.get("emits", []),
                    tokens_used=0,
                    execution_time_seconds=time.time() - start_time,
                    metadata={"dry_run": True}
                )

            # Execute step
            result: AdapterResult = adapter.execute(step, context, files)

            # Track costs
            if self.cost_tracker and result.tokens_used > 0:
                self.cost_tracker.add_tokens(actor, result.tokens_used)

            # Build result
            return StepExecutionResult(
                step_id=step_id,
                success=result.success,
                output=result.output or "",
                artifacts=result.artifacts or [],
                tokens_used=result.tokens_used,
                execution_time_seconds=time.time() - start_time,
                error=result.error,
                metadata=result.metadata
            )

        except Exception as e:
            return StepExecutionResult(
                step_id=step_id,
                success=False,
                output="",
                artifacts=[],
                tokens_used=0,
                execution_time_seconds=time.time() - start_time,
                error=str(e)
            )

    def _validate_step(self, step: Dict[str, Any]) -> None:
        """
        Validate step definition.

        Args:
            step: Step definition to validate

        Raises:
            ValueError: If step is invalid
        """
        required_fields = ["id", "name", "actor"]
        for field in required_fields:
            if field not in step:
                raise ValueError(f"Step missing required field: {field}")

    def estimate_step_cost(self, step: Dict[str, Any]) -> int:
        """
        Estimate token cost for a step.

        Args:
            step: Step definition

        Returns:
            Estimated tokens
        """
        actor = step.get("actor")
        if not actor:
            return 0

        adapter = self.router.get_adapter(actor)
        if not adapter:
            return 0

        return adapter.estimate_cost(step)
```

**Testing Requirements:**

Create `tests/core/test_executor.py`:
- Test step validation (missing fields, invalid actor)
- Test successful step execution
- Test failed step execution
- Test dry-run mode
- Test cost tracking integration
- Test error handling and result collection
- Minimum 20 tests, ≥85% coverage

---

### Task 2: Create `core/coordinator.py`

**Purpose:** Orchestrate multi-step workflow execution

**Responsibilities:**
- Load and validate workflow YAML against schema
- Execute steps sequentially or in parallel (future)
- Manage workflow context and state
- Handle step dependencies and conditional execution
- Aggregate results and generate final report

**Key Classes:**

```python
#!/usr/bin/env python3
"""
Workflow Coordinator - Orchestrate multi-step workflow execution

Handles workflow loading, validation, execution order, and result aggregation.
Separated from step execution for better separation of concerns.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .executor import StepExecutor, StepExecutionResult


@dataclass
class WorkflowResult:
    """Result of executing a complete workflow."""

    workflow_name: str
    success: bool
    steps_executed: int
    steps_succeeded: int
    steps_failed: int
    total_tokens_used: int
    total_execution_time_seconds: float
    step_results: List[StepExecutionResult]
    artifacts: List[str]
    error: Optional[str] = None


class WorkflowCoordinator:
    """
    Orchestrate multi-step workflow execution.

    Responsibilities:
    - Load and validate workflows
    - Execute steps in order
    - Manage workflow state and context
    - Aggregate results
    """

    def __init__(
        self,
        executor: StepExecutor,
        schema_validator: Optional[Any] = None
    ):
        """
        Initialize workflow coordinator.

        Args:
            executor: Step executor for running individual steps
            schema_validator: Optional JSON schema validator
        """
        self.executor = executor
        self.schema_validator = schema_validator

    def execute_workflow(
        self,
        workflow_path: str,
        files: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Execute a complete workflow.

        Args:
            workflow_path: Path to workflow YAML file
            files: File pattern for execution
            extra_context: Additional context to merge

        Returns:
            WorkflowResult with aggregated execution details
        """
        import time

        start_time = time.time()

        try:
            # Load workflow
            workflow = self._load_workflow(workflow_path)
            workflow_name = workflow.get("name", Path(workflow_path).stem)

            # Validate workflow
            if self.schema_validator:
                self._validate_workflow(workflow)

            # Build initial context
            context = self._build_initial_context(workflow, extra_context)

            # Execute steps
            steps = workflow.get("steps", [])
            step_results: List[StepExecutionResult] = []

            for step in steps:
                # Execute step
                result = self.executor.execute_step(step, context, files)
                step_results.append(result)

                # Update context with step results
                context = self._update_context(context, step, result)

                # Stop on failure if fail_fast
                if not result.success and workflow.get("policy", {}).get("fail_fast", True):
                    break

            # Aggregate results
            return self._aggregate_results(
                workflow_name=workflow_name,
                step_results=step_results,
                total_time=time.time() - start_time
            )

        except Exception as e:
            return WorkflowResult(
                workflow_name=Path(workflow_path).stem,
                success=False,
                steps_executed=0,
                steps_succeeded=0,
                steps_failed=0,
                total_tokens_used=0,
                total_execution_time_seconds=time.time() - start_time,
                step_results=[],
                artifacts=[],
                error=str(e)
            )

    def _load_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """Load workflow YAML file."""
        with open(workflow_path, "r") as f:
            return yaml.safe_load(f)

    def _validate_workflow(self, workflow: Dict[str, Any]) -> None:
        """Validate workflow against schema."""
        # Implement schema validation if validator provided
        if not workflow.get("steps"):
            raise ValueError("Workflow missing 'steps' field")

    def _build_initial_context(
        self,
        workflow: Dict[str, Any],
        extra_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build initial execution context."""
        context = {
            "workflow_name": workflow.get("name", "unknown"),
            "inputs": workflow.get("inputs", {}),
            "policy": workflow.get("policy", {}),
            "step_results": {},
        }

        if extra_context:
            context.update(extra_context)

        return context

    def _update_context(
        self,
        context: Dict[str, Any],
        step: Dict[str, Any],
        result: StepExecutionResult
    ) -> Dict[str, Any]:
        """Update context with step result."""
        step_id = step.get("id", "unknown")
        context["step_results"][step_id] = {
            "success": result.success,
            "output": result.output,
            "artifacts": result.artifacts,
            "metadata": result.metadata,
        }
        return context

    def _aggregate_results(
        self,
        workflow_name: str,
        step_results: List[StepExecutionResult],
        total_time: float
    ) -> WorkflowResult:
        """Aggregate step results into workflow result."""
        succeeded = sum(1 for r in step_results if r.success)
        failed = sum(1 for r in step_results if not r.success)
        total_tokens = sum(r.tokens_used for r in step_results)

        all_artifacts = []
        for result in step_results:
            all_artifacts.extend(result.artifacts)

        return WorkflowResult(
            workflow_name=workflow_name,
            success=failed == 0,
            steps_executed=len(step_results),
            steps_succeeded=succeeded,
            steps_failed=failed,
            total_tokens_used=total_tokens,
            total_execution_time_seconds=total_time,
            step_results=step_results,
            artifacts=all_artifacts,
        )
```

**Testing Requirements:**

Create `tests/core/test_coordinator.py`:
- Test workflow loading from YAML
- Test workflow validation
- Test step execution order
- Test context building and updates
- Test result aggregation
- Test fail-fast behavior
- Test error handling
- Minimum 15 tests, ≥85% coverage

---

### Task 3: Create `core/gate_manager.py`

**Purpose:** Manage verification gates and quality checks

**Responsibilities:**
- Validate gate definitions
- Execute gate checks (schema validation, test results, diff limits)
- Aggregate gate results
- Support custom gate types
- Provide detailed failure reports

**Key Classes:**

```python
#!/usr/bin/env python3
"""
Gate Manager - Verification gates and quality checks

Handles execution and validation of verification gates to ensure
workflow quality and compliance.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import json


class GateType(Enum):
    """Supported gate types."""

    TESTS_PASS = "tests_pass"
    DIFF_LIMITS = "diff_limits"
    SCHEMA_VALID = "schema_valid"
    CUSTOM = "custom"


@dataclass
class GateResult:
    """Result of executing a verification gate."""

    gate_id: str
    gate_type: GateType
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class GateManager:
    """
    Manage verification gates and quality checks.

    Responsibilities:
    - Execute gate checks
    - Validate artifacts
    - Aggregate gate results
    - Support extensibility for custom gates
    """

    def __init__(self):
        """Initialize gate manager."""
        self._gate_handlers = {
            GateType.TESTS_PASS: self._check_tests_pass,
            GateType.DIFF_LIMITS: self._check_diff_limits,
            GateType.SCHEMA_VALID: self._check_schema_valid,
        }

    def execute_gates(
        self,
        gates: List[Dict[str, Any]],
        artifacts: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[GateResult]:
        """
        Execute all verification gates.

        Args:
            gates: List of gate definitions
            artifacts: Artifact paths generated by workflow
            context: Additional context for gate execution

        Returns:
            List of GateResult objects
        """
        results = []

        for gate in gates:
            result = self.execute_gate(gate, artifacts, context)
            results.append(result)

        return results

    def execute_gate(
        self,
        gate: Dict[str, Any],
        artifacts: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> GateResult:
        """
        Execute a single verification gate.

        Args:
            gate: Gate definition
            artifacts: Artifact paths
            context: Additional context

        Returns:
            GateResult
        """
        gate_id = gate.get("id", "unknown")
        gate_type_str = gate.get("type", "custom")

        try:
            gate_type = GateType(gate_type_str)
        except ValueError:
            gate_type = GateType.CUSTOM

        # Get handler
        handler = self._gate_handlers.get(gate_type)

        if not handler:
            return GateResult(
                gate_id=gate_id,
                gate_type=gate_type,
                success=False,
                message=f"No handler for gate type: {gate_type_str}"
            )

        # Execute gate
        try:
            return handler(gate, artifacts, context)
        except Exception as e:
            return GateResult(
                gate_id=gate_id,
                gate_type=gate_type,
                success=False,
                message=f"Gate execution failed: {str(e)}"
            )

    def _check_tests_pass(
        self,
        gate: Dict[str, Any],
        artifacts: List[str],
        context: Optional[Dict[str, Any]]
    ) -> GateResult:
        """Check if tests pass from test report artifact."""
        gate_id = gate.get("id", "tests_pass")

        # Find test report artifact
        test_report_path = gate.get("artifact", "artifacts/test_report.json")

        if not Path(test_report_path).exists():
            return GateResult(
                gate_id=gate_id,
                gate_type=GateType.TESTS_PASS,
                success=False,
                message=f"Test report not found: {test_report_path}"
            )

        # Load and check test report
        with open(test_report_path) as f:
            report = json.load(f)

        tests_passed = report.get("passed", 0)
        tests_failed = report.get("failed", 0)

        success = tests_failed == 0

        return GateResult(
            gate_id=gate_id,
            gate_type=GateType.TESTS_PASS,
            success=success,
            message=f"Tests: {tests_passed} passed, {tests_failed} failed",
            details={"passed": tests_passed, "failed": tests_failed}
        )

    def _check_diff_limits(
        self,
        gate: Dict[str, Any],
        artifacts: List[str],
        context: Optional[Dict[str, Any]]
    ) -> GateResult:
        """Check if diff size is within limits."""
        gate_id = gate.get("id", "diff_limits")
        max_files = gate.get("max_files", 100)
        max_lines = gate.get("max_lines", 1000)

        # Get diff stats from context or artifact
        diff_stats = (context or {}).get("diff_stats", {})

        files_changed = diff_stats.get("files_changed", 0)
        lines_changed = diff_stats.get("lines_changed", 0)

        within_limits = files_changed <= max_files and lines_changed <= max_lines

        return GateResult(
            gate_id=gate_id,
            gate_type=GateType.DIFF_LIMITS,
            success=within_limits,
            message=f"Diff: {files_changed}/{max_files} files, {lines_changed}/{max_lines} lines",
            details={
                "files_changed": files_changed,
                "lines_changed": lines_changed,
                "within_limits": within_limits
            }
        )

    def _check_schema_valid(
        self,
        gate: Dict[str, Any],
        artifacts: List[str],
        context: Optional[Dict[str, Any]]
    ) -> GateResult:
        """Check if artifact is valid against schema."""
        gate_id = gate.get("id", "schema_valid")
        artifact_path = gate.get("artifact")
        schema_path = gate.get("schema")

        if not artifact_path or not schema_path:
            return GateResult(
                gate_id=gate_id,
                gate_type=GateType.SCHEMA_VALID,
                success=False,
                message="Missing artifact or schema path"
            )

        # Use existing verifier logic (import and delegate)
        from ..verifier import Verifier

        verifier = Verifier(schema_dir=Path(schema_path).parent)
        result = verifier.verify_artifact(artifact_path, schema_path)

        return GateResult(
            gate_id=gate_id,
            gate_type=GateType.SCHEMA_VALID,
            success=result.get("valid", False),
            message=result.get("message", "Schema validation result"),
            details=result
        )

    def register_custom_gate(
        self,
        gate_type: str,
        handler: callable
    ) -> None:
        """
        Register a custom gate handler.

        Args:
            gate_type: Custom gate type name
            handler: Function(gate, artifacts, context) -> GateResult
        """
        self._gate_handlers[GateType.CUSTOM] = handler
```

**Testing Requirements:**

Create `tests/core/test_gate_manager.py`:
- Test tests_pass gate
- Test diff_limits gate
- Test schema_valid gate
- Test custom gate registration
- Test gate failure scenarios
- Test missing artifacts
- Minimum 12 tests, ≥85% coverage

---

### Task 4: Create `core/artifact_manager.py`

**Purpose:** Track and manage workflow artifacts

**Responsibilities:**
- Track artifact creation and paths
- Validate artifact existence
- Organize artifacts by workflow/step
- Provide artifact discovery and querying
- Support artifact cleanup

**Key Classes:**

```python
#!/usr/bin/env python3
"""
Artifact Manager - Track and manage workflow artifacts

Handles artifact registration, validation, organization, and cleanup.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Artifact:
    """Metadata for a workflow artifact."""

    path: str
    step_id: str
    created_at: str
    size_bytes: int = 0
    exists: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ArtifactManager:
    """
    Track and manage workflow artifacts.

    Responsibilities:
    - Register artifacts from steps
    - Validate artifact existence
    - Organize by workflow/step
    - Support cleanup
    """

    def __init__(self, artifacts_dir: str = "artifacts"):
        """
        Initialize artifact manager.

        Args:
            artifacts_dir: Base directory for artifacts
        """
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts: List[Artifact] = []

    def register_artifact(
        self,
        path: str,
        step_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Artifact:
        """
        Register a new artifact.

        Args:
            path: Artifact file path
            step_id: ID of step that created it
            metadata: Optional metadata

        Returns:
            Artifact object
        """
        artifact_path = Path(path)

        artifact = Artifact(
            path=str(artifact_path),
            step_id=step_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            size_bytes=artifact_path.stat().st_size if artifact_path.exists() else 0,
            exists=artifact_path.exists(),
            metadata=metadata or {}
        )

        self.artifacts.append(artifact)
        return artifact

    def get_artifacts_by_step(self, step_id: str) -> List[Artifact]:
        """Get all artifacts created by a specific step."""
        return [a for a in self.artifacts if a.step_id == step_id]

    def get_all_artifacts(self) -> List[Artifact]:
        """Get all registered artifacts."""
        return self.artifacts.copy()

    def validate_artifacts(self) -> Dict[str, Any]:
        """
        Validate that all registered artifacts exist.

        Returns:
            Validation report with missing/invalid artifacts
        """
        missing = [a for a in self.artifacts if not Path(a.path).exists()]

        return {
            "total": len(self.artifacts),
            "existing": len(self.artifacts) - len(missing),
            "missing": len(missing),
            "missing_paths": [a.path for a in missing],
            "valid": len(missing) == 0
        }

    def cleanup_artifacts(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up artifact files.

        Args:
            dry_run: If True, don't actually delete files

        Returns:
            Cleanup report
        """
        deleted = []
        errors = []

        for artifact in self.artifacts:
            artifact_path = Path(artifact.path)

            if not artifact_path.exists():
                continue

            if dry_run:
                deleted.append(artifact.path)
            else:
                try:
                    artifact_path.unlink()
                    deleted.append(artifact.path)
                except Exception as e:
                    errors.append({"path": artifact.path, "error": str(e)})

        return {
            "dry_run": dry_run,
            "deleted": len(deleted),
            "errors": len(errors),
            "deleted_paths": deleted,
            "error_details": errors
        }

    def generate_manifest(self) -> Dict[str, Any]:
        """
        Generate artifact manifest.

        Returns:
            Manifest with all artifact metadata
        """
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifacts_dir": str(self.artifacts_dir),
            "total_artifacts": len(self.artifacts),
            "artifacts": [
                {
                    "path": a.path,
                    "step_id": a.step_id,
                    "created_at": a.created_at,
                    "size_bytes": a.size_bytes,
                    "exists": a.exists,
                    "metadata": a.metadata
                }
                for a in self.artifacts
            ]
        }
```

**Testing Requirements:**

Create `tests/core/test_artifact_manager.py`:
- Test artifact registration
- Test get_artifacts_by_step
- Test artifact validation
- Test cleanup (dry-run and actual)
- Test manifest generation
- Minimum 10 tests, ≥85% coverage

---

### Task 5: Refactor `workflow_runner.py` as Facade

**Purpose:** Maintain backward compatibility while delegating to core modules

**Approach:**
1. Keep existing public API (`WorkflowRunner` class, `run_workflow()` method)
2. Add deprecation warnings for direct instantiation
3. Delegate all logic to `core/` modules
4. Reduce from 1,404 LOC to ~200 LOC

**Example Refactoring:**

```python
#!/usr/bin/env python3
"""
Workflow Runner - Backward-compatible facade over core modules

DEPRECATED: This module is maintained for backward compatibility.
New code should use core.coordinator.WorkflowCoordinator directly.
"""

import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from .core.executor import StepExecutor
from .core.coordinator import WorkflowCoordinator, WorkflowResult
from .core.gate_manager import GateManager
from .core.artifact_manager import ArtifactManager
from .router import Router
from .cost_tracker import CostTracker


class WorkflowRunner:
    """
    DEPRECATED: Use core.coordinator.WorkflowCoordinator instead.

    This class is maintained for backward compatibility and will be
    removed in version 2.0 (estimated 6 months).

    Migration:
        # Old way
        runner = WorkflowRunner()
        result = runner.run_workflow("workflow.yaml")

        # New way
        from cli_multi_rapid.core.coordinator import WorkflowCoordinator
        from cli_multi_rapid.core.executor import StepExecutor
        from cli_multi_rapid.router import Router

        executor = StepExecutor(Router())
        coordinator = WorkflowCoordinator(executor)
        result = coordinator.execute_workflow("workflow.yaml")
    """

    def __init__(
        self,
        router: Optional[Router] = None,
        cost_tracker: Optional[CostTracker] = None,
        console: Optional[Console] = None
    ):
        """Initialize workflow runner (deprecated)."""
        warnings.warn(
            "WorkflowRunner is deprecated. Use core.coordinator.WorkflowCoordinator instead. "
            "See migration guide in docs/guides/PHASE-2-3-REFACTORING-GUIDE.md",
            DeprecationWarning,
            stacklevel=2
        )

        # Initialize core modules
        self.router = router or Router()
        self.cost_tracker = cost_tracker or CostTracker()
        self.console = console or Console()

        self.executor = StepExecutor(self.router, self.cost_tracker)
        self.coordinator = WorkflowCoordinator(self.executor)
        self.gate_manager = GateManager()
        self.artifact_manager = ArtifactManager()

    def run_workflow(
        self,
        workflow_path: str,
        files: Optional[str] = None,
        dry_run: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a workflow (deprecated).

        Args:
            workflow_path: Path to workflow YAML
            files: File pattern
            dry_run: Simulate execution
            **kwargs: Additional context

        Returns:
            Result dictionary (backward-compatible format)
        """
        # Set dry-run mode
        self.executor.dry_run = dry_run

        # Execute workflow via coordinator
        result: WorkflowResult = self.coordinator.execute_workflow(
            workflow_path, files, kwargs
        )

        # Register artifacts
        for artifact_path in result.artifacts:
            self.artifact_manager.register_artifact(
                artifact_path,
                step_id="unknown",  # Would need step-level tracking
            )

        # Convert to legacy format
        return self._convert_to_legacy_format(result)

    def _convert_to_legacy_format(self, result: WorkflowResult) -> Dict[str, Any]:
        """Convert WorkflowResult to legacy dictionary format."""
        return {
            "success": result.success,
            "workflow": result.workflow_name,
            "steps_executed": result.steps_executed,
            "steps_succeeded": result.steps_succeeded,
            "steps_failed": result.steps_failed,
            "tokens_used": result.total_tokens_used,
            "execution_time": result.total_execution_time_seconds,
            "artifacts": result.artifacts,
            "error": result.error,
        }


# Convenience function (deprecated)
def run_workflow(workflow_path: str, **kwargs) -> Dict[str, Any]:
    """
    DEPRECATED: Use WorkflowCoordinator.execute_workflow() instead.

    Convenience function maintained for backward compatibility.
    """
    warnings.warn(
        "run_workflow() is deprecated. Use WorkflowCoordinator.execute_workflow() instead.",
        DeprecationWarning,
        stacklevel=2
    )

    runner = WorkflowRunner()
    return runner.run_workflow(workflow_path, **kwargs)
```

**Testing Requirements:**

Update `tests/test_workflow_runner.py`:
- Ensure existing tests still pass (backward compatibility)
- Add tests for deprecation warnings
- Add tests for delegation to core modules
- Maintain ≥85% coverage

---

## Week 4: Coordination Module Consolidation

### Current State

The `src/cli_multi_rapid/coordination/` directory contains 13 files:

```
coordination/
├── __init__.py
├── plan_coordinator.py        # Planning logic
├── plan_tracker.py            # Plan tracking
├── progress_reporter.py       # Progress reporting
├── error_coordinator.py       # Error handling
├── error_tracker.py           # Error tracking
├── lane_coordinator.py        # Lane management
├── lane_tracker.py            # Lane tracking
├── context_coordinator.py     # Context management
├── context_tracker.py         # Context tracking
├── state_manager.py           # State management
├── event_emitter.py           # Event emission
└── telemetry_collector.py     # Telemetry collection
```

### Goal

Consolidate into 5 focused modules:

```
coordination/
├── __init__.py
├── plan_manager.py           # Planning + tracking
├── progress_tracker.py       # Progress + reporting
├── error_handler.py          # Error coordination + tracking
├── lane_manager.py           # Lane coordination + tracking
└── context_manager.py        # Context + state + events + telemetry
```

### Consolidation Strategy

1. **plan_manager.py** ← merge `plan_coordinator.py` + `plan_tracker.py`
2. **progress_tracker.py** ← merge `progress_reporter.py` (keep existing)
3. **error_handler.py** ← merge `error_coordinator.py` + `error_tracker.py`
4. **lane_manager.py** ← merge `lane_coordinator.py` + `lane_tracker.py`
5. **context_manager.py** ← merge `context_coordinator.py` + `context_tracker.py` + `state_manager.py` + `event_emitter.py` + `telemetry_collector.py`

### Task 6: Create `coordination/plan_manager.py`

```python
#!/usr/bin/env python3
"""
Plan Manager - Planning logic and tracking

Consolidates plan_coordinator.py and plan_tracker.py into a single module.
"""

# Merge logic from both files
# Add deprecation warnings to old files
# Update imports in __init__.py
```

**Steps:**
1. Read both source files
2. Identify overlapping vs. unique functionality
3. Merge into single module with clear section comments
4. Add deprecation warnings to old files
5. Update `__init__.py` to export from new module
6. Run tests and fix any failures

**Testing:**
- Ensure existing tests pass
- Add integration tests for merged functionality
- Coverage ≥85%

### Task 7-10: Similar consolidation for other modules

Follow the same pattern for:
- `error_handler.py`
- `lane_manager.py`
- `context_manager.py`

---

## Phase 3: CLI & Configuration (Weeks 5-6)

### Goals

1. **Modularize CLI commands** into separate focused files
2. **Consolidate configuration management** from multiple sources
3. **Improve CLI UX** with better help, autocomplete, validation

---

## Week 5: CLI Command Modularization

### Current State

`src/cli_multi_rapid/cli.py` is minimal (31 LOC), but command logic is scattered.

### Goal

Create modular command structure:

```
src/cli_multi_rapid/commands/
├── __init__.py
├── git_commands.py      # EXISTING: Git operations
├── replay.py            # EXISTING: Conversation replay
├── workflow_commands.py # NEW: Workflow execution commands
├── verify_commands.py   # NEW: Verification commands
├── pr_commands.py       # NEW: PR creation commands
└── cost_commands.py     # NEW: Cost tracking commands
```

### Task 11: Create `commands/workflow_commands.py`

Extract workflow-related commands:

```python
#!/usr/bin/env python3
"""
Workflow Commands - CLI commands for workflow execution
"""

import typer
from pathlib import Path
from typing import Optional

from ..core.coordinator import WorkflowCoordinator
from ..core.executor import StepExecutor
from ..router import Router

app = typer.Typer(help="Workflow execution commands")


@app.command("run")
def run_workflow(
    workflow_path: Path = typer.Argument(..., help="Path to workflow YAML file"),
    files: Optional[str] = typer.Option(None, "--files", help="File pattern to process"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate execution without changes"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run a workflow from YAML file."""
    from rich.console import Console

    console = Console()

    if not workflow_path.exists():
        console.print(f"[red]Error: Workflow file not found: {workflow_path}[/red]")
        raise typer.Exit(1)

    # Initialize core modules
    router = Router()
    executor = StepExecutor(router, dry_run=dry_run)
    coordinator = WorkflowCoordinator(executor)

    # Execute workflow
    console.print(f"[bold]Executing workflow:[/bold] {workflow_path}")
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")

    result = coordinator.execute_workflow(str(workflow_path), files)

    # Display results
    if result.success:
        console.print(f"[green]✓ Workflow completed successfully[/green]")
    else:
        console.print(f"[red]✗ Workflow failed: {result.error}[/red]")

    console.print(f"\nSteps: {result.steps_succeeded}/{result.steps_executed} succeeded")
    console.print(f"Tokens: {result.total_tokens_used:,}")
    console.print(f"Time: {result.total_execution_time_seconds:.2f}s")

    if result.artifacts:
        console.print(f"\nArtifacts generated:")
        for artifact in result.artifacts:
            console.print(f"  - {artifact}")

    if not result.success:
        raise typer.Exit(1)


@app.command("list")
def list_workflows(
    workflow_dir: Path = typer.Option(".ai/workflows", "--dir", help="Workflow directory"),
):
    """List available workflows."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    if not workflow_dir.exists():
        console.print(f"[red]Workflow directory not found: {workflow_dir}[/red]")
        raise typer.Exit(1)

    workflows = list(workflow_dir.glob("*.yaml")) + list(workflow_dir.glob("*.yml"))

    if not workflows:
        console.print(f"[yellow]No workflows found in {workflow_dir}[/yellow]")
        return

    table = Table(title="Available Workflows")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")

    for workflow in sorted(workflows):
        table.add_row(workflow.stem, str(workflow))

    console.print(table)
```

### Task 12: Create additional command modules

Follow similar pattern for:
- `verify_commands.py` - Artifact verification commands
- `pr_commands.py` - PR creation commands
- `cost_commands.py` - Cost tracking and reporting commands

### Task 13: Update main CLI entrypoint

Update `src/cli_multi_rapid/cli.py` to import and register all command modules.

---

## Week 6: Configuration Consolidation

### Current State

Configuration is scattered across:
- Environment variables
- `.env` files
- `config/` directory YAML files
- `src/cli_multi_rapid/config.py`
- Adapter-specific config
- Hardcoded defaults

### Goal

Create unified configuration system:

```
src/cli_multi_rapid/config/
├── __init__.py
├── settings.py          # Pydantic settings (env + .env)
├── loader.py            # Load config from multiple sources
├── validator.py         # Validate configuration
└── defaults.py          # Default values
```

### Task 14: Create `config/settings.py`

Use Pydantic Settings for environment-based config:

```python
#!/usr/bin/env python3
"""
Settings - Unified configuration from environment variables

Uses Pydantic Settings for type-safe configuration loading.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class OrchestratorSettings(BaseSettings):
    """Unified orchestrator configuration."""

    # GitHub
    github_token: Optional[str] = Field(None, env="GITHUB_TOKEN")

    # AI API Keys
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")

    # Ollama
    ollama_api_base: str = Field("http://localhost:11434", env="OLLAMA_API_BASE")

    # Workflow settings
    max_token_budget: int = Field(500000, env="MAX_TOKEN_BUDGET")
    default_workflow_timeout: int = Field(30, env="DEFAULT_WORKFLOW_TIMEOUT")

    # Directories
    workflow_dir: Path = Field(Path(".ai/workflows"), env="WORKFLOW_DIR")
    artifacts_dir: Path = Field(Path("artifacts"), env="ARTIFACTS_DIR")
    logs_dir: Path = Field(Path("logs"), env="LOGS_DIR")

    # Environment
    cli_orchestrator_env: str = Field("development", env="CLI_ORCHESTRATOR_ENV")
    debug: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings: Optional[OrchestratorSettings] = None


def get_settings() -> OrchestratorSettings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = OrchestratorSettings()
    return _settings
```

### Task 15: Migrate code to use unified settings

1. Update all modules to use `get_settings()` instead of `os.environ.get()`
2. Remove hardcoded defaults
3. Update tests to mock settings
4. Create configuration migration guide

---

## Testing Strategy

### Test Coverage Requirements

- Each new module: ≥85% coverage
- Integration tests for module interactions
- Backward compatibility tests for deprecated APIs
- Performance tests for lazy loading

### Test Organization

```
tests/
├── core/
│   ├── test_executor.py          # ≥20 tests
│   ├── test_coordinator.py       # ≥15 tests
│   ├── test_gate_manager.py      # ≥12 tests
│   └── test_artifact_manager.py  # ≥10 tests
├── coordination/
│   ├── test_plan_manager.py
│   ├── test_error_handler.py
│   ├── test_lane_manager.py
│   └── test_context_manager.py
├── commands/
│   ├── test_workflow_commands.py
│   ├── test_verify_commands.py
│   ├── test_pr_commands.py
│   └── test_cost_commands.py
├── config/
│   ├── test_settings.py
│   ├── test_loader.py
│   └── test_validator.py
└── integration/
    ├── test_end_to_end_workflow.py
    └── test_backward_compatibility.py
```

### Running Tests

```bash
# All Phase 2 tests
pytest tests/core/ -v --cov=src/cli_multi_rapid/core --cov-fail-under=85

# All Phase 3 tests
pytest tests/commands/ tests/config/ -v --cov-fail-under=85

# Integration tests
pytest tests/integration/ -v

# Full suite
pytest tests/ -v --cov=src --cov-fail-under=85
```

---

## Migration Guides

### For Users

Create `docs/guides/WORKFLOW-RUNNER-MIGRATION.md`:

```markdown
# Migrating from WorkflowRunner to Core Modules

## Overview

`WorkflowRunner` is deprecated and will be removed in v2.0 (estimated 6 months).
Migrate to the new `core` modules for better modularity and testability.

## Old Way (Deprecated)

```python
from cli_multi_rapid.workflow_runner import WorkflowRunner

runner = WorkflowRunner()
result = runner.run_workflow("workflow.yaml", files="src/**/*.py")
```

## New Way (Recommended)

```python
from cli_multi_rapid.core.coordinator import WorkflowCoordinator
from cli_multi_rapid.core.executor import StepExecutor
from cli_multi_rapid.router import Router

# Initialize components
router = Router()
executor = StepExecutor(router)
coordinator = WorkflowCoordinator(executor)

# Execute workflow
result = coordinator.execute_workflow("workflow.yaml", files="src/**/*.py")
```

## Benefits

- Better separation of concerns
- Easier to test individual components
- More flexible for custom orchestration logic
- Better performance with lazy loading
```

### For Developers

Create `docs/guides/COORDINATION-CONSOLIDATION.md`:

```markdown
# Coordination Module Consolidation

## Overview

The 13 coordination files have been consolidated into 5 focused modules.

## Import Changes

### Old Imports (Deprecated)

```python
from cli_multi_rapid.coordination.plan_coordinator import PlanCoordinator
from cli_multi_rapid.coordination.plan_tracker import PlanTracker
```

### New Imports (Recommended)

```python
from cli_multi_rapid.coordination.plan_manager import PlanManager
```

## Migration Matrix

| Old Module | New Module | Notes |
|-----------|-----------|-------|
| `plan_coordinator.py` | `plan_manager.py` | Merged with plan_tracker |
| `plan_tracker.py` | `plan_manager.py` | Merged into plan_manager |
| `error_coordinator.py` | `error_handler.py` | Merged with error_tracker |
| `error_tracker.py` | `error_handler.py` | Merged into error_handler |
| ... | ... | ... |
```

---

## Success Criteria

### Phase 2 Complete When:

- ✅ All 4 core modules created (`executor.py`, `coordinator.py`, `gate_manager.py`, `artifact_manager.py`)
- ✅ `workflow_runner.py` refactored as facade (~200 LOC, down from 1,404)
- ✅ 13 coordination files consolidated into 5 modules
- ✅ ≥85% test coverage for all new modules
- ✅ All existing tests still pass (backward compatibility)
- ✅ Deprecation warnings added to old APIs
- ✅ Migration guides created

### Phase 3 Complete When:

- ✅ CLI commands modularized into `commands/` directory
- ✅ Unified configuration system in `config/`
- ✅ All code migrated to use `get_settings()`
- ✅ ≥85% test coverage for commands and config
- ✅ Configuration migration guide created
- ✅ CLI UX improvements (help, autocomplete)

---

## Common Pitfalls

1. **Breaking Backward Compatibility**: Always add deprecation warnings before removing APIs
2. **Insufficient Testing**: Aim for ≥85% coverage and comprehensive integration tests
3. **Incomplete Consolidation**: Ensure all functionality from old modules is preserved
4. **Missing Documentation**: Update docstrings, migration guides, and architecture docs
5. **Circular Dependencies**: Be careful when refactoring to avoid reintroducing circular imports
6. **Hardcoded Paths**: Use configuration for all paths (workflow dir, artifacts dir, etc.)
7. **Inconsistent Patterns**: Follow established patterns from Phase 1 (lazy loading, deprecation warnings, etc.)

---

## Getting Help

- **Phase 1 Reference**: See git commit `c2ec201` for patterns and examples
- **Architecture Docs**: `docs/architecture/`
- **Testing Guide**: `docs/guides/testing-guide.md`
- **GitHub Issues**: https://github.com/DICKY1987/CLI_RESTART/issues

---

## Appendix: File Checklist

### Phase 2 New Files

- [ ] `src/cli_multi_rapid/core/__init__.py`
- [ ] `src/cli_multi_rapid/core/executor.py`
- [ ] `src/cli_multi_rapid/core/coordinator.py`
- [ ] `src/cli_multi_rapid/core/gate_manager.py`
- [ ] `src/cli_multi_rapid/core/artifact_manager.py`
- [ ] `tests/core/test_executor.py`
- [ ] `tests/core/test_coordinator.py`
- [ ] `tests/core/test_gate_manager.py`
- [ ] `tests/core/test_artifact_manager.py`

### Phase 2 Modified Files

- [ ] `src/cli_multi_rapid/workflow_runner.py` (refactor as facade)
- [ ] `src/cli_multi_rapid/coordination/plan_manager.py` (consolidate)
- [ ] `src/cli_multi_rapid/coordination/error_handler.py` (consolidate)
- [ ] `src/cli_multi_rapid/coordination/lane_manager.py` (consolidate)
- [ ] `src/cli_multi_rapid/coordination/context_manager.py` (consolidate)
- [ ] `src/cli_multi_rapid/coordination/__init__.py` (update exports)

### Phase 2 Deprecated Files

- [ ] Add deprecation warnings to old coordination files

### Phase 3 New Files

- [ ] `src/cli_multi_rapid/commands/workflow_commands.py`
- [ ] `src/cli_multi_rapid/commands/verify_commands.py`
- [ ] `src/cli_multi_rapid/commands/pr_commands.py`
- [ ] `src/cli_multi_rapid/commands/cost_commands.py`
- [ ] `src/cli_multi_rapid/config/settings.py`
- [ ] `src/cli_multi_rapid/config/loader.py`
- [ ] `src/cli_multi_rapid/config/validator.py`
- [ ] `src/cli_multi_rapid/config/defaults.py`
- [ ] `tests/commands/test_workflow_commands.py`
- [ ] `tests/config/test_settings.py`

### Phase 3 Modified Files

- [ ] `src/cli_multi_rapid/cli.py` (register command modules)
- [ ] All modules using `os.environ.get()` → `get_settings()`

### Documentation

- [ ] `docs/guides/WORKFLOW-RUNNER-MIGRATION.md`
- [ ] `docs/guides/COORDINATION-CONSOLIDATION.md`
- [ ] `docs/guides/CONFIGURATION-MIGRATION.md`
- [ ] Update `CLAUDE.md` with Phase 2-3 changes

---

## Commit Message Template

```
feat: Complete Phase 2/3 - [Module Name]

Brief description of changes.

## Changes
- Created [new module] with [functionality]
- Refactored [old module] as facade
- Added deprecation warnings
- Tests: [X] tests (all passing)

## Impact
- LOC reduction: ~[X] lines
- Test coverage: [X]%
- Backward compatibility: Maintained

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**END OF GUIDE**
