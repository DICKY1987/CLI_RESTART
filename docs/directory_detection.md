# Directory Detection in CLI Orchestrator

## Overview

The CLI Orchestrator needs to know where the repository root is located to correctly reference configuration files, workflows, and source code. This document explains how directory detection works across different components.

## Detection Strategy

The repository uses a two-tier detection strategy:

1. **Git-based detection** (preferred): Use `git rev-parse --show-toplevel` to find the repository root
2. **Fallback to current directory**: If git detection fails, use `Path.cwd()` (the current working directory)

## Current Location

The repository is currently located at:
```
/home/runner/work/CLI_RESTART/CLI_RESTART
```

To verify this, run:
```bash
python3 scripts/show_directory_detection.py
```

## Component Behavior

### WorkflowRunner
- **Location**: `src/cli_multi_rapid/workflow_runner.py`
- **Strategy**: Uses `Path.cwd()` for relative paths
- **Logging**: Logs working directory on initialization with `[dim]` style output

### WorkstreamExecutor
- **Location**: `WORKFLOW_VIS_FOLDER_1/master-workstream-executor.py`
- **Strategy**: 
  - Tries `git rev-parse --show-toplevel` first
  - Falls back to `Path.cwd()` if git detection fails
- **Logging**: Logs detected repository root with `logger.info()`

### WorkflowOrchestrator
- **Location**: `workflows/orchestrator.py`
- **Strategy**: Uses `Path.cwd()` as `project_root`
- **Logging**: Logs project_root on initialization with `logger.info()`

### PipelineScaffolder
- **Location**: `src/cli_multi_rapid/workflow_engine.py`
- **Strategy**: 
  - Accepts optional `repo_root` parameter
  - Defaults to `Path.cwd()` if not provided
- **Logging**: Logs repository root with `console.print()` in dim style

## Important Paths

All relative paths in the codebase are resolved relative to the repository root:

- **Workflows**: `.ai/workflows/` or `workflows/`
- **Configuration**: `config/`
- **Source Code**: `src/cli_multi_rapid/`
- **Tests**: `tests/`
- **Artifacts**: `artifacts/`
- **Logs**: `logs/`

## Running from Different Directories

### From Repository Root (Recommended)
```bash
cd /home/runner/work/CLI_RESTART/CLI_RESTART
cli-orchestrator run .ai/workflows/PY_EDIT_TRIAGE.yaml
```

### From Subdirectory
When running from a subdirectory:
- Git-based detection will still find the correct repository root
- Components using `Path.cwd()` may have issues with relative paths
- **Recommendation**: Always run commands from the repository root

## Troubleshooting

### Issue: "Workflow file not found"
**Cause**: Running from wrong directory or relative path is incorrect

**Solution**:
1. Check current directory: `pwd`
2. Verify repository root: `git rev-parse --show-toplevel`
3. Run the directory detection script: `python3 scripts/show_directory_detection.py`
4. Navigate to repository root before running commands

### Issue: "Config file not found"
**Cause**: Configuration files are expected relative to repository root

**Solution**:
1. Ensure you're in the repository root: `cd $(git rev-parse --show-toplevel)`
2. Verify config directory exists: `ls -la config/`

### Issue: Components detect different directories
**Cause**: Some components use git detection, others use `Path.cwd()`

**Solution**:
- Ensure you're running from the git repository root
- If not in a git repository, all components will use the same `Path.cwd()`

## Environment Variables

Currently, there are no environment variables to override directory detection. If needed, you can:

1. Pass explicit paths to components that accept them (e.g., `PipelineScaffolder(repo_root=Path("/custom/path"))`)
2. Use `cd` to change to the desired directory before running commands

## Testing Directory Detection

To test how directory detection works in your environment:

```bash
# From repository root
python3 scripts/show_directory_detection.py

# From a subdirectory
cd src/cli_multi_rapid
python3 ../../scripts/show_directory_detection.py
```

This will show:
- Current working directory
- Git repository root
- Whether they match
- Status of key directories

## Best Practices

1. **Always run commands from the repository root** unless you have a specific reason not to
2. **Use absolute paths** when programmatically invoking CLI orchestrator commands
3. **Check logs** - components now log their detected directories for debugging
4. **Verify setup** - run `show_directory_detection.py` after cloning or moving the repository
5. **In CI/CD** - ensure workflows start from the repository root:
   ```yaml
   - name: Run CLI Orchestrator
     working-directory: ${{ github.workspace }}
     run: cli-orchestrator run .ai/workflows/workflow.yaml
   ```

## Future Improvements

Potential enhancements to directory detection:

1. Add `CLI_ORCHESTRATOR_ROOT` environment variable for explicit override
2. Standardize all components to use the same detection strategy
3. Add validation that warns when running from subdirectory
4. Support for `.orchestratorrc` file to mark repository root
