#!/usr/bin/env python3
"""
Step Executor - Execute individual workflow steps

Handles step validation, routing, execution, and result collection.
Isolated from orchestration logic for better testability.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import AdapterResult
from ..cost_tracker import CostTracker
from ..router import Router


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

    def execute_steps_batch(
        self,
        steps: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        files: Optional[str] = None
    ) -> List[StepExecutionResult]:
        """
        Execute multiple steps sequentially.

        Args:
            steps: List of step definitions
            context: Shared execution context
            files: File pattern for execution

        Returns:
            List of StepExecutionResult objects
        """
        results = []
        for step in steps:
            result = self.execute_step(step, context, files)
            results.append(result)

            # Update context with step result for subsequent steps
            if context is not None:
                step_id = step.get("id", "unknown")
                if "step_results" not in context:
                    context["step_results"] = {}
                context["step_results"][step_id] = {
                    "success": result.success,
                    "output": result.output,
                    "artifacts": result.artifacts,
                    "metadata": result.metadata,
                }

        return results

    def validate_steps(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple step definitions.

        Args:
            steps: List of step definitions to validate

        Returns:
            Validation report with any errors
        """
        errors = []
        warnings = []

        for i, step in enumerate(steps):
            step_id = step.get("id", f"step_{i}")

            try:
                self._validate_step(step)
            except ValueError as e:
                errors.append({"step_id": step_id, "error": str(e)})
                continue

            # Check adapter availability
            actor = step.get("actor")
            if actor:
                adapter = self.router.get_adapter(actor)
                if not adapter:
                    errors.append({
                        "step_id": step_id,
                        "error": f"Adapter '{actor}' not found"
                    })
                elif not adapter.is_available():
                    warnings.append({
                        "step_id": step_id,
                        "warning": f"Adapter '{actor}' is not currently available"
                    })

        return {
            "valid": len(errors) == 0,
            "total_steps": len(steps),
            "errors": errors,
            "warnings": warnings
        }
