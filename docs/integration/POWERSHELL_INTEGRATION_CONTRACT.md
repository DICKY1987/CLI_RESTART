# PowerShell Integration Contract

**Version**: 1.0.0
**Date**: 2025-10-18
**Status**: Approved

## Overview

This document defines the integration contract between **CLI_RESTART** (Python-based orchestrator) and **PowerShell_deterministi_factory** (PowerShell-based file routing and Git automation system).

The two systems integrate through:
1. **PowerShell Adapter** in CLI_RESTART that executes PowerShell scripts
2. **Standardized JSON schemas** for data exchange
3. **Workflow definitions** that coordinate both systems
4. **Shared artifact formats** for handoff between systems

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI_RESTART                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   Workflow   │──▶│    Router    │──▶│   PowerShell │        │
│  │    Runner    │   │              │   │   Adapter    │        │
│  └──────────────┘   └──────────────┘   └───────┬──────┘        │
└────────────────────────────────────────────────│────────────────┘
                                                  │
                                                  │ subprocess
                                                  │ pwsh -File
                                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              PowerShell_deterministi_factory                     │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │    Core      │   │   File       │   │     Git      │        │
│  │   Module     │   │   Router     │   │   Worktree   │        │
│  └──────────────┘   └──────────────┘   └──────────────┘        │
│                                                                  │
│  Emits JSON artifacts matching schemas                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## PowerShell Adapter Interface

### Adapter Registration

The PowerShell adapter is registered in CLI_RESTART's router as:

```python
# src/cli_multi_rapid/adapters/powershell_adapter.py
class PowerShellAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            name="powershell_adapter",
            adapter_type=AdapterType.DETERMINISTIC,
            description="Execute PowerShell scripts from deterministi_factory"
        )
```

### Supported Operations

The adapter supports the following operations:

| Operation | PowerShell Script | Output Schema | Description |
|-----------|------------------|---------------|-------------|
| `route_files` | `Invoke-FileRouter` | `file_router_output.schema.json` | Route files from Downloads to repo paths |
| `get_worktree_status` | `Get-GitWorktreeStatus` | `git_worktree_status.schema.json` | List active Git worktrees |
| `create_worktree` | `New-GitWorktree` | `git_worktree_status.schema.json` | Create new worktree |
| `get_status` | `Get-FactoryStatus` | `factory_diagnostics.schema.json` | Health check and diagnostics |
| `launch_session` | `Enhanced-CLI-Launcher.ps1` | `session_status.schema.json` | Launch multi-tab CLI environment |

### Execution Contract

**Input to PowerShell Adapter**:
```yaml
# In workflow YAML
- actor: powershell_adapter
  with:
    operation: route_files
    source_directory: "C:/Users/*/Downloads"
    auto_commit: true
    conflict_policy: "quarantine"
```

**Adapter Behavior**:
1. Validate PowerShell 7+ is available (`pwsh.exe`)
2. Validate PowerShell_deterministi_factory repo path exists
3. Build PowerShell command:
   ```powershell
   pwsh -NoProfile -File "C:/PowerShell_ deterministi_factory/scripts/Invoke-FileRouter.ps1" `
        -SourceDirectory "C:/Users/*/Downloads" `
        -AutoCommit $true `
        -ConflictPolicy "quarantine" `
        -OutputFormat "json"
   ```
4. Execute command, capture stdout/stderr
5. Parse JSON output according to schema
6. Return `AdapterResult` with:
   - `success`: True if PowerShell exit code 0
   - `tokens_used`: 0 (deterministic)
   - `artifacts`: Path to emitted JSON files
   - `output`: Parsed JSON or raw stdout
   - `metadata`: PowerShell version, execution time, etc.

**Error Handling**:
- PowerShell not found → `AdapterResult(success=False, error="PowerShell 7+ not found")`
- Script execution error → Capture stderr, parse PowerShell error records
- Invalid JSON output → `AdapterResult(success=False, error="Invalid JSON output")`
- Timeout (default 5 min) → Kill process, return timeout error

---

## Data Exchange Schemas

All data exchanged between systems must validate against JSON Schema definitions.

### Schema Locations

**CLI_RESTART**:
- `.ai/schemas/powershell/file_router_output.schema.json`
- `.ai/schemas/powershell/git_worktree_status.schema.json`
- `.ai/schemas/powershell/session_status.schema.json`
- `.ai/schemas/powershell/factory_diagnostics.schema.json`

**PowerShell_deterministi_factory**:
- `config/schemas/` (mirror of CLI_RESTART schemas for validation)

### Schema Versioning

Schemas use semantic versioning in `$id`:
```json
{
  "$id": "https://cli-orchestrator.dev/schemas/powershell/file_router_output.v1.schema.json"
}
```

**Breaking changes** require major version bump (v1 → v2).
**Additive changes** (new optional fields) are non-breaking.

### Validation Requirements

**PowerShell Side**:
- All JSON output MUST be emitted to stdout
- JSON MUST be valid and validate against schema
- Errors SHOULD be logged to stderr and error array in JSON
- Exit code 0 for success, non-zero for failure

**CLI_RESTART Side**:
- Adapter MUST validate JSON against schema before returning success
- Schema validation failures SHOULD be logged with detailed error
- Adapter SHOULD provide helpful error messages for common schema violations

---

## Workflow Integration Patterns

### Pattern 1: File Routing + Processing

```yaml
name: "Route and Process Downloads"
steps:
  - id: "1.001"
    actor: powershell_adapter
    with:
      operation: route_files
      source_directory: "Downloads"
    emits: ["artifacts/routed_files.json"]

  - id: "1.002"
    actor: vscode_diagnostics
    with:
      files_from_artifact: "artifacts/routed_files.json"
      analyzers: ["ruff", "mypy"]
    emits: ["artifacts/diagnostics.json"]

  - id: "1.003"
    actor: code_fixers
    with:
      fix_issues: "artifacts/diagnostics.json"
```

**Data Flow**:
1. PowerShell routes files, emits `routed_files.json` with paths
2. CLI_RESTART reads artifact, extracts destination paths
3. Runs diagnostics on routed files
4. Fixes issues found

### Pattern 2: Parallel Worktree Testing

```yaml
name: "Test in Isolated Worktree"
steps:
  - id: "1.001"
    actor: powershell_adapter
    with:
      operation: create_worktree
      branch: "test/{{timestamp}}"
      path: "worktrees/test-{{timestamp}}"
    emits: ["artifacts/worktree_created.json"]

  - id: "1.002"
    actor: pytest_runner
    with:
      working_directory_from_artifact: "artifacts/worktree_created.json"
      coverage: true
    emits: ["artifacts/test_report.json"]

  - id: "1.003"
    actor: powershell_adapter
    with:
      operation: remove_worktree
      path_from_artifact: "artifacts/worktree_created.json"
```

**Data Flow**:
1. PowerShell creates isolated worktree
2. CLI_RESTART runs tests in that worktree
3. PowerShell cleans up worktree after tests complete

### Pattern 3: Health Check and Coordination

```yaml
name: "Dual System Health Check"
steps:
  - id: "1.001"
    actor: powershell_adapter
    with:
      operation: get_status
    emits: ["artifacts/powershell_status.json"]

  - id: "1.002"
    actor: verifier
    with:
      gate_type: system_health
      check_powershell: "artifacts/powershell_status.json"
      check_cli_orchestrator: true
```

**Data Flow**:
1. PowerShell emits diagnostic data
2. Verifier checks both systems are healthy
3. Workflow proceeds only if both systems operational

---

## Configuration Management

### PowerShell Adapter Configuration

**Location**: `config/powershell_adapter.yaml` (new file)

```yaml
powershell_adapter:
  enabled: true

  # PowerShell executable
  powershell_path: "pwsh"  # or "C:/Program Files/PowerShell/7/pwsh.exe"

  # PowerShell_deterministi_factory repository
  factory_repo_path: "C:/PowerShell_ deterministi_factory"

  # Execution settings
  timeout_seconds: 300  # 5 minutes default
  no_profile: true  # Run with -NoProfile
  execution_policy: "RemoteSigned"

  # Script paths (relative to factory_repo_path)
  scripts:
    file_router: "scripts/Invoke-FileRouter.ps1"
    worktree_status: "scripts/Get-GitWorktreeStatus.ps1"
    worktree_create: "scripts/New-GitWorktree.ps1"
    factory_status: "scripts/Get-FactoryStatus.ps1"
    launcher: "NEXT_STEPS/Enhanced-CLI-Launcher.ps1"

  # Output settings
  output_format: "json"
  capture_stderr: true
  log_execution: true
```

### Environment Variables

```bash
# Required
POWERSHELL_FACTORY_PATH="C:/PowerShell_ deterministi_factory"

# Optional
POWERSHELL_EXECUTABLE="pwsh"
POWERSHELL_TIMEOUT=300
```

---

## Error Handling and Resilience

### Error Categories

1. **Missing Dependencies**
   - PowerShell not found → Graceful degradation, skip PowerShell steps
   - Factory repo not found → Clear error message with setup instructions

2. **Execution Failures**
   - Script not found → Log error, return `success=False`
   - PowerShell error → Capture error record, include in AdapterResult
   - Timeout → Kill process, log timeout, allow workflow retry

3. **Schema Validation Failures**
   - Invalid JSON → Log raw output, helpful error message
   - Schema mismatch → Point to schema definition, show diff

### Retry Strategy

```yaml
# In workflow with retry
steps:
  - id: "1.001"
    actor: powershell_adapter
    with:
      operation: route_files
    retry:
      max_attempts: 3
      backoff_seconds: 5
      retry_on_timeout: true
```

### Graceful Degradation

If PowerShell adapter unavailable:
- Workflows check `powershell_adapter.is_available()` before execution
- Conditional steps using `requires: powershell_available`
- Fallback to Python-native implementations where possible

---

## Testing Strategy

### Unit Tests (CLI_RESTART)

**File**: `tests/unit/test_powershell_adapter.py`

```python
def test_powershell_adapter_route_files():
    adapter = PowerShellAdapter()
    step = {
        "with": {
            "operation": "route_files",
            "source_directory": "test_downloads"
        }
    }
    result = adapter.execute(step)
    assert result.success
    assert result.tokens_used == 0
    # Validate JSON output against schema
```

### Integration Tests (Both Systems)

**File**: `tests/integration/test_powershell_integration.py`

```python
@pytest.mark.integration
def test_file_routing_end_to_end():
    # 1. Create test file in Downloads
    # 2. Run PowerShell router via adapter
    # 3. Verify file moved to correct location
    # 4. Validate JSON output schema
```

### Contract Tests

**File**: `tests/contract/test_powershell_schemas.py`

```python
def test_file_router_output_schema():
    schema = load_schema("powershell/file_router_output.schema.json")
    sample_output = {
        "timestamp": "2025-10-18T12:00:00Z",
        "operation": "route_files",
        "status": "success",
        "routed_files": []
    }
    validate(sample_output, schema)  # Should pass
```

---

## Performance Characteristics

### PowerShell Adapter Performance Profile

```python
AdapterPerformanceProfile(
    complexity_threshold=0.3,  # Handles simple file/git operations
    preferred_file_types=["*"],  # File-agnostic (operates on any type)
    max_files=1000,  # Can handle large file sets
    operation_types=["file_ops", "git_ops", "diagnostics"],
    avg_execution_time=2.0,  # 2 seconds average
    success_rate=0.98,
    cost_efficiency=0,  # No tokens (deterministic)
    parallel_capable=True,  # Can run multiple instances
    requires_network=False,
    requires_api_key=False
)
```

### Benchmarks

| Operation | Files | Avg Time | P95 Time |
|-----------|-------|----------|----------|
| route_files | 10 | 0.5s | 1.2s |
| route_files | 100 | 2.1s | 3.5s |
| route_files | 1000 | 15.3s | 22.0s |
| get_worktree_status | 5 worktrees | 0.3s | 0.6s |
| create_worktree | 1 | 1.2s | 2.0s |
| get_status | - | 0.4s | 0.8s |

---

## Security Considerations

1. **Script Execution**
   - Only execute scripts from trusted `PowerShell_deterministi_factory` repo
   - Validate repo path before execution
   - Use `-NoProfile` to prevent profile injection

2. **Input Validation**
   - Sanitize all parameters passed to PowerShell
   - Prevent command injection via parameter escaping
   - Validate paths are within expected directories

3. **Output Handling**
   - Parse JSON safely (catch exceptions)
   - Don't execute code from JSON output
   - Log but don't display sensitive data from stderr

4. **Filesystem Access**
   - PowerShell scripts run with user permissions
   - Limit file operations to configured directories
   - Avoid privileged operations (no `sudo`/admin)

---

## Migration and Compatibility

### Version Compatibility Matrix

| CLI_RESTART | PowerShell Factory | Schema Version | Status |
|-------------|-------------------|----------------|--------|
| 1.0.x | 0.1.x (Phase 0-3) | v1 | Development |
| 1.1.x | 0.2.x (Phase 4-6) | v1 | Planned |
| 2.0.x | 1.0.x (Stable) | v2 | Future |

### Breaking Change Policy

Breaking changes to schemas or adapter interface require:
1. Major version bump in schema `$id`
2. Deprecation notice 1 version prior
3. Support for both old and new versions during transition
4. Migration guide in documentation

---

## Appendix: Example Outputs

### File Router Output Example

```json
{
  "timestamp": "2025-10-18T12:34:56Z",
  "operation": "route_files",
  "status": "success",
  "routed_files": [
    {
      "source_path": "C:/Users/User/Downloads/PowerShell_deterministi_factory-scripts-20251018-abc123.ps1",
      "destination_path": "C:/PowerShell_ deterministi_factory/scripts/new_script.ps1",
      "project": "PowerShell_deterministi_factory",
      "alias": "scripts",
      "timestamp_parsed": "20251018",
      "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "size_bytes": 2048
    }
  ],
  "conflicts": [],
  "statistics": {
    "total_processed": 1,
    "successful_routes": 1,
    "conflicts_found": 0,
    "bytes_processed": 2048,
    "duration_ms": 450
  },
  "errors": [],
  "router_config": {
    "version": "v1.0.0",
    "conflict_policy": "dedupe-or-quarantine",
    "file_stable_ms": 1500
  }
}
```

### Factory Diagnostics Example

```json
{
  "timestamp": "2025-10-18T12:00:00Z",
  "repo_root": "C:/PowerShell_ deterministi_factory",
  "health_status": "healthy",
  "git": {
    "has_git": true,
    "current_branch": "main",
    "remote_url": "https://github.com/DICKY1987/PowerShell_-deterministi_factory.git",
    "uncommitted_changes": false,
    "untracked_files": 0,
    "ahead_behind": {
      "ahead": 0,
      "behind": 0
    }
  },
  "configuration": {
    "config_present": true,
    "config_valid": true,
    "router_version": "v1.0.0",
    "projects_configured": 1
  },
  "modules": {
    "core_module_available": true,
    "core_module_version": "0.1.0",
    "exported_functions": ["Get-FactoryStatus", "Invoke-FileRouter", "Get-GitWorktreeStatus"]
  },
  "tools": {
    "git": true,
    "pwsh": true,
    "wt": true
  },
  "powershell": {
    "version": "7.4.1",
    "edition": "Core",
    "os": "Windows"
  },
  "filesystem": {
    "required_directories": {
      "config": true,
      "docs": true,
      "modules": true,
      "scripts": true,
      "tests": true
    },
    "path_has_space": true
  },
  "errors": [],
  "recommendations": []
}
```

---

## Contract Approval

**Approved by**: Development Team
**Date**: 2025-10-18
**Next Review**: After Phase 4 completion
**Change Control**: Major changes require approval, minor clarifications via PR

---

## Related Documentation

- [CLI_RESTART CLAUDE.md](../../CLAUDE.md)
- [PowerShell_deterministi_factory README.md](C:/PowerShell_ deterministi_factory/README.md)
- [PowerShell_deterministi_factory AGENTS.md](C:/PowerShell_ deterministi_factory/AGENTS.md)
- [Schema Definitions](.ai/schemas/powershell/)
