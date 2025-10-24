# Enforce Workflow Step IDs at Schema Level

## Summary

This PR implements JSON schema-level enforcement of workflow step IDs and required fields. Previously, step validation only occurred at runtime in Python code. This enhancement adds schema validation that catches structural issues before workflow execution.

## Changes

### 1. Enhanced Workflow Schema (`.ai/schemas/workflow.schema.json`)

Added a complete `step` definition with:
- **Required fields**: `id`, `name`, `actor`
- **Optional fields**: `with`, `when`, `retry`, `emits`, `on_fail`
- **Enum validation**: `on_fail` must be one of: `pause_for_review`, `abort`, `continue`, `stop`
- **Type constraints**: Proper typing for all fields

### 2. New Test Suite (`tests/schemas/test_workflow_schema_enforcement.py`)

Comprehensive tests covering:
- ✓ Schema enforcement of required fields (id, name, actor)
- ✓ Acceptance of valid steps with all fields
- ✓ Acceptance of optional fields
- ✓ Validation of all existing workflows (13/13 pass)
- ✓ Validation of template workflows

### 3. Documentation (`docs/architecture/WORKFLOW_ID_ENFORCEMENT.md`)

Complete documentation including:
- Problem statement and solution approach
- Schema structure and field definitions
- Validation layers (JSON Schema + Python Runtime)
- Testing strategy
- Impact analysis on existing workflows
- Migration guide for future workflows
- Example valid/invalid workflow steps

## Validation Results

### All Existing Workflows Pass

✓ CODE_QUALITY.yaml
✓ DEEPSEEK_ANALYSIS.yaml
✓ DEEPSEEK_CODE_REVIEW.yaml
✓ DEEPSEEK_REFACTOR.yaml
✓ DEEPSEEK_TEST_GEN.yaml
✓ GITHUB_ISSUE_AUTOMATION.yaml
✓ GITHUB_PR_REVIEW.yaml
✓ GITHUB_RELEASE_MANAGEMENT.yaml
✓ GITHUB_REPO_ANALYSIS.yaml
✓ PY_EDIT_TRIAGE.yaml
✓ SIMPLE_PY_FIX.yaml
✓ SIMPLIFIED_25_OPERATION.yaml
✓ atom_catalog_template.yaml

### Test Results

```
tests/schemas/test_workflow_schema_enforcement.py .......   [ 7 tests]
tests/core/test_executor.py ....                           [ 4 tests]
================================================== 11 passed in 0.29s
```

## Breaking Changes

**None**. All existing workflows already follow the required structure.

## Benefits

1. **Early Detection**: Schema validation catches errors before execution
2. **Clear Errors**: Descriptive validation messages guide developers
3. **Consistency**: Enforces uniform step structure across all workflows
4. **Documentation**: Schema serves as machine-readable documentation
5. **IDE Support**: Editors can use schema for autocomplete and validation

## Example

### Before (No Schema Enforcement)

This would pass schema validation but fail at runtime:

```yaml
steps:
  - name: "Run Tests"
    actor: pytest_runner
    # Missing 'id' - only caught at runtime
```

### After (Schema Enforcement)

This fails schema validation with a clear error:

```
ValidationError: 'id' is a required property
Failed validating 'required' in schema['properties']['steps']['items']
```

Developer must fix before execution:

```yaml
steps:
  - id: "1.001"
    name: "Run Tests"
    actor: pytest_runner
```

## Testing Instructions

### Run Schema Tests

```bash
python3 -m pytest tests/schemas/test_workflow_schema_enforcement.py -v
```

### Run Executor Validation Tests

```bash
python3 -m pytest tests/core/test_executor.py::test_validate_step_success \
  tests/core/test_executor.py::test_validate_step_missing_id \
  tests/core/test_executor.py::test_validate_step_missing_name \
  tests/core/test_executor.py::test_validate_step_missing_actor -v
```

### Validate All Workflows

```bash
python3 -c "
import json
import yaml
from jsonschema import validate
from pathlib import Path

schema = json.load(open('.ai/schemas/workflow.schema.json'))
for wf in Path('.ai/workflows').glob('*.yaml'):
    workflow = yaml.safe_load(open(wf))
    validate(instance=workflow, schema=schema)
    print(f'✓ {wf.name}')
"
```

## Files Changed

```
 .ai/schemas/workflow.schema.json                  |  51 +++++++++++++++-
 docs/architecture/WORKFLOW_ID_ENFORCEMENT.md      | 219 ++++++++++++++++++++++++
 tests/schemas/test_workflow_schema_enforcement.py | 144 ++++++++++++++++
 3 files changed, 413 insertions(+), 1 deletion(-)
```

## Related Issues

This PR addresses the need to enforce workflow structure consistency and catch configuration errors early in the development process.

## CI Checks

All CI checks should pass:
- ✓ Schema validation tests
- ✓ Executor validation tests
- ✓ All existing workflow files validate successfully
- ✓ No breaking changes to existing functionality

## Review Focus Areas

1. **Schema Definition**: Review the `step` definition for completeness
2. **Enum Values**: Confirm `on_fail` enum includes all used values
3. **Test Coverage**: Verify tests cover all required and optional fields
4. **Documentation**: Ensure documentation is clear and comprehensive
5. **Backward Compatibility**: Confirm no existing workflows are broken
