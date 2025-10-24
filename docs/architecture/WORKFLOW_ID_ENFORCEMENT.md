# Workflow ID Enforcement

## Overview

This document describes the workflow ID enforcement feature that ensures all workflow steps have required identifiers at both the JSON schema and Python validation levels.

## Problem

Prior to this enhancement, the workflow schema (`schemas/workflow.schema.json`) did not enforce required fields for workflow steps. While Python code validation existed in `src/cli_multi_rapid/core/executor.py`, YAML files could technically pass JSON schema validation without step IDs, only failing at runtime.

## Solution

The workflow schema has been enhanced to enforce step structure at the JSON schema level, providing early validation before workflow execution.

### Schema Changes

Added a new `step` definition in `workflow.schema.json`:

```json
{
  "$defs": {
    "step": {
      "type": "object",
      "required": ["id", "name", "actor"],
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "actor": {"type": "string"},
        "with": {"type": "object"},
        "when": {"type": "string"},
        "retry": {
          "type": "object",
          "properties": {
            "max": {"type": "integer"},
            "backoff": {"type": "string", "enum": ["linear", "exponential"]}
          }
        },
        "emits": {"type": "array", "items": {"type": "string"}},
        "on_fail": {
          "type": "string",
          "enum": ["pause_for_review", "abort", "continue", "stop"]
        }
      }
    }
  }
}
```

Updated the `steps` property to reference this definition:

```json
{
  "properties": {
    "steps": {
      "type": ["array", "null"],
      "items": {"$ref": "#/$defs/step"}
    }
  }
}
```

### Required Fields

Every workflow step must now include:

1. **id** (string): Unique identifier for the step (e.g., "1.001", "2.005")
2. **name** (string): Human-readable name describing the step
3. **actor** (string): Adapter to execute this step

### Optional Fields

Steps may optionally include:

- **with** (object): Parameters for the adapter
- **when** (string): Conditional expression for step execution
- **retry** (object): Retry configuration with `max` attempts and `backoff` strategy
- **emits** (array): List of artifacts produced by the step
- **on_fail** (string): Action to take on failure (pause_for_review, abort, continue, stop)

## Validation Layers

The enforcement works at two levels:

### 1. JSON Schema Validation

Workflow YAML files are validated against the schema before loading. This catches structural issues early:

```python
from jsonschema import validate

validate(instance=workflow_data, schema=workflow_schema)
# Raises ValidationError if step missing required field
```

### 2. Python Runtime Validation

The `StepExecutor` class validates steps during execution:

```python
def _validate_step(self, step: Dict[str, Any]) -> None:
    required_fields = ["id", "name", "actor"]
    for field in required_fields:
        if field not in step:
            raise ValueError(f"Step missing required field: {field}")
```

## Testing

Comprehensive tests ensure enforcement works correctly:

### Schema Enforcement Tests

Location: `tests/schemas/test_workflow_schema_enforcement.py`

Tests include:
- Missing ID detection
- Missing name detection
- Missing actor detection
- Valid step acceptance
- Optional fields handling
- All existing workflows validation

### Python Validation Tests

Location: `tests/core/test_executor.py`

Existing tests verify:
- `test_validate_step_missing_id`
- `test_validate_step_missing_name`
- `test_validate_step_missing_actor`
- `test_validate_step_success`

## Impact

### Existing Workflows

All 13 existing workflow files pass the enhanced validation:

- CODE_QUALITY.yaml ✓
- DEEPSEEK_ANALYSIS.yaml ✓
- DEEPSEEK_CODE_REVIEW.yaml ✓
- DEEPSEEK_REFACTOR.yaml ✓
- DEEPSEEK_TEST_GEN.yaml ✓
- GITHUB_ISSUE_AUTOMATION.yaml ✓
- GITHUB_PR_REVIEW.yaml ✓
- GITHUB_RELEASE_MANAGEMENT.yaml ✓
- GITHUB_REPO_ANALYSIS.yaml ✓
- PY_EDIT_TRIAGE.yaml ✓
- SIMPLE_PY_FIX.yaml ✓
- SIMPLIFIED_25_OPERATION.yaml ✓
- atom_catalog_template.yaml ✓

Template workflow also passes:
- templates/comprehensive_quality_workflow.yaml ✓

### Breaking Changes

**None**. All existing workflows already follow the required structure.

### Future Workflows

New workflows must include IDs for all steps. Schema validation will fail early if IDs are missing, providing clear error messages:

```
ValidationError: 'id' is a required property
Failed validating 'required' in schema['properties']['steps']['items']
```

## Benefits

1. **Early Detection**: Schema validation catches errors before execution
2. **Clear Errors**: Descriptive validation messages guide developers
3. **Consistency**: Enforces uniform step structure across all workflows
4. **Documentation**: Schema serves as machine-readable documentation
5. **IDE Support**: Editors can use schema for autocomplete and validation

## Example

### Valid Workflow Step

```yaml
steps:
  - id: "1.001"
    name: "Run Python Tests"
    actor: pytest_runner
    with:
      path: "tests/"
      coverage: true
    emits: ["artifacts/test_report.json"]
    on_fail: "pause_for_review"
```

### Invalid Workflow Step (Missing ID)

```yaml
steps:
  - name: "Run Tests"  # ERROR: Missing 'id' field
    actor: pytest_runner
```

Validation error:
```
ValidationError: 'id' is a required property
```

## Migration Guide

For any workflow that doesn't follow the required structure:

1. Add an `id` field to each step (use format like "1.001", "1.002", etc.)
2. Ensure `name` and `actor` fields are present
3. Validate with: `cli-orchestrator verify <workflow.yaml> --schema .ai/schemas/workflow.schema.json`

## Related Files

- Schema: `.ai/schemas/workflow.schema.json`
- Executor: `src/cli_multi_rapid/core/executor.py`
- Tests: `tests/schemas/test_workflow_schema_enforcement.py`
- Tests: `tests/core/test_executor.py`
