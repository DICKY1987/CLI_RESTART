"""Chaos tests for network failure scenarios."""

from __future__ import annotations

import time
from pathlib import Path
from unittest import mock

import pytest
import yaml

from cli_multi_rapid.resilience.circuit_breaker import SimpleCircuitBreaker
from cli_multi_rapid.workflow_runner import WorkflowRunner


@pytest.fixture
def ai_workflow(tmp_path: Path):
    """Create workflow that uses AI adapter (requires network)."""
    workflow = {
        "name": "AI Workflow",
        "inputs": {"files": ["src/*.py"]},
        "steps": [
            {
                "id": "1.001",
                "name": "AI Analysis",
                "actor": "ai_analyst",
                "with": {"model": "claude-3-sonnet"},
            }
        ],
    }
    workflow_file = tmp_path / "ai_workflow.yaml"
    workflow_file.write_text(yaml.dump(workflow))
    return workflow_file


def test_circuit_breaker_opens_on_repeated_failures():
    """Test circuit breaker opens after threshold failures."""
    cb = SimpleCircuitBreaker(failure_threshold=3, reset_timeout=1.0)

    def failing_call():
        raise ConnectionError("Network failure")

    # First 3 failures should increment counter
    for i in range(3):
        with pytest.raises(ConnectionError):
            cb.call(failing_call)

    # Circuit should now be open
    assert cb.is_open()

    # Subsequent calls should fail fast without calling function
    with pytest.raises(RuntimeError, match="circuit_open"):
        cb.call(lambda: 42)


def test_circuit_breaker_recovers_after_timeout():
    """Test circuit breaker enters half-open state after timeout."""
    cb = SimpleCircuitBreaker(failure_threshold=2, reset_timeout=0.5)

    def failing_call():
        raise ConnectionError("Network failure")

    # Trigger circuit to open
    for _ in range(2):
        with pytest.raises(ConnectionError):
            cb.call(failing_call)

    assert cb.is_open()

    # Wait for reset timeout
    time.sleep(0.6)

    # Should allow a test call (half-open)
    assert not cb.is_open()

    # Successful call should close circuit
    result = cb.call(lambda: "success")
    assert result == "success"
    assert not cb.is_open()


def test_workflow_degrades_gracefully_on_network_failure(ai_workflow: Path):
    """Test workflow handles network failures gracefully."""

    with mock.patch(
        "cli_multi_rapid.adapters.ai_analyst.AIAnalyst.execute"
    ) as mock_execute:
        # Simulate network failure
        mock_execute.side_effect = ConnectionError("API unavailable")

        runner = WorkflowRunner(str(ai_workflow))
        result = runner.run()

        # Workflow should fail but not crash
        assert not result.success
        assert result.error
        assert "network" in result.error.lower() or "connection" in result.error.lower()


def test_retry_with_exponential_backoff():
    """Test exponential backoff retry logic."""
    from cli_multi_rapid.resilience.retry import retry_with_backoff

    call_times = []

    @retry_with_backoff(max_retries=3, base_delay=0.1, max_delay=1.0)
    def flaky_function(attempt=[0]):
        call_times.append(time.time())
        attempt[0] += 1
        if attempt[0] < 3:
            raise ConnectionError("Temporary failure")
        return "success"

    start = time.time()
    result = flaky_function()

    assert result == "success"
    assert len(call_times) == 3

    # Verify exponential backoff
    if len(call_times) >= 2:
        first_delay = call_times[1] - call_times[0]
        assert first_delay >= 0.1  # First retry after base_delay

    if len(call_times) >= 3:
        second_delay = call_times[2] - call_times[1]
        assert second_delay >= first_delay  # Exponential increase


def test_resource_exhaustion_handling(tmp_path: Path):
    """Test system handles resource exhaustion gracefully."""
    workflow = {
        "name": "Resource Heavy",
        "inputs": {"files": ["**/*.py"]},  # Large file set
        "policy": {"max_tokens": 1000000},  # Unrealistic limit
        "steps": [
            {
                "id": "1.001",
                "name": "Heavy Processing",
                "actor": "ai_editor",
                "with": {"model": "claude-3-opus"},
            }
        ],
    }
    workflow_file = tmp_path / "heavy.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    with mock.patch(
        "cli_multi_rapid.adapters.ai_editor.AIEditor.execute"
    ) as mock_execute:
        # Simulate memory/resource error
        mock_execute.side_effect = MemoryError("Out of memory")

        runner = WorkflowRunner(str(workflow_file))
        result = runner.run()

        # Should handle gracefully without crashing
        assert not result.success
        assert "memory" in result.error.lower() or "resource" in result.error.lower()


def test_dependency_unavailable_fallback(tmp_path: Path):
    """Test fallback behavior when dependencies unavailable."""
    workflow = {
        "name": "With Fallback",
        "inputs": {},
        "steps": [
            {
                "id": "1.001",
                "name": "Primary",
                "actor": "ai_analyst",
                "with": {"model": "claude-3-opus"},
                "fallback": {
                    "actor": "ai_analyst",
                    "with": {"model": "claude-3-sonnet"},  # Fallback model
                },
            }
        ],
    }
    workflow_file = tmp_path / "fallback.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    with mock.patch(
        "cli_multi_rapid.adapters.ai_analyst.AIAnalyst.execute"
    ) as mock_execute:
        # Primary fails, fallback succeeds
        mock_execute.side_effect = [
            ConnectionError("Primary unavailable"),
            {"status": "success", "result": "fallback result"},
        ]

        runner = WorkflowRunner(str(workflow_file))
        result = runner.run()

        # Fallback should succeed
        assert result.success or "fallback" in str(result)
        assert mock_execute.call_count == 2  # Primary + fallback


def test_timeout_prevents_hanging(tmp_path: Path):
    """Test timeout mechanism prevents workflows from hanging."""
    workflow = {
        "name": "Timeout Test",
        "inputs": {},
        "policy": {"timeout_seconds": 2},  # Short timeout
        "steps": [
            {
                "id": "1.001",
                "name": "Slow Step",
                "actor": "ai_analyst",
                "with": {"model": "claude-3-opus"},
            }
        ],
    }
    workflow_file = tmp_path / "timeout.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    with mock.patch(
        "cli_multi_rapid.adapters.ai_analyst.AIAnalyst.execute"
    ) as mock_execute:
        # Simulate slow response
        def slow_execute(*args, **kwargs):
            time.sleep(5)  # Longer than timeout
            return {"status": "success"}

        mock_execute.side_effect = slow_execute

        start = time.time()
        runner = WorkflowRunner(str(workflow_file))
        result = runner.run()
        duration = time.time() - start

        # Should timeout before completion
        assert duration < 4.0  # Some buffer but well under slow_execute time
        assert not result.success
        assert "timeout" in result.error.lower()
