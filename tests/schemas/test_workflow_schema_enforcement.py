#!/usr/bin/env python3
"""Test that workflow schema enforces required step fields including IDs."""

import json
import pytest
import yaml
from jsonschema import validate, ValidationError
from pathlib import Path


@pytest.fixture
def workflow_schema():
    """Load the workflow schema."""
    schema_path = Path(__file__).parent.parent.parent / ".ai" / "schemas" / "workflow.schema.json"
    with open(schema_path) as f:
        return json.load(f)


def test_schema_enforces_step_id(workflow_schema):
    """Test that schema requires 'id' field in steps."""
    invalid_workflow = {
        "name": "Test Workflow",
        "steps": [
            {
                # Missing 'id'
                "name": "Test Step",
                "actor": "test_adapter"
            }
        ]
    }
    
    with pytest.raises(ValidationError, match="'id' is a required property"):
        validate(instance=invalid_workflow, schema=workflow_schema)


def test_schema_enforces_step_name(workflow_schema):
    """Test that schema requires 'name' field in steps."""
    invalid_workflow = {
        "name": "Test Workflow",
        "steps": [
            {
                "id": "1.001",
                # Missing 'name'
                "actor": "test_adapter"
            }
        ]
    }
    
    with pytest.raises(ValidationError, match="'name' is a required property"):
        validate(instance=invalid_workflow, schema=workflow_schema)


def test_schema_enforces_step_actor(workflow_schema):
    """Test that schema requires 'actor' field in steps."""
    invalid_workflow = {
        "name": "Test Workflow",
        "steps": [
            {
                "id": "1.001",
                "name": "Test Step"
                # Missing 'actor'
            }
        ]
    }
    
    with pytest.raises(ValidationError, match="'actor' is a required property"):
        validate(instance=invalid_workflow, schema=workflow_schema)


def test_schema_accepts_valid_step(workflow_schema):
    """Test that schema accepts valid steps with all required fields."""
    valid_workflow = {
        "name": "Test Workflow",
        "steps": [
            {
                "id": "1.001",
                "name": "Test Step",
                "actor": "test_adapter",
                "with": {"param": "value"},
                "emits": ["artifacts/output.json"]
            }
        ]
    }
    
    # Should not raise
    validate(instance=valid_workflow, schema=workflow_schema)


def test_schema_accepts_step_with_optional_fields(workflow_schema):
    """Test that schema accepts steps with optional fields."""
    valid_workflow = {
        "name": "Test Workflow",
        "steps": [
            {
                "id": "1.001",
                "name": "Test Step",
                "actor": "test_adapter",
                "when": "has_errors('file.json')",
                "retry": {
                    "max": 3,
                    "backoff": "exponential"
                },
                "on_fail": "pause_for_review",
                "emits": ["artifacts/output.json"]
            }
        ]
    }
    
    # Should not raise
    validate(instance=valid_workflow, schema=workflow_schema)


def test_all_existing_workflows_validate(workflow_schema):
    """Test that all existing workflow files validate against the schema."""
    workflows_dir = Path(__file__).parent.parent.parent / ".ai" / "workflows"
    workflow_files = list(workflows_dir.glob("*.yaml"))
    
    assert len(workflow_files) > 0, "No workflow files found"
    
    failed = []
    for wf_file in workflow_files:
        try:
            with open(wf_file) as f:
                workflow = yaml.safe_load(f)
            validate(instance=workflow, schema=workflow_schema)
        except ValidationError as e:
            failed.append((wf_file.name, str(e.message)))
    
    assert not failed, f"Workflows failed validation: {failed}"


def test_template_workflow_validates(workflow_schema):
    """Test that template workflow validates."""
    template_path = (
        Path(__file__).parent.parent.parent 
        / ".ai" / "workflows" / "templates" / "comprehensive_quality_workflow.yaml"
    )
    
    if template_path.exists():
        with open(template_path) as f:
            workflow = yaml.safe_load(f)
        
        # Should not raise
        validate(instance=workflow, schema=workflow_schema)
