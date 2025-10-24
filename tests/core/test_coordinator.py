#!/usr/bin/env python3
"""
Tests for core.coordinator module

Test coverage for WorkflowCoordinator class and workflow orchestration logic.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.cli_multi_rapid.core.coordinator import WorkflowCoordinator, WorkflowResult
from src.cli_multi_rapid.core.executor import StepExecutionResult, StepExecutor

# Fixtures

@pytest.fixture
def mock_executor():
    """Create a mock step executor."""
    executor = Mock(spec=StepExecutor)
    executor.execute_step.return_value = StepExecutionResult(
        step_id="1.001",
        success=True,
        output="Step completed",
        artifacts=["artifacts/output.json"],
        tokens_used=100,
        execution_time_seconds=0.5
    )
    executor.estimate_step_cost.return_value = 1000
    executor.validate_steps.return_value = {
        "valid": True,
        "total_steps": 1,
        "errors": [],
        "warnings": []
    }
    return executor


@pytest.fixture
def coordinator(mock_executor):
    """Create a WorkflowCoordinator instance."""
    return WorkflowCoordinator(executor=mock_executor)


@pytest.fixture
def simple_workflow_dict():
    """Create a simple workflow dictionary."""
    return {
        "name": "Test Workflow",
        "inputs": {"files": ["src/**/*.py"]},
        "policy": {"max_tokens": 10000, "fail_fast": True},
        "steps": [
            {
                "id": "1.001",
                "name": "Test Step",
                "actor": "test_adapter",
                "emits": ["artifacts/output.json"]
            }
        ]
    }


@pytest.fixture
def temp_workflow_file(simple_workflow_dict):
    """Create a temporary workflow YAML file."""
    import yaml

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(simple_workflow_dict, f)
        return f.name


# Test Coordinator Initialization

def test_coordinator_initialization(mock_executor):
    """Test WorkflowCoordinator initialization."""
    coordinator = WorkflowCoordinator(executor=mock_executor)

    assert coordinator.executor == mock_executor
    assert coordinator.schema_validator is None


def test_coordinator_initialization_with_validator(mock_executor):
    """Test WorkflowCoordinator initialization with schema validator."""
    validator = Mock()
    coordinator = WorkflowCoordinator(executor=mock_executor, schema_validator=validator)

    assert coordinator.schema_validator == validator


# Test Workflow Loading

def test_load_workflow(coordinator, temp_workflow_file):
    """Test loading workflow from YAML file."""
    workflow = coordinator._load_workflow(temp_workflow_file)

    assert workflow["name"] == "Test Workflow"
    assert "steps" in workflow
    assert len(workflow["steps"]) == 1


def test_load_workflow_file_not_found(coordinator):
    """Test loading non-existent workflow file."""
    with pytest.raises(FileNotFoundError, match="Workflow file not found"):
        coordinator._load_workflow("nonexistent.yaml")


def test_load_workflow_invalid_yaml(coordinator):
    """Test loading invalid YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content: [")
        temp_path = f.name

    with pytest.raises(Exception):
        coordinator._load_workflow(temp_path)


# Test Workflow Validation

def test_basic_validate_workflow_success(coordinator, simple_workflow_dict):
    """Test basic workflow validation with valid workflow."""
    coordinator._basic_validate_workflow(simple_workflow_dict)
    # Should not raise exception


def test_basic_validate_workflow_missing_steps(coordinator):
    """Test basic workflow validation with missing steps."""
    workflow = {"name": "Test"}

    with pytest.raises(ValueError, match="missing 'steps' field"):
        coordinator._basic_validate_workflow(workflow)


def test_basic_validate_workflow_steps_not_list(coordinator):
    """Test basic workflow validation with non-list steps."""
    workflow = {"steps": "not a list"}

    with pytest.raises(ValueError, match="must be a list"):
        coordinator._basic_validate_workflow(workflow)


def test_basic_validate_workflow_empty_steps(coordinator):
    """Test basic workflow validation with empty steps list."""
    workflow = {"steps": []}

    with pytest.raises(ValueError, match="must have at least one step"):
        coordinator._basic_validate_workflow(workflow)


# Test Context Management

def test_build_initial_context(coordinator, simple_workflow_dict):
    """Test building initial execution context."""
    context = coordinator._build_initial_context(simple_workflow_dict, None)

    assert context["workflow_name"] == "Test Workflow"
    assert context["inputs"] == {"files": ["src/**/*.py"]}
    assert context["policy"] == {"max_tokens": 10000, "fail_fast": True}
    assert context["step_results"] == {}


def test_build_initial_context_with_extra(coordinator, simple_workflow_dict):
    """Test building initial context with extra context."""
    extra = {"custom_key": "custom_value"}
    context = coordinator._build_initial_context(simple_workflow_dict, extra)

    assert context["custom_key"] == "custom_value"
    assert context["workflow_name"] == "Test Workflow"


def test_update_context(coordinator):
    """Test updating context with step result."""
    context = {"step_results": {}}
    step = {"id": "1.001", "name": "Test"}
    result = StepExecutionResult(
        step_id="1.001",
        success=True,
        output="Done",
        artifacts=["output.json"],
        tokens_used=100,
        execution_time_seconds=0.5,
        metadata={"key": "value"}
    )

    updated_context = coordinator._update_context(context, step, result)

    assert "1.001" in updated_context["step_results"]
    assert updated_context["step_results"]["1.001"]["success"] is True
    assert updated_context["step_results"]["1.001"]["output"] == "Done"


# Test Result Aggregation

def test_aggregate_results_all_success(coordinator):
    """Test aggregating results when all steps succeed."""
    step_results = [
        StepExecutionResult("1.001", True, "Done", ["out1.json"], 100, 0.5),
        StepExecutionResult("1.002", True, "Done", ["out2.json"], 200, 0.6),
    ]

    result = coordinator._aggregate_results(
        workflow_name="Test",
        step_results=step_results,
        total_time=1.5
    )

    assert result.success is True
    assert result.steps_executed == 2
    assert result.steps_succeeded == 2
    assert result.steps_failed == 0
    assert result.total_tokens_used == 300
    assert len(result.artifacts) == 2


def test_aggregate_results_with_failures(coordinator):
    """Test aggregating results with step failures."""
    step_results = [
        StepExecutionResult("1.001", True, "Done", ["out1.json"], 100, 0.5),
        StepExecutionResult("1.002", False, "", [], 0, 0.1, error="Failed"),
    ]

    result = coordinator._aggregate_results(
        workflow_name="Test",
        step_results=step_results,
        total_time=1.0
    )

    assert result.success is False
    assert result.steps_executed == 2
    assert result.steps_succeeded == 1
    assert result.steps_failed == 1


def test_aggregate_results_empty(coordinator):
    """Test aggregating empty results."""
    result = coordinator._aggregate_results(
        workflow_name="Test",
        step_results=[],
        total_time=0.1
    )

    assert result.success is True  # No failures = success
    assert result.steps_executed == 0
    assert result.total_tokens_used == 0


# Test Workflow Execution from Dictionary

def test_execute_workflow_from_dict_success(coordinator, mock_executor, simple_workflow_dict):
    """Test executing workflow from dictionary."""
    result = coordinator.execute_workflow_from_dict(simple_workflow_dict)

    assert result.success is True
    assert result.workflow_name == "Test Workflow"
    assert result.steps_executed == 1
    mock_executor.execute_step.assert_called_once()


def test_execute_workflow_from_dict_with_files(coordinator, mock_executor, simple_workflow_dict):
    """Test executing workflow from dictionary with file pattern."""
    result = coordinator.execute_workflow_from_dict(simple_workflow_dict, files="src/**/*.py")

    assert result.success is True
    mock_executor.execute_step.assert_called_once()


def test_execute_workflow_from_dict_fail_fast(coordinator, mock_executor, simple_workflow_dict):
    """Test workflow execution stops on failure with fail_fast."""
    # Add second step
    simple_workflow_dict["steps"].append({
        "id": "1.002",
        "name": "Second Step",
        "actor": "test_adapter"
    })

    # First step fails
    mock_executor.execute_step.side_effect = [
        StepExecutionResult("1.001", False, "", [], 0, 0.1, error="Failed"),
        StepExecutionResult("1.002", True, "Done", [], 0, 0.1),
    ]

    result = coordinator.execute_workflow_from_dict(simple_workflow_dict)

    # Should only execute first step due to fail_fast
    assert mock_executor.execute_step.call_count == 1
    assert result.success is False


def test_execute_workflow_from_dict_no_fail_fast(coordinator, mock_executor, simple_workflow_dict):
    """Test workflow execution continues on failure without fail_fast."""
    simple_workflow_dict["policy"]["fail_fast"] = False
    simple_workflow_dict["steps"].append({
        "id": "1.002",
        "name": "Second Step",
        "actor": "test_adapter"
    })

    # First step fails
    mock_executor.execute_step.side_effect = [
        StepExecutionResult("1.001", False, "", [], 0, 0.1, error="Failed"),
        StepExecutionResult("1.002", True, "Done", [], 0, 0.1),
    ]

    result = coordinator.execute_workflow_from_dict(simple_workflow_dict)

    # Should execute both steps
    assert mock_executor.execute_step.call_count == 2
    assert result.success is False  # Overall failure due to first step


# Test Workflow Execution from File

def test_execute_workflow_from_file(coordinator, mock_executor, temp_workflow_file):
    """Test executing workflow from YAML file."""
    result = coordinator.execute_workflow(temp_workflow_file)

    assert result.success is True
    assert result.workflow_name == "Test Workflow"
    mock_executor.execute_step.assert_called_once()


def test_execute_workflow_file_not_found(coordinator):
    """Test executing non-existent workflow file."""
    result = coordinator.execute_workflow("nonexistent.yaml")

    assert result.success is False
    assert "not found" in result.error.lower()


def test_execute_workflow_with_context(coordinator, mock_executor, temp_workflow_file):
    """Test executing workflow with extra context."""
    extra_context = {"custom_key": "custom_value"}
    result = coordinator.execute_workflow(temp_workflow_file, extra_context=extra_context)

    assert result.success is True


# Test Cost Estimation

def test_estimate_workflow_cost(coordinator, mock_executor, temp_workflow_file):
    """Test estimating workflow cost."""
    report = coordinator.estimate_workflow_cost(temp_workflow_file)

    assert "total_estimated_tokens" in report
    assert report["workflow_name"] == "Test Workflow"
    assert report["total_steps"] == 1
    assert len(report["step_estimates"]) == 1


def test_estimate_workflow_cost_file_not_found(coordinator):
    """Test cost estimation with non-existent file."""
    report = coordinator.estimate_workflow_cost("nonexistent.yaml")

    assert "error" in report
    assert report["total_estimated_tokens"] == 0


# Test Workflow Validation

def test_validate_workflow_file_success(coordinator, mock_executor, temp_workflow_file):
    """Test validating a valid workflow file."""
    report = coordinator.validate_workflow_file(temp_workflow_file)

    assert report["valid"] is True
    assert report["workflow_name"] == "Test Workflow"
    assert report["total_steps"] == 1
    assert len(report["errors"]) == 0


def test_validate_workflow_file_not_found(coordinator):
    """Test validating non-existent workflow file."""
    report = coordinator.validate_workflow_file("nonexistent.yaml")

    assert report["valid"] is False
    assert "error" in report


def test_validate_workflow_file_invalid_structure(coordinator):
    """Test validating workflow with invalid structure."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("name: Invalid\n")  # Missing steps
        temp_path = f.name

    report = coordinator.validate_workflow_file(temp_path)

    assert report["valid"] is False
    assert len(report["errors"]) > 0


# Test Multiple Steps Execution

def test_execute_multiple_steps(coordinator, mock_executor, simple_workflow_dict):
    """Test executing workflow with multiple steps."""
    simple_workflow_dict["steps"] = [
        {"id": "1.001", "name": "Step 1", "actor": "test1"},
        {"id": "1.002", "name": "Step 2", "actor": "test2"},
        {"id": "1.003", "name": "Step 3", "actor": "test3"},
    ]

    mock_executor.execute_step.return_value = StepExecutionResult(
        "1.001", True, "Done", [], 100, 0.5
    )

    result = coordinator.execute_workflow_from_dict(simple_workflow_dict)

    assert result.success is True
    assert result.steps_executed == 3
    assert mock_executor.execute_step.call_count == 3


# Test Error Handling

def test_execute_workflow_exception_during_execution(coordinator, mock_executor, simple_workflow_dict):
    """Test workflow execution when exception occurs during step execution."""
    mock_executor.execute_step.side_effect = Exception("Unexpected error")

    result = coordinator.execute_workflow_from_dict(simple_workflow_dict)

    assert result.success is False
    assert "Unexpected error" in result.error
