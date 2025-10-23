#!/usr/bin/env python3
"""
Tests for core.executor module

Test coverage for StepExecutor class and step execution logic.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass

from src.cli_multi_rapid.core.executor import StepExecutor, StepExecutionResult
from src.cli_multi_rapid.adapters.base_adapter import AdapterResult
from src.cli_multi_rapid.router import Router
from src.cli_multi_rapid.cost_tracker import CostTracker


# Fixtures

@pytest.fixture
def mock_router():
    """Create a mock router."""
    return Mock(spec=Router)


@pytest.fixture
def mock_cost_tracker():
    """Create a mock cost tracker."""
    return Mock(spec=CostTracker)


@pytest.fixture
def mock_adapter():
    """Create a mock adapter."""
    adapter = Mock()
    adapter.is_available.return_value = True
    adapter.estimate_cost.return_value = 1000
    adapter.execute.return_value = AdapterResult(
        success=True,
        output="Step completed successfully",
        artifacts=["artifacts/output.json"],
        tokens_used=500,
        metadata={"key": "value"}
    )
    return adapter


@pytest.fixture
def executor(mock_router, mock_cost_tracker):
    """Create a StepExecutor instance."""
    return StepExecutor(
        router=mock_router,
        cost_tracker=mock_cost_tracker,
        dry_run=False
    )


@pytest.fixture
def valid_step():
    """Create a valid step definition."""
    return {
        "id": "1.001",
        "name": "Test Step",
        "actor": "test_adapter",
        "with": {"param": "value"},
        "emits": ["artifacts/output.json"]
    }


# Test StepExecutor Initialization

def test_executor_initialization(mock_router, mock_cost_tracker):
    """Test StepExecutor initialization."""
    executor = StepExecutor(
        router=mock_router,
        cost_tracker=mock_cost_tracker,
        dry_run=False
    )

    assert executor.router == mock_router
    assert executor.cost_tracker == mock_cost_tracker
    assert executor.dry_run is False


def test_executor_initialization_without_cost_tracker(mock_router):
    """Test StepExecutor initialization without cost tracker."""
    executor = StepExecutor(router=mock_router)

    assert executor.router == mock_router
    assert executor.cost_tracker is None
    assert executor.dry_run is False


def test_executor_initialization_with_dry_run(mock_router):
    """Test StepExecutor initialization with dry_run=True."""
    executor = StepExecutor(router=mock_router, dry_run=True)

    assert executor.dry_run is True


# Test Step Validation

def test_validate_step_success(executor, valid_step):
    """Test step validation with valid step."""
    # Should not raise any exception
    executor._validate_step(valid_step)


def test_validate_step_missing_id(executor):
    """Test step validation with missing id."""
    invalid_step = {"name": "Test", "actor": "test"}

    with pytest.raises(ValueError, match="missing required field: id"):
        executor._validate_step(invalid_step)


def test_validate_step_missing_name(executor):
    """Test step validation with missing name."""
    invalid_step = {"id": "1.001", "actor": "test"}

    with pytest.raises(ValueError, match="missing required field: name"):
        executor._validate_step(invalid_step)


def test_validate_step_missing_actor(executor):
    """Test step validation with missing actor."""
    invalid_step = {"id": "1.001", "name": "Test"}

    with pytest.raises(ValueError, match="missing required field: actor"):
        executor._validate_step(invalid_step)


# Test Step Execution - Success Cases

def test_execute_step_success(executor, mock_router, mock_adapter, valid_step, mock_cost_tracker):
    """Test successful step execution."""
    mock_router.get_adapter.return_value = mock_adapter

    result = executor.execute_step(valid_step)

    assert result.success is True
    assert result.step_id == "1.001"
    assert result.output == "Step completed successfully"
    assert result.artifacts == ["artifacts/output.json"]
    assert result.tokens_used == 500
    assert result.error is None
    assert result.execution_time_seconds > 0

    # Verify adapter was called
    mock_router.get_adapter.assert_called_once_with("test_adapter")
    mock_adapter.is_available.assert_called_once()
    mock_adapter.execute.assert_called_once_with(valid_step, None, None)

    # Verify cost tracking
    mock_cost_tracker.add_tokens.assert_called_once_with("test_adapter", 500)


def test_execute_step_with_context(executor, mock_router, mock_adapter, valid_step):
    """Test step execution with context."""
    mock_router.get_adapter.return_value = mock_adapter
    context = {"workflow_name": "test", "inputs": {"key": "value"}}

    result = executor.execute_step(valid_step, context=context)

    assert result.success is True
    mock_adapter.execute.assert_called_once_with(valid_step, context, None)


def test_execute_step_with_files(executor, mock_router, mock_adapter, valid_step):
    """Test step execution with file pattern."""
    mock_router.get_adapter.return_value = mock_adapter
    files = "src/**/*.py"

    result = executor.execute_step(valid_step, files=files)

    assert result.success is True
    mock_adapter.execute.assert_called_once_with(valid_step, None, files)


def test_execute_step_no_cost_tracker(mock_router, mock_adapter, valid_step):
    """Test step execution without cost tracker."""
    executor = StepExecutor(router=mock_router, cost_tracker=None)
    mock_router.get_adapter.return_value = mock_adapter

    result = executor.execute_step(valid_step)

    assert result.success is True
    # No error should occur even without cost tracker


def test_execute_step_zero_tokens(executor, mock_router, mock_adapter, valid_step, mock_cost_tracker):
    """Test step execution with zero tokens used."""
    mock_adapter.execute.return_value = AdapterResult(
        success=True,
        output="Done",
        tokens_used=0
    )
    mock_router.get_adapter.return_value = mock_adapter

    result = executor.execute_step(valid_step)

    assert result.success is True
    assert result.tokens_used == 0
    # Cost tracker should not be called for zero tokens
    mock_cost_tracker.add_tokens.assert_not_called()


# Test Step Execution - Dry Run

def test_execute_step_dry_run(mock_router, valid_step):
    """Test step execution in dry-run mode."""
    executor = StepExecutor(router=mock_router, dry_run=True)

    result = executor.execute_step(valid_step)

    assert result.success is True
    assert result.step_id == "1.001"
    assert "[DRY RUN]" in result.output
    assert result.artifacts == ["artifacts/output.json"]
    assert result.tokens_used == 0
    assert result.metadata == {"dry_run": True}

    # Adapter should not be called in dry-run mode
    mock_router.get_adapter.assert_not_called()


# Test Step Execution - Failure Cases

def test_execute_step_missing_actor(executor, mock_router):
    """Test step execution with missing actor."""
    invalid_step = {"id": "1.001", "name": "Test"}

    result = executor.execute_step(invalid_step)

    assert result.success is False
    assert "missing required field: actor" in result.error


def test_execute_step_actor_not_found(executor, mock_router, valid_step):
    """Test step execution when adapter not found."""
    mock_router.get_adapter.return_value = None

    result = executor.execute_step(valid_step)

    assert result.success is False
    assert "Adapter 'test_adapter' not found" in result.error


def test_execute_step_adapter_not_available(executor, mock_router, mock_adapter, valid_step):
    """Test step execution when adapter is not available."""
    mock_adapter.is_available.return_value = False
    mock_router.get_adapter.return_value = mock_adapter

    result = executor.execute_step(valid_step)

    assert result.success is False
    assert "not available" in result.error


def test_execute_step_adapter_execution_failure(executor, mock_router, mock_adapter, valid_step):
    """Test step execution when adapter returns failure."""
    mock_adapter.execute.return_value = AdapterResult(
        success=False,
        error="Execution failed",
        tokens_used=0
    )
    mock_router.get_adapter.return_value = mock_adapter

    result = executor.execute_step(valid_step)

    assert result.success is False
    assert result.error == "Execution failed"


def test_execute_step_adapter_raises_exception(executor, mock_router, mock_adapter, valid_step):
    """Test step execution when adapter raises exception."""
    mock_adapter.execute.side_effect = Exception("Unexpected error")
    mock_router.get_adapter.return_value = mock_adapter

    result = executor.execute_step(valid_step)

    assert result.success is False
    assert "Unexpected error" in result.error


# Test Cost Estimation

def test_estimate_step_cost(executor, mock_router, mock_adapter, valid_step):
    """Test cost estimation for a step."""
    mock_router.get_adapter.return_value = mock_adapter

    cost = executor.estimate_step_cost(valid_step)

    assert cost == 1000
    mock_adapter.estimate_cost.assert_called_once_with(valid_step)


def test_estimate_step_cost_no_actor(executor):
    """Test cost estimation with no actor."""
    step = {"id": "1.001", "name": "Test"}

    cost = executor.estimate_step_cost(step)

    assert cost == 0


def test_estimate_step_cost_adapter_not_found(executor, mock_router, valid_step):
    """Test cost estimation when adapter not found."""
    mock_router.get_adapter.return_value = None

    cost = executor.estimate_step_cost(valid_step)

    assert cost == 0


# Test Batch Execution

def test_execute_steps_batch(executor, mock_router, mock_adapter):
    """Test batch execution of multiple steps."""
    steps = [
        {"id": "1.001", "name": "Step 1", "actor": "test1"},
        {"id": "1.002", "name": "Step 2", "actor": "test2"},
    ]
    mock_router.get_adapter.return_value = mock_adapter

    results = executor.execute_steps_batch(steps)

    assert len(results) == 2
    assert all(r.success for r in results)


def test_execute_steps_batch_with_context_update(executor, mock_router, mock_adapter):
    """Test batch execution updates context with step results."""
    steps = [
        {"id": "1.001", "name": "Step 1", "actor": "test1"},
        {"id": "1.002", "name": "Step 2", "actor": "test2"},
    ]
    mock_router.get_adapter.return_value = mock_adapter
    context = {"step_results": {}}

    results = executor.execute_steps_batch(steps, context=context)

    assert len(results) == 2
    assert "1.001" in context["step_results"]
    assert "1.002" in context["step_results"]
    assert context["step_results"]["1.001"]["success"] is True


def test_execute_steps_batch_empty_list(executor):
    """Test batch execution with empty step list."""
    results = executor.execute_steps_batch([])

    assert results == []


# Test Step Validation (Batch)

def test_validate_steps_all_valid(executor, mock_router, mock_adapter):
    """Test validation of all valid steps."""
    steps = [
        {"id": "1.001", "name": "Step 1", "actor": "test1"},
        {"id": "1.002", "name": "Step 2", "actor": "test2"},
    ]
    mock_router.get_adapter.return_value = mock_adapter

    report = executor.validate_steps(steps)

    assert report["valid"] is True
    assert report["total_steps"] == 2
    assert len(report["errors"]) == 0
    assert len(report["warnings"]) == 0


def test_validate_steps_with_errors(executor, mock_router):
    """Test validation with invalid steps."""
    steps = [
        {"id": "1.001", "name": "Step 1", "actor": "test1"},
        {"id": "1.002", "name": "Step 2"},  # Missing actor
    ]
    mock_router.get_adapter.return_value = Mock()

    report = executor.validate_steps(steps)

    assert report["valid"] is False
    assert report["total_steps"] == 2
    assert len(report["errors"]) == 1
    assert report["errors"][0]["step_id"] == "1.002"


def test_validate_steps_adapter_not_found(executor, mock_router):
    """Test validation when adapter not found."""
    steps = [
        {"id": "1.001", "name": "Step 1", "actor": "missing_adapter"},
    ]
    mock_router.get_adapter.return_value = None

    report = executor.validate_steps(steps)

    assert report["valid"] is False
    assert len(report["errors"]) == 1
    assert "not found" in report["errors"][0]["error"]


def test_validate_steps_adapter_not_available(executor, mock_router, mock_adapter):
    """Test validation when adapter is not available."""
    steps = [
        {"id": "1.001", "name": "Step 1", "actor": "test_adapter"},
    ]
    mock_adapter.is_available.return_value = False
    mock_router.get_adapter.return_value = mock_adapter

    report = executor.validate_steps(steps)

    assert report["valid"] is True  # Warnings don't fail validation
    assert len(report["warnings"]) == 1
    assert "not currently available" in report["warnings"][0]["warning"]


def test_validate_steps_empty_list(executor):
    """Test validation of empty step list."""
    report = executor.validate_steps([])

    assert report["valid"] is True
    assert report["total_steps"] == 0
    assert len(report["errors"]) == 0
