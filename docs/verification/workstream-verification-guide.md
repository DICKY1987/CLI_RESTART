# Workstream Implementation Verification Guide

## Overview

The Workstream Verification System is a comprehensive tool for tracking and validating the implementation status of workstreams defined in JSON specification files. It helps ensure that planned features and improvements are properly implemented in the codebase.

## What It Does

The verification tool:

1. **Parses workstream JSON specifications** - Reads all workstream definition files
2. **Checks file implementation** - Verifies that files mentioned in specifications exist and have content
3. **Validates Git branches** - Checks if workstream branches exist and are merged
4. **Analyzes completion status** - Calculates completion percentages for each workstream
5. **Generates comprehensive reports** - Creates JSON, Markdown, and HTML reports

## Quick Start

### Using the CLI Command

```bash
# Verify all workstreams with default settings
cli-orchestrator verify-workstreams

# Specify custom workstreams directory
cli-orchestrator verify-workstreams \
  --workstreams-dir Downloads/WORKFLOW_VIS_FOLDER_1 \
  --output-format all \
  --output-dir artifacts

# Generate only JSON report
cli-orchestrator verify-workstreams --output-format json
```

### Using the Python Script Directly

```bash
# Run verification with all output formats
python scripts/verify_workstreams.py \
  --workstreams-dir "Downloads/WORKFLOW_VIS_FOLDER_1" \
  --repo-root "." \
  --output-format all

# Generate specific format
python scripts/verify_workstreams.py \
  --workstreams-dir "Downloads/WORKFLOW_VIS_FOLDER_1" \
  --output-format markdown
```

### Using the Workflow

```bash
# Run the verification workflow
cli-orchestrator run .ai/workflows/WORKSTREAM_VERIFICATION.yaml
```

## Output Formats

### 1. Console Output

Real-time table view showing:
- Summary statistics (total, completed, partial, missing)
- Per-workstream status with color coding
- Branch status and file counts
- Completion percentages

### 2. JSON Report

Machine-readable report containing:
- Complete verification results
- Detailed task and file information
- Structured data for programmatic processing

**Location**: `artifacts/workstream_verification_<timestamp>.json`

### 3. Markdown Report

Human-readable report with:
- Summary statistics
- Workstream-by-workstream breakdown
- Task completion status
- File implementation details

**Location**: `artifacts/workstream_verification_<timestamp>.md`

### 4. HTML Report

Interactive dashboard featuring:
- Visual progress bars
- Color-coded status indicators
- Expandable task details
- File-level verification results

**Location**: `artifacts/workstream_verification_<timestamp>.html`

## Verification Status Levels

### Completed ✓
- All files implemented (100%)
- Branch exists and is merged
- All tasks have files present

### Partial ~
- Some files implemented (1-99%)
- Branch may or may not exist
- At least one file is present

### Missing ✗
- No files implemented (0%)
- Branch does not exist
- No evidence of implementation

## Workstream JSON Specification

Each workstream JSON file should contain:

```json
{
  "workstream_id": 1,
  "workstream_name": "Feature Name",
  "branch_name": "ws/01-feature-name",
  "tasks": [
    {
      "id": "task-001",
      "description": "Task description",
      "files_to_create_or_modify": [
        "src/path/to/file.py",
        "tests/path/to/test.py"
      ],
      "acceptance_criteria": [
        "Criterion 1",
        "Criterion 2"
      ],
      "test_plan": [
        "Step 1",
        "Step 2"
      ]
    }
  ]
}
```

## Understanding the Reports

### Summary Section

```
Total Workstreams: 23
Completed: 2 (8.7%)
Partial: 17
Missing: 4
Overall File Implementation: 116/263 (44.1%)
```

**Interpretation**:
- **23 workstreams** defined in total
- **2 are fully completed** (WS-01, WS-05)
- **17 are partially implemented** (some files exist)
- **4 have no implementation** yet
- **44.1% of all files** across all workstreams are implemented

### Per-Workstream Details

```
WS-01: Schema Runtime Enforcement & Contract Validation
- Status: completed
- Branch: ws/01-schema-runtime-enforcement - Merged ✓
- Completion: 100.0%
- Files: 9/9
```

**Interpretation**:
- Workstream 01 is **fully completed**
- Branch is **merged to main**
- **All 9 files** are implemented
- **100% completion**

## Integration with CI/CD

### GitHub Actions

Add to `.github/workflows/verify-workstreams.yml`:

```yaml
name: Verify Workstreams

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install rich

      - name: Run verification
        run: |
          python scripts/verify_workstreams.py \
            --workstreams-dir workstreams \
            --output-format all

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: verification-reports
          path: artifacts/workstream_verification_*
```

## Advanced Usage

### Filtering Workstreams

Modify the script to verify specific workstreams:

```python
# In verify_workstreams.py, add filtering
parser.add_argument('--workstreams', help='Comma-separated workstream IDs')

# Filter in load_workstreams()
if args.workstreams:
    ws_filter = set(args.workstreams.split(','))
    workstreams = {k: v for k, v in workstreams.items() if k in ws_filter}
```

### Custom Verification Logic

Extend the `AcceptanceCriteriaValidator` class to add custom checks:

```python
def _check_custom_criterion(self, criterion: str, context: dict) -> bool:
    """Add custom verification logic"""
    if 'api_endpoint' in criterion:
        # Check if API endpoint exists
        return self._verify_api_endpoint(criterion, context)
    return False
```

## Troubleshooting

### Issue: No workstreams found

**Solution**: Verify the workstreams directory path:
```bash
ls "Downloads/WORKFLOW_VIS_FOLDER_1"/*.json
```

### Issue: Unicode encoding errors

**Solution**: The tool automatically handles encoding. If issues persist, set:
```bash
export PYTHONIOENCODING=utf-8
```

### Issue: Git commands fail

**Solution**: Ensure Git is installed and repository is initialized:
```bash
git --version
git status
```

### Issue: Missing dependencies

**Solution**: Install required packages:
```bash
pip install rich typer
```

## Schema Validation

The verification results conform to the schema at:
`.ai/schemas/verification_result.schema.json`

Validate a report:
```bash
cli-orchestrator verify \
  artifacts/workstream_verification_*.json \
  --schema .ai/schemas/verification_result.schema.json
```

## Best Practices

1. **Run verification regularly** - Before and after major changes
2. **Track completion trends** - Compare reports over time
3. **Prioritize missing workstreams** - Focus on 0% completion items
4. **Review partial implementations** - Identify what's blocking completion
5. **Validate before releases** - Ensure critical workstreams are completed

## Example Output

### Successful Verification

```
✓ WS-01: Schema Runtime Enforcement [completed] - 100%
   Branch: ws/01-schema-runtime-enforcement - Merged
   Files: 9/9

✓ WS-05: Schema CI/CD Integration [completed] - 100%
   Branch: ws/05-schema-cicd-integration - Merged
   Files: 11/11

~ WS-09: Observability Core [partial] - 93%
   Branch: ws/09-observability-core - Exists
   Files: 14/15

✗ WS-11: Self-Healing Implementation [missing] - 0%
   Branch: ws/11-self-healing - Missing
   Files: 0/9
```

## Next Steps

After running verification:

1. **Review HTML report** - Open the interactive dashboard
2. **Identify gaps** - Focus on missing/partial workstreams
3. **Prioritize work** - Use completion percentages to guide effort
4. **Track progress** - Re-run verification after implementing changes
5. **Generate recommendations** - Use AI analyst to suggest next steps

## Related Documentation

- [Workstream Execution Guide](../operations/workstream-execution.md)
- [JSON Schema Reference](../schemas/workstream-spec.md)
- [CI/CD Integration](../operations/ci-cd-integration.md)
- [Architecture Overview](../architecture/verification-system.md)
