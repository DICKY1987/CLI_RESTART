"""
Workflow Execution Optimizer

Analyzes workflow execution patterns and provides optimization recommendations
for improving parallel execution performance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class OptimizationRecommendation:
    """A single optimization recommendation."""

    category: str  # "thread_pool", "batching", "scheduling", "resource_allocation"
    severity: str  # "low", "medium", "high"
    title: str
    description: str
    expected_improvement: str  # e.g., "10-20% faster"
    implementation_effort: str  # "low", "medium", "high"


class WorkflowOptimizer:
    """Optimizes workflow execution based on performance data."""

    def __init__(self):
        self.recommendations: list[OptimizationRecommendation] = []

    def analyze_workflow(
        self,
        workflow: dict[str, Any],
        execution_history: Optional[list[dict[str, Any]]] = None
    ) -> list[OptimizationRecommendation]:
        """
        Analyze a workflow and provide optimization recommendations.

        Args:
            workflow: Workflow definition
            execution_history: Historical execution data

        Returns:
            List of optimization recommendations
        """
        recommendations = []

        # Analyze workflow structure
        recommendations.extend(self._analyze_workflow_structure(workflow))

        # Analyze parallelization opportunities
        recommendations.extend(self._analyze_parallelization(workflow))

        # If we have execution history, analyze performance
        if execution_history:
            recommendations.extend(self._analyze_execution_history(execution_history))

        self.recommendations = recommendations
        return recommendations

    def _analyze_workflow_structure(
        self, workflow: dict[str, Any]
    ) -> list[OptimizationRecommendation]:
        """Analyze workflow structure for optimization opportunities."""
        recommendations = []
        steps = workflow.get("steps", [])

        # Check for unnecessarily sequential steps
        sequential_count = 0
        for i in range(len(steps) - 1):
            current_step = steps[i]
            next_step = steps[i + 1]

            # Check if steps could run in parallel
            current_files = set(current_step.get("files", []))
            next_files = set(next_step.get("files", []))

            # If no file overlap, could potentially parallelize
            if current_files and next_files and not (current_files & next_files):
                sequential_count += 1

        if sequential_count > 2:
            recommendations.append(
                OptimizationRecommendation(
                    category="scheduling",
                    severity="medium",
                    title="Parallelization Opportunity",
                    description=f"Found {sequential_count} sequential steps that could potentially run in parallel",
                    expected_improvement="20-40% faster",
                    implementation_effort="medium"
                )
            )

        # Check workflow size
        if len(steps) > 20:
            recommendations.append(
                OptimizationRecommendation(
                    category="batching",
                    severity="low",
                    title="Large Workflow - Consider Batching",
                    description=f"Workflow has {len(steps)} steps. Consider breaking into smaller batches.",
                    expected_improvement="Better resource utilization",
                    implementation_effort="medium"
                )
            )

        return recommendations

    def _analyze_parallelization(
        self, workflow: dict[str, Any]
    ) -> list[OptimizationRecommendation]:
        """Analyze parallelization configuration."""
        recommendations = []

        policy = workflow.get("policy", {})
        max_parallel = policy.get("max_parallel", 3)
        steps = workflow.get("steps", [])

        # Calculate optimal thread pool size
        optimal_size = self._calculate_optimal_pool_size(len(steps))

        if max_parallel < optimal_size and len(steps) > max_parallel * 2:
            recommendations.append(
                OptimizationRecommendation(
                    category="thread_pool",
                    severity="high",
                    title="Increase Thread Pool Size",
                    description=f"Current max_parallel={max_parallel}, optimal would be {optimal_size} for {len(steps)} steps",
                    expected_improvement="30-50% faster",
                    implementation_effort="low"
                )
            )
        elif max_parallel > optimal_size * 2:
            recommendations.append(
                OptimizationRecommendation(
                    category="thread_pool",
                    severity="medium",
                    title="Reduce Thread Pool Size",
                    description=f"Current max_parallel={max_parallel} may cause overhead. Consider {optimal_size}",
                    expected_improvement="10-15% less resource usage",
                    implementation_effort="low"
                )
            )

        return recommendations

    def _analyze_execution_history(
        self, execution_history: list[dict[str, Any]]
    ) -> list[OptimizationRecommendation]:
        """Analyze historical execution data."""
        recommendations = []

        if not execution_history:
            return recommendations

        # Analyze average execution times
        total_times = [ex.get("total_execution_time", 0) for ex in execution_history]
        if total_times:
            avg_time = sum(total_times) / len(total_times)

            # Check for consistently slow executions
            slow_executions = sum(1 for t in total_times if t > avg_time * 1.5)
            if slow_executions > len(total_times) * 0.3:  # More than 30% slow
                recommendations.append(
                    OptimizationRecommendation(
                        category="resource_allocation",
                        severity="high",
                        title="Frequent Slow Executions",
                        description=f"{slow_executions}/{len(total_times)} executions are significantly slower than average",
                        expected_improvement="Investigate bottlenecks",
                        implementation_effort="high"
                    )
                )

        # Analyze failure rates
        failed = sum(1 for ex in execution_history if not ex.get("success", True))
        if failed > 0:
            failure_rate = failed / len(execution_history)
            if failure_rate > 0.1:  # More than 10% failure rate
                recommendations.append(
                    OptimizationRecommendation(
                        category="resource_allocation",
                        severity="high",
                        title="High Failure Rate",
                        description=f"Failure rate: {failure_rate:.1%}. Review error handling and resource allocation",
                        expected_improvement="Improved reliability",
                        implementation_effort="medium"
                    )
                )

        return recommendations

    def _calculate_optimal_pool_size(self, task_count: int) -> int:
        """Calculate optimal thread pool size based on task count."""
        import os

        cpu_count = os.cpu_count() or 4

        # Amdahl's law consideration
        # For I/O bound tasks (most workflow steps), use more threads
        # For CPU bound tasks, stay closer to CPU count

        if task_count < cpu_count:
            return task_count

        # For I/O bound: CPU count + small multiplier
        # Cap at 32 to avoid excessive overhead
        optimal = min(cpu_count * 2 + 4, 32)

        # Don't exceed task count
        return min(optimal, task_count)

    def optimize_thread_pool_config(
        self,
        workflow: dict[str, Any],
        target_utilization: float = 0.75
    ) -> dict[str, Any]:
        """
        Generate optimized thread pool configuration.

        Args:
            workflow: Workflow definition
            target_utilization: Target CPU utilization (0.0-1.0)

        Returns:
            Optimized configuration dictionary
        """
        steps = workflow.get("steps", [])
        step_count = len(steps)

        optimal_size = self._calculate_optimal_pool_size(step_count)

        # Adjust based on target utilization
        adjusted_size = int(optimal_size * target_utilization)
        adjusted_size = max(1, min(adjusted_size, 32))

        return {
            "max_parallel": adjusted_size,
            "thread_pool_size": adjusted_size,
            "queue_size": step_count,
            "timeout_per_step": 300,  # 5 minutes default
            "enable_adaptive_sizing": True,
            "min_threads": max(1, adjusted_size // 2),
            "max_threads": adjusted_size * 2,
        }

    def get_recommendations_by_priority(self) -> dict[str, list[OptimizationRecommendation]]:
        """Group recommendations by severity."""
        grouped = {
            "high": [],
            "medium": [],
            "low": []
        }

        for rec in self.recommendations:
            grouped[rec.severity].append(rec)

        return grouped

    def generate_optimization_report(self) -> str:
        """Generate a formatted optimization report."""
        if not self.recommendations:
            return "No optimization recommendations at this time."

        report_lines = ["# Workflow Optimization Report\n"]

        grouped = self.get_recommendations_by_priority()

        for severity in ["high", "medium", "low"]:
            recs = grouped[severity]
            if not recs:
                continue

            severity_label = severity.upper()
            report_lines.append(f"\n## {severity_label} Priority ({len(recs)} items)\n")

            for i, rec in enumerate(recs, 1):
                report_lines.append(f"### {i}. {rec.title}")
                report_lines.append(f"**Category**: {rec.category}")
                report_lines.append(f"**Description**: {rec.description}")
                report_lines.append(f"**Expected Improvement**: {rec.expected_improvement}")
                report_lines.append(f"**Implementation Effort**: {rec.implementation_effort}")
                report_lines.append("")

        return "\n".join(report_lines)


__all__ = [
    "OptimizationRecommendation",
    "WorkflowOptimizer"
]
