"""E2E tests for complete workflow execution from CLI to artifact verification."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from cli_multi_rapid.workflow_runner import WorkflowRunner


@pytest.fixture
def temp_workspace(tmp_path: Path):
    """Create isolated workspace for E2E tests."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    artifacts = workspace / "artifacts"
    artifacts.mkdir()
    return workspace


@pytest.fixture
def simple_workflow_yaml(temp_workspace: Path):
    """Create a simple linear workflow YAML."""
    workflow = {
        "name": "E2E Simple Workflow",
        "inputs": {"files": ["src/**/*.py"]},
        "policy": {"max_tokens": 10000, "prefer_deterministic": true},
        "steps": [
            {
                "id": "1.001",
                "name": "Syntax Validation",
                "actor": "syntax_validator",
                "with": {"language": "python"},
                "emits": [str(temp_workspace / "artifacts" / "syntax.json")],
            }
        ],
    }
    workflow_file = temp_workspace / "test_workflow.yaml"
    workflow_file.write_text(yaml.dump(workflow))
    return workflow_file


def test_simple_linear_workflow(simple_workflow_yaml: Path, temp_workspace: Path):
    """Execute a simple linear workflow and verify artifacts."""
    runner = WorkflowRunner(str(simple_workflow_yaml))
    result = runner.run()

    assert result.success, f"Workflow failed: {result.error}"
    assert result.artifacts, "No artifacts generated"

    # Verify artifact exists and is valid JSON
    artifact_path = temp_workspace / "artifacts" / "syntax.json"
    assert artifact_path.exists(), "Artifact file not created"

    artifact_data = json.loads(artifact_path.read_text())
    assert isinstance(artifact_data, dict), "Artifact is not valid JSON object"


def test_workflow_with_multiple_steps(temp_workspace: Path):
    """Execute workflow with multiple sequential steps."""
    workflow = {
        "name": "Multi-Step Workflow",
        "inputs": {"files": ["tests/**/*.py"]},
        "policy": {"max_tokens": 20000},
        "steps": [
            {
                "id": "1.001",
                "name": "Lint Check",
                "actor": "code_fixers",
                "with": {"tool": "ruff"},
                "emits": [str(temp_workspace / "artifacts" / "lint.json")],
            },
            {
                "id": "1.002",
                "name": "Type Check",
                "actor": "type_checker",
                "with": {"tool": "mypy"},
                "emits": [str(temp_workspace / "artifacts" / "types.json")],
            },
        ],
    }

    workflow_file = temp_workspace / "multi_step.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    runner = WorkflowRunner(str(workflow_file))
    result = runner.run()

    assert result.success, f"Multi-step workflow failed: {result.error}"
    assert len(result.artifacts) >= 2, "Not all step artifacts generated"


def test_workflow_dry_run_mode(simple_workflow_yaml: Path):
    """Test workflow execution in dry-run mode."""
    runner = WorkflowRunner(str(simple_workflow_yaml), dry_run=True)
    result = runner.run()

    # Dry run should succeed without actually executing
    assert result.success, "Dry run should succeed"
    # In dry run, artifacts might not be created
    assert result.dry_run_executed, "Dry run flag not set"


def test_workflow_with_invalid_step_fails_gracefully(temp_workspace: Path):
    """Test that invalid step configuration fails with clear error."""
    workflow = {
        "name": "Invalid Workflow",
        "inputs": {"files": []},
        "steps": [
            {
                "id": "1.001",
                "name": "Invalid Step",
                "actor": "nonexistent_actor",  # This actor doesn't exist
                "with": {},
            }
        ],
    }

    workflow_file = temp_workspace / "invalid.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    runner = WorkflowRunner(str(workflow_file))
    result = runner.run()

    assert not result.success, "Invalid workflow should fail"
    assert result.error, "Error message should be populated"
    assert "nonexistent_actor" in result.error.lower() or "actor" in result.error.lower()


def test_workflow_cleanup_on_completion(temp_workspace: Path):
    """Verify workflow cleans up temp files after execution."""
    workflow = {
        "name": "Cleanup Test",
        "inputs": {"files": ["tests/*.py"]},
        "steps": [
            {
                "id": "1.001",
                "name": "Test Step",
                "actor": "syntax_validator",
                "with": {"language": "python"},
            }
        ],
    }

    workflow_file = temp_workspace / "cleanup_test.yaml"
    workflow_file.write_text(yaml.dump(workflow))

    # Count temp files before
    temp_dir = Path(tempfile.gettempdir())
    temp_files_before = list(temp_dir.glob("cli_orchestrator_*"))

    runner = WorkflowRunner(str(workflow_file))
    runner.run()

    # Count temp files after - should not increase significantly
    temp_files_after = list(temp_dir.glob("cli_orchestrator_*"))

    # Allow for some temp files but not excessive
    assert len(temp_files_after) - len(temp_files_before) < 10, "Temp files not cleaned up"

