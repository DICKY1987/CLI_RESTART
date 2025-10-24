#!/usr/bin/env python3
"""
Workflow Coordinator - Orchestrate multi-step workflow execution

Handles workflow loading, validation, execution order, and result aggregation.
Separated from step execution for better separation of concerns.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .executor import StepExecutionResult, StepExecutor


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
    metadata: Dict[str, Any] = field(default_factory=dict)


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
            else:
                # Basic validation without schema
                self._basic_validate_workflow(workflow)

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
                total_time=time.time() - start_time,
                workflow_metadata=workflow.get("metadata", {})
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

    def execute_workflow_from_dict(
        self,
        workflow: Dict[str, Any],
        files: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Execute a workflow from dictionary (already loaded YAML).

        Args:
            workflow: Workflow definition dictionary
            files: File pattern for execution
            extra_context: Additional context to merge

        Returns:
            WorkflowResult with aggregated execution details
        """
        import time

        start_time = time.time()

        try:
            workflow_name = workflow.get("name", "unnamed_workflow")

            # Validate workflow
            if self.schema_validator:
                self._validate_workflow(workflow)
            else:
                self._basic_validate_workflow(workflow)

            # Build initial context
            context = self._build_initial_context(workflow, extra_context)

            # Execute steps
            steps = workflow.get("steps", [])
            step_results: List[StepExecutionResult] = []

            for step in steps:
                result = self.executor.execute_step(step, context, files)
                step_results.append(result)

                # Update context
                context = self._update_context(context, step, result)

                # Stop on failure if fail_fast
                if not result.success and workflow.get("policy", {}).get("fail_fast", True):
                    break

            # Aggregate results
            return self._aggregate_results(
                workflow_name=workflow_name,
                step_results=step_results,
                total_time=time.time() - start_time,
                workflow_metadata=workflow.get("metadata", {})
            )

        except Exception as e:
            return WorkflowResult(
                workflow_name=workflow.get("name", "unnamed_workflow"),
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
        workflow_file = Path(workflow_path)

        if not workflow_file.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

        with open(workflow_file, encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        if not workflow:
            raise ValueError(f"Empty or invalid workflow file: {workflow_path}")

        return workflow

    def _validate_workflow(self, workflow: Dict[str, Any]) -> None:
        """Validate workflow against schema."""
        if self.schema_validator:
            # Use provided schema validator
            self.schema_validator.validate(workflow)
        else:
            # Fallback to basic validation
            self._basic_validate_workflow(workflow)

    def _basic_validate_workflow(self, workflow: Dict[str, Any]) -> None:
        """Perform basic workflow validation without schema."""
        if not workflow.get("steps"):
            raise ValueError("Workflow missing 'steps' field")

        if not isinstance(workflow["steps"], list):
            raise ValueError("Workflow 'steps' must be a list")

        if len(workflow["steps"]) == 0:
            raise ValueError("Workflow must have at least one step")

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
        total_time: float,
        workflow_metadata: Optional[Dict[str, Any]] = None
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
            metadata=workflow_metadata or {}
        )

    def estimate_workflow_cost(self, workflow_path: str) -> Dict[str, Any]:
        """
        Estimate total token cost for a workflow.

        Args:
            workflow_path: Path to workflow YAML file

        Returns:
            Cost estimation report
        """
        try:
            workflow = self._load_workflow(workflow_path)
            steps = workflow.get("steps", [])

            total_estimated_tokens = 0
            step_estimates = []

            for step in steps:
                cost = self.executor.estimate_step_cost(step)
                total_estimated_tokens += cost
                step_estimates.append({
                    "step_id": step.get("id", "unknown"),
                    "actor": step.get("actor"),
                    "estimated_tokens": cost
                })

            return {
                "workflow_name": workflow.get("name", Path(workflow_path).stem),
                "total_steps": len(steps),
                "total_estimated_tokens": total_estimated_tokens,
                "step_estimates": step_estimates
            }

        except Exception as e:
            return {
                "error": str(e),
                "total_estimated_tokens": 0
            }

    def validate_workflow_file(self, workflow_path: str) -> Dict[str, Any]:
        """
        Validate a workflow file without executing it.

        Args:
            workflow_path: Path to workflow YAML file

        Returns:
            Validation report
        """
        try:
            # Load workflow
            workflow = self._load_workflow(workflow_path)

            # Validate workflow structure
            self._basic_validate_workflow(workflow)

            # Validate steps
            steps = workflow.get("steps", [])
            step_validation = self.executor.validate_steps(steps)

            return {
                "valid": step_validation["valid"],
                "workflow_name": workflow.get("name", Path(workflow_path).stem),
                "total_steps": len(steps),
                "errors": step_validation["errors"],
                "warnings": step_validation["warnings"]
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "errors": [{"error": str(e)}],
                "warnings": []
            }
