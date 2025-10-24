#!/usr/bin/env python3
"""
Cost Estimator Adapter

Estimates workflow token usage and rough USD cost using the Router's
cost model and emits a structured artifact.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

from .base_adapter import AdapterResult, AdapterType, BaseAdapter

if TYPE_CHECKING:
    from ..router import Router


class CostEstimatorAdapter(BaseAdapter):
    """Adapter that estimates cost for a YAML workflow file."""

    def __init__(self) -> None:
        super().__init__(
            name="cost_estimator",
            adapter_type=AdapterType.DETERMINISTIC,
            description="Estimate workflow token/$$ cost and emit artifact",
        )

    def validate_step(self, step: dict[str, Any]) -> bool:
        """Validate that this adapter can execute the given step."""
        # Cost estimator just needs a workflow parameter
        params = step.get("with", {})
        return "workflow" in params or True  # Has default workflow

    def estimate_cost(self, step: dict[str, Any]) -> int:
        """Estimate the token cost of executing this step."""
        # Cost estimator itself uses no tokens (it's a deterministic tool)
        return 0

    def execute(
        self,
        step: dict[str, Any],
        context: dict[str, Any] | None = None,
        files: str | None = None,
    ) -> AdapterResult:
        self._log_execution_start(step)
        try:
            # Lazy import to avoid circular dependency
            from ..router import Router

            params = self._extract_with_params(step)
            emit_paths = self._extract_emit_paths(step)
            workflow_path = Path(
                params.get("workflow", ".ai/workflows/AI_WORKFLOW_DEMO.yaml")
            )

            if not workflow_path.exists():
                return AdapterResult(
                    success=False, error=f"Workflow not found: {workflow_path}"
                )

            import yaml

            with open(workflow_path, encoding="utf-8") as f:
                workflow = yaml.safe_load(f) or {}

            router = Router()
            estimate = router.estimate_workflow_cost(workflow)

            artifact_obj = {
                "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
                "type": "ai_cost_estimate",
                **estimate,
            }

            written = self._write_artifacts(emit_paths, artifact_obj)
            return AdapterResult(
                success=True, tokens_used=0, artifacts=written, metadata=estimate
            )
        except Exception as e:
            return AdapterResult(success=False, error=f"cost_estimator failed: {e}")
