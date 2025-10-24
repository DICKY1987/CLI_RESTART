"""
Performance Profiler for Workflow Execution

This module provides benchmarking and profiling capabilities for workflow
execution, helping identify bottlenecks and optimize parallel execution.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json


@dataclass
class ExecutionMetrics:
    """Metrics for a single execution."""

    execution_id: str
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    thread_id: Optional[int] = None
    memory_used_mb: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        return self.duration * 1000


@dataclass
class ParallelExecutionReport:
    """Report of parallel execution performance."""

    total_operations: int
    successful_operations: int
    failed_operations: int
    total_duration: float
    average_duration: float
    min_duration: float
    max_duration: float
    parallel_efficiency: float  # 0.0-1.0, higher is better
    thread_pool_size: int
    operations_per_second: float
    bottlenecks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    detailed_metrics: list[ExecutionMetrics] = field(default_factory=list)


class PerformanceProfiler:
    """Profiles and benchmarks workflow execution performance."""

    def __init__(self):
        self.metrics: list[ExecutionMetrics] = []
        self.benchmarks: dict[str, list[float]] = {}

    def profile_execution(
        self,
        operation_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> tuple[Any, ExecutionMetrics]:
        """
        Profile a single operation execution.

        Args:
            operation_name: Name of the operation being profiled
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Tuple of (result, metrics)
        """
        import threading

        execution_id = f"{operation_name}_{int(time.time() * 1000)}"
        start_time = time.time()
        thread_id = threading.current_thread().ident

        success = True
        result = None
        error = None

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            success = False
            error = str(e)

        end_time = time.time()
        duration = end_time - start_time

        metrics = ExecutionMetrics(
            execution_id=execution_id,
            operation_name=operation_name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=success,
            thread_id=thread_id,
            metadata={"error": error} if error else {}
        )

        self.metrics.append(metrics)

        # Add to benchmarks for comparison
        if operation_name not in self.benchmarks:
            self.benchmarks[operation_name] = []
        self.benchmarks[operation_name].append(duration)

        return result, metrics

    def benchmark_parallel_execution(
        self,
        operations: list[tuple[str, Callable, tuple, dict]],
        max_workers: Optional[int] = None,
    ) -> ParallelExecutionReport:
        """
        Benchmark parallel execution of multiple operations.

        Args:
            operations: List of (name, func, args, kwargs) tuples
            max_workers: Max thread pool size (None = auto)

        Returns:
            Parallel execution report with metrics
        """
        if max_workers is None:
            import os
            max_workers = min(32, (os.cpu_count() or 1) + 4)

        start_time = time.time()
        execution_metrics: list[ExecutionMetrics] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_op = {}

            for op_name, func, args, kwargs in operations:
                future = executor.submit(
                    self.profile_execution,
                    op_name,
                    func,
                    *args,
                    **kwargs
                )
                future_to_op[future] = op_name

            for future in as_completed(future_to_op):
                try:
                    result, metrics = future.result()
                    execution_metrics.append(metrics)
                except Exception as e:
                    # Create failed metric
                    op_name = future_to_op[future]
                    metrics = ExecutionMetrics(
                        execution_id=f"{op_name}_failed",
                        operation_name=op_name,
                        start_time=start_time,
                        end_time=time.time(),
                        duration=0.0,
                        success=False,
                        metadata={"error": str(e)}
                    )
                    execution_metrics.append(metrics)

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate metrics
        successful = [m for m in execution_metrics if m.success]
        failed = [m for m in execution_metrics if not m.success]

        durations = [m.duration for m in execution_metrics if m.success]
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0

        # Calculate parallel efficiency
        # Efficiency = (sum of individual durations) / (total wall time * workers)
        total_work_time = sum(durations)
        theoretical_time = total_duration * max_workers
        efficiency = total_work_time / theoretical_time if theoretical_time > 0 else 0

        ops_per_second = len(successful) / total_duration if total_duration > 0 else 0

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(execution_metrics, avg_duration)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            execution_metrics,
            max_workers,
            efficiency
        )

        report = ParallelExecutionReport(
            total_operations=len(execution_metrics),
            successful_operations=len(successful),
            failed_operations=len(failed),
            total_duration=total_duration,
            average_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            parallel_efficiency=efficiency,
            thread_pool_size=max_workers,
            operations_per_second=ops_per_second,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            detailed_metrics=execution_metrics
        )

        return report

    def compare_thread_pool_sizes(
        self,
        operations: list[tuple[str, Callable, tuple, dict]],
        pool_sizes: list[int] = None,
    ) -> dict[int, ParallelExecutionReport]:
        """
        Compare performance across different thread pool sizes.

        Args:
            operations: Operations to benchmark
            pool_sizes: List of pool sizes to test (default: [1, 2, 4, 8, 16])

        Returns:
            Dictionary mapping pool size to performance report
        """
        if pool_sizes is None:
            pool_sizes = [1, 2, 4, 8, 16]

        results = {}

        for pool_size in pool_sizes:
            print(f"Testing with pool size: {pool_size}")
            report = self.benchmark_parallel_execution(operations, max_workers=pool_size)
            results[pool_size] = report

        return results

    def _identify_bottlenecks(
        self,
        metrics: list[ExecutionMetrics],
        avg_duration: float
    ) -> list[str]:
        """Identify operations that are bottlenecks."""
        bottlenecks = []

        # Operations taking >2x average time
        threshold = avg_duration * 2

        for metric in metrics:
            if metric.duration > threshold:
                bottlenecks.append(
                    f"{metric.operation_name}: {metric.duration:.2f}s (avg: {avg_duration:.2f}s)"
                )

        return bottlenecks

    def _generate_recommendations(
        self,
        metrics: list[ExecutionMetrics],
        pool_size: int,
        efficiency: float
    ) -> list[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Check efficiency
        if efficiency < 0.5:
            recommendations.append(
                f"Low parallel efficiency ({efficiency:.1%}). "
                "Consider reducing thread pool size or optimizing operation granularity."
            )
        elif efficiency > 0.9:
            recommendations.append(
                f"High parallel efficiency ({efficiency:.1%}). "
                "Consider increasing thread pool size for better throughput."
            )

        # Check for failed operations
        failed_count = sum(1 for m in metrics if not m.success)
        if failed_count > 0:
            recommendations.append(
                f"{failed_count} operations failed. Review error handling and retry logic."
            )

        # Check for variance in execution times
        durations = [m.duration for m in metrics if m.success]
        if durations:
            import statistics
            if len(durations) > 1:
                std_dev = statistics.stdev(durations)
                mean = statistics.mean(durations)
                cv = std_dev / mean if mean > 0 else 0

                if cv > 0.5:  # High coefficient of variation
                    recommendations.append(
                        f"High variance in execution times (CV: {cv:.2f}). "
                        "Consider grouping similar operations or load balancing."
                    )

        # Check pool size utilization
        unique_threads = len(set(m.thread_id for m in metrics if m.thread_id))
        if unique_threads < pool_size * 0.5:
            recommendations.append(
                f"Low thread utilization ({unique_threads}/{pool_size} threads used). "
                "Consider reducing pool size or increasing operation count."
            )

        return recommendations

    def get_operation_statistics(self, operation_name: str) -> dict[str, Any]:
        """Get statistics for a specific operation type."""
        durations = self.benchmarks.get(operation_name, [])

        if not durations:
            return {"error": f"No benchmarks for operation: {operation_name}"}

        import statistics

        return {
            "operation": operation_name,
            "executions": len(durations),
            "mean": statistics.mean(durations),
            "median": statistics.median(durations),
            "stdev": statistics.stdev(durations) if len(durations) > 1 else 0,
            "min": min(durations),
            "max": max(durations),
            "total_time": sum(durations)
        }

    def export_report(self, report: ParallelExecutionReport, output_file: Path):
        """Export performance report to JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        report_data = {
            "summary": {
                "total_operations": report.total_operations,
                "successful_operations": report.successful_operations,
                "failed_operations": report.failed_operations,
                "total_duration": report.total_duration,
                "average_duration": report.average_duration,
                "min_duration": report.min_duration,
                "max_duration": report.max_duration,
                "parallel_efficiency": report.parallel_efficiency,
                "thread_pool_size": report.thread_pool_size,
                "operations_per_second": report.operations_per_second,
            },
            "bottlenecks": report.bottlenecks,
            "recommendations": report.recommendations,
            "detailed_metrics": [
                {
                    "execution_id": m.execution_id,
                    "operation_name": m.operation_name,
                    "duration": m.duration,
                    "duration_ms": m.duration_ms,
                    "success": m.success,
                    "thread_id": m.thread_id,
                    "metadata": m.metadata
                }
                for m in report.detailed_metrics
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"Report exported to: {output_file}")


def create_benchmark_operations(count: int = 10) -> list[tuple[str, Callable, tuple, dict]]:
    """Create sample operations for benchmarking."""
    import random

    def sample_operation(operation_id: int, sleep_time: float):
        """Sample operation that sleeps for a specified time."""
        time.sleep(sleep_time)
        return f"Operation {operation_id} completed"

    operations = []
    for i in range(count):
        # Vary sleep times to simulate different workloads
        sleep_time = random.uniform(0.01, 0.1)
        operations.append((
            f"operation_{i}",
            sample_operation,
            (i, sleep_time),
            {}
        ))

    return operations


__all__ = [
    "ExecutionMetrics",
    "ParallelExecutionReport",
    "PerformanceProfiler",
    "create_benchmark_operations"
]
