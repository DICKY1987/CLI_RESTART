"""Performance benchmarks for workflow execution."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
import yaml

from cli_multi_rapid.workflow_runner import WorkflowRunner


@pytest.fixture
def benchmark_workflow(tmp_path: Path):
    """Create workflow for performance testing."""
    workflow = {
        "name": "Performance Benchmark",
        "inputs": {"files": ["src/**/*.py"]},
        "policy": {"max_tokens": 5000},
        "steps": [
            {
                "id": "1.001",
                "name": "Quick Validation",
                "actor": "syntax_validator",
                "with": {"language": "python"},
            }
        ],
    }
    workflow_file = tmp_path / "benchmark.yaml"
    workflow_file.write_text(yaml.dump(workflow))
    return workflow_file


def test_workflow_execution_performance(benchmark, benchmark_workflow: Path):
    """Benchmark single workflow execution time."""

    def run_workflow():
        runner = WorkflowRunner(str(benchmark_workflow))
        result = runner.run()
        assert result.success

    # Run benchmark
    result = benchmark(run_workflow)

    # Assert performance targets
    assert result.stats["mean"] < 5.0, "Workflow execution too slow (>5s mean)"
    assert result.stats["stddev"] < 2.0, "Workflow execution too variable"


def test_workflow_startup_overhead(benchmark, tmp_path: Path):
    """Measure workflow initialization overhead."""

    workflow = {
        "name": "Minimal Workflow",
        "inputs": {},
        "steps": [],
    }
    workflow_file = tmp_path / "minimal.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    def init_workflow():
        WorkflowRunner(str(workflow_file))

    result = benchmark(init_workflow)

    # Initialization should be very fast
    assert result.stats["mean"] < 0.1, "Workflow initialization too slow"


def test_artifact_generation_performance(benchmark, tmp_path: Path):
    """Benchmark artifact generation speed."""
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()

    workflow = {
        "name": "Artifact Generation",
        "inputs": {"files": ["tests/*.py"]},
        "steps": [
            {
                "id": "1.001",
                "name": "Generate Artifacts",
                "actor": "vscode_diagnostics",
                "with": {"analyzers": ["python"]},
                "emits": [str(artifacts_dir / "diagnostics.json")],
            }
        ],
    }
    workflow_file = tmp_path / "artifacts.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    def run_with_artifacts():
        runner = WorkflowRunner(str(workflow_file))
        runner.run()

    result = benchmark(run_with_artifacts)

    # Artifact generation should be reasonably fast
    assert result.stats["mean"] < 10.0, "Artifact generation too slow"


def test_schema_validation_performance(benchmark, tmp_path: Path):
    """Benchmark JSON schema validation speed."""
    from cli_multi_rapid.validation import validate_workflow

    workflow = {
        "name": "Schema Test",
        "inputs": {"files": []},
        "policy": {"max_tokens": 1000},
        "steps": [{"id": "1.001", "name": "Test", "actor": "syntax_validator"}],
    }

    def validate():
        validate_workflow(workflow)

    result = benchmark(validate)

    # Schema validation should be very fast
    assert result.stats["mean"] < 0.01, "Schema validation too slow"


def test_concurrent_workflow_throughput(tmp_path: Path):
    """Test throughput with multiple concurrent workflows."""
    import concurrent.futures

    workflow = {
        "name": "Concurrent Test",
        "inputs": {},
        "steps": [
            {
                "id": "1.001",
                "name": "Quick Step",
                "actor": "syntax_validator",
                "with": {"language": "python"},
            }
        ],
    }
    workflow_file = tmp_path / "concurrent.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    def run_workflow():
        runner = WorkflowRunner(str(workflow_file))
        return runner.run()

    # Run 10 workflows concurrently
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_workflow) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    duration = time.time() - start

    # All workflows should succeed
    assert all(r.success for r in results), "Some workflows failed"

    # Should complete in reasonable time with concurrency benefit
    # 10 workflows sequentially would take ~10x single workflow time
    # With concurrency should be much faster
    assert duration < 30.0, "Concurrent execution too slow"

    # Calculate throughput
    throughput = len(results) / duration
    assert throughput > 0.5, f"Throughput too low: {throughput:.2f} workflows/sec"
