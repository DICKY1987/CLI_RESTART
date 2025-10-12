# CLI_RESTART Launcher

## Overview

The CLI_RESTART launcher is a robust workspace validation and launch system for PowerShell-based development environments. It validates configuration files, manages sessions, and optionally launches health monitoring services.

## Features

- **Configuration Validation**: Fail-fast validation of workspace JSON configurations
- **Session Management**: Automatic session tracking with unique identifiers
- **Error Surfacing**: Detailed error reporting with automatic Notepad integration
- **No-Launch Mode**: Test harness mode for CI/CD pipelines
- **Health Monitoring**: Optional background health monitoring with JSON status reports
- **Log Rotation**: Automatic log file rotation based on size and file count limits
- **Hardened Quoting**: Safe tool launching with proper path escaping

## Quick Start

### Basic Usage

```powershell
# Validate and launch with a configuration file
.\restart.ps1 -ConfigPath .\config\workspace.json

# Run in test mode (no UI panes spawned)
.\restart.ps1 -ConfigPath .\config\workspace.json -NoLaunch

# Suppress error editor (useful in CI)
.\restart.ps1 -ConfigPath .\config\workspace.json -NoOpenEditor
```

### Configuration File Format

```json
{
  "repository": {
    "url": "https://github.com/user/repo.git"
  },
  "toggles": {
    "enableHealthMonitor": false,
    "offline": false
  },
  "logs": {
    "maxSizeMB": 10,
    "maxFiles": 5
  }
}
```

#### Required Fields

- `repository.url` (string): Repository URL - must be non-empty

#### Optional Fields

- `toggles` (object): Boolean feature flags
  - `enableHealthMonitor` (bool): Enable background health monitoring
  - `offline` (bool): Skip network operations
- `logs` (object): Log rotation settings
  - `maxSizeMB` (int): Maximum log size before rotation (default: 10)
  - `maxFiles` (int): Maximum rotated log files to keep (default: 5)

## Components

### Core Script: `restart.ps1`

Main launcher script that handles:
- Configuration validation
- Session directory creation (`.sessions/<SessionId>/`)
- Error handling and surfacing
- Health monitor integration
- Launch orchestration

**Parameters:**
- `ConfigPath` (required): Path to JSON configuration
- `SessionId` (optional): Custom session identifier (auto-generated if not provided)
- `NoOpenEditor` (switch): Suppress Notepad on validation errors
- `NoLaunch` (switch): Test mode - create artifacts without spawning panes

### Health Monitor: `.launcher/health-monitor.ps1`

Background service that monitors system health and writes status to `health.json`.

**Features:**
- Disk space monitoring (C: drive)
- Memory usage tracking
- Process count monitoring
- Configurable check intervals
- JSON status output

**Parameters:**
- `OutputPath` (optional): Path for health.json (default: ./health.json)
- `IntervalSeconds` (optional): Check interval in seconds (default: 30)
- `MaxChecks` (optional): Maximum checks before exit (default: 0 = unlimited)

**Usage:**
```powershell
# Run with defaults
.\.launcher\health-monitor.ps1

# Custom interval and output
.\.launcher\health-monitor.ps1 -OutputPath .sessions/health.json -IntervalSeconds 10

# Limited run for testing
.\.launcher\health-monitor.ps1 -MaxChecks 6 -IntervalSeconds 5
```

**Output Format (`health.json`):**
```json
{
  "timestamp": "2025-10-01T00:00:00.0000000Z",
  "healthy": true,
  "checks": {
    "disk": {
      "status": "ok",
      "freeGB": 123.45,
      "usedGB": 876.55,
      "totalGB": 1000.0,
      "freePercent": 12.35
    },
    "memory": {
      "status": "ok",
      "totalGB": 16.0,
      "usedGB": 8.5,
      "freeGB": 7.5,
      "usedPercent": 53.13
    },
    "processes": {
      "status": "ok",
      "count": 234
    }
  }
}
```

### Tool Launcher: `.launcher/Run-Tool.ps1`

Utility for launching tools with hardened quoting to handle:
- Paths with spaces
- Non-ASCII characters
- Special characters requiring escaping

**Parameters:**
- `ToolPath` (required): Full path to executable
- `Arguments` (optional): Array of arguments
- `WorkingDirectory` (optional): Working directory (default: current)
- `UseWindowsTerminal` (switch): Launch via wt.exe instead of Start-Process

**Usage:**
```powershell
# Launch tool with spaces in path
.\.launcher\Run-Tool.ps1 -ToolPath "C:\Program Files\My Tool\app.exe" -Arguments @("--config", "C:\My Configs\config.json")

# Launch in Windows Terminal
.\.launcher\Run-Tool.ps1 -ToolPath .\tool.exe -UseWindowsTerminal
```

## Testing

### Running Tests

```powershell
# Run all Pester tests
Invoke-Pester -Path tests/pester -CI -Output Detailed

# Run specific test suites
Invoke-Pester -Path tests/pester/Launcher.Unit.Tests.ps1
Invoke-Pester -Path tests/pester/Launcher.Integration.Tests.ps1
Invoke-Pester -Path tests/pester/Config.Validation.Tests.ps1

# Run tests with specific tags
Invoke-Pester -Path tests/pester -Tag Quoting,Rotation -CI
```

### Test Suites

- **Launcher.Unit.Tests.ps1**: Unit tests for core functions
  - `New-SessionId`: 8-character hex ID generation
  - `Read-Config`: Configuration parsing
  - Preflight check formatting

- **Launcher.Integration.Tests.ps1**: Integration tests
  - Session artifact creation
  - Manifest.json and preflight.md generation
  - No-launch mode verification

- **Config.Validation.Tests.ps1**: Configuration validation
  - Required field enforcement
  - Type validation for toggles
  - Error surfacing

- **Launch.Quoting.Tests.ps1**: Path quoting validation
  - Paths with spaces
  - Non-ASCII characters
  - Special character escaping

- **Log.Rotation.Tests.ps1**: Log rotation logic
  - Size-based rotation
  - File count limits
  - Sequential numbering

- **Health.Monitor.Tests.ps1**: Health monitoring
  - JSON output validation
  - Interval and max checks
  - System metrics collection

## CI/CD Integration

### GitHub Actions Workflow

The repository includes `.github/workflows/windows-ci.yml` for automated testing:

```yaml
name: Windows CI - Pester
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Pester Tests
        run: |
          Invoke-Pester -Path tests/pester -CI -Output Detailed
```

### Running in CI Mode

Use `-NoLaunch` and `-NoOpenEditor` for headless CI execution:

```powershell
.\restart.ps1 -ConfigPath .\config\workspace.json -NoLaunch -NoOpenEditor
```

## Session Artifacts

Each launcher execution creates a session directory: `.sessions/<SessionId>/`

### Session Contents

- **manifest.json**: Session metadata
  ```json
  {
    "sessionId": "a1b2c3d4",
    "config": "C:\\path\\to\\config.json",
    "timestamp": "2025-10-01T00:00:00.0000000Z",
    "mode": "no-launch"
  }
  ```

- **preflight.md**: Pre-launch checklist
  ```markdown
  # Preflight Check

  - Workspace: C:\Dev\CLI_RESTART
  - Timestamp: 2025-10-01T00:00:00
  - User: username
  ```

- **error.txt**: Validation errors (if any)
  ```
  repository.url is required and must be a non-empty string
  ```

- **health.json**: Health monitor output (if enabled)

## Troubleshooting

### Common Issues

**Issue: "Config file not found"**
- Verify the path to your configuration file
- Use absolute paths or ensure relative paths are correct from the script location

**Issue: "repository.url is required"**
- Check your configuration JSON includes the `repository` object with a `url` field
- Ensure the URL is a non-empty string

**Issue: "toggles.X must be boolean"**
- All toggle values must be `true` or `false`, not strings or numbers

**Issue: Health monitor not starting**
- Verify `enableHealthMonitor` is set to `true` in toggles
- Check that `.launcher/health-monitor.ps1` exists
- Look for warnings in launcher output

**Issue: Log rotation not working**
- Ensure `logs.maxSizeMB` and `logs.maxFiles` are properly configured
- Verify log file paths are writable
- Check that log files exceed the size threshold

### Debug Mode

Enable verbose output in PowerShell:

```powershell
$VerbosePreference = 'Continue'
.\restart.ps1 -ConfigPath .\config\workspace.json -Verbose
```

### Session Inspection

Review session artifacts for detailed diagnostics:

```powershell
# List all sessions
Get-ChildItem .sessions

# View latest session manifest
Get-Content .sessions\<SessionId>\manifest.json | ConvertFrom-Json

# Check for errors
Get-Content .sessions\<SessionId>\error.txt -ErrorAction SilentlyContinue
```

## Desktop Shortcut

Create a desktop shortcut for quick access:

```powershell
.\scripts\Create-DesktopShortcut.ps1
```

This creates a shortcut on your desktop that launches the restart script with your default configuration.

## Advanced Usage

### Custom Session IDs

Provide a custom session identifier for tracking:

```powershell
.\restart.ps1 -ConfigPath .\config\workspace.json -SessionId "prod-deploy-001"
```

### Automated Testing

Combine with Pester for comprehensive validation:

```powershell
# Run launcher in test mode
.\restart.ps1 -ConfigPath .\tests\fixtures\valid-config.json -NoLaunch -NoOpenEditor

# Verify session artifacts
$sessionId = (Get-ChildItem .sessions | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name
Test-Path ".sessions\$sessionId\manifest.json" | Should -Be $true
```

### Health Monitor Integration

Enable continuous monitoring for long-running sessions:

```json
{
  "repository": {
    "url": "https://github.com/user/repo.git"
  },
  "toggles": {
    "enableHealthMonitor": true
  }
}
```

Monitor health status:

```powershell
# Watch health.json updates
Get-Content .sessions\<SessionId>\health.json -Wait

# Parse and display health
$health = Get-Content .sessions\<SessionId>\health.json | ConvertFrom-Json
Write-Host "System Healthy: $($health.healthy)" -ForegroundColor $(if ($health.healthy) { 'Green' } else { 'Red' })
```

## Contributing

### Adding New Validation Rules

Extend `Validate-Config` function in `restart.ps1`:

```powershell
# Add custom validation
if (Has-Property -obj $Config -name 'customField') {
  $value = Get-PropertyValue -obj $Config -name 'customField'
  if (-not ($value -match '^[A-Z]{3}$')) {
    $errors += 'customField must be a 3-letter uppercase code'
  }
}
```

### Adding New Health Checks

Extend `Get-HealthStatus` in `.launcher/health-monitor.ps1`:

```powershell
# Add custom health check
try {
  $customMetric = Get-CustomMetric
  $status.checks['custom'] = @{
    status = if ($customMetric -lt $threshold) { 'ok' } else { 'warning' }
    value = $customMetric
  }
} catch {
  $status.checks['custom'] = @{
    status = 'error'
    error = $_.Exception.Message
  }
}
```

## License

See repository LICENSE file for details.

## Support

For issues and feature requests, please create an issue in the repository issue tracker.
