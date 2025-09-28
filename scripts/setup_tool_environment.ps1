# PowerShell session setup for CLI Orchestrator tools
# - Adds .venv\Scripts to PATH (if present)
# - Applies env vars from config/tool_adapters.yaml (via Python helper)
# - Prints a quick status of resolved tool paths/versions

param(
  [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

# Ensure repo root
if (-not (Test-Path -LiteralPath 'config')) {
  Write-Error 'Run this script from the repository root.'
}

# 1) Add venv Scripts to PATH (session only)
if (Test-Path -LiteralPath '.venv/Scripts') {
  $venvScripts = (Resolve-Path '.venv/Scripts').Path
  if (-not ($env:Path -split ';' | Where-Object { $_ -eq $venvScripts })) {
    $env:Path = "$venvScripts;$env:Path"
    if (-not $Quiet) { Write-Host "Added to PATH: $venvScripts" -ForegroundColor Cyan }
  }
}

# 2) Ask Python helper for env + tool info
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error 'Python not found in PATH; cannot parse YAML config.'
}

$json = python scripts/setup_tool_environment.py
if ($LASTEXITCODE -ne 0) {
  Write-Error 'Failed to parse tool_adapters.yaml'
}

$obj = $json | ConvertFrom-Json
if ($null -eq $obj) {
  Write-Error 'Invalid JSON output from setup_tool_environment.py'
}

# 3) Apply env vars
if ($obj.env) {
  foreach ($k in $obj.env.PSObject.Properties.Name) {
    $v = $obj.env.$k
    $env:$k = $v
    if (-not $Quiet) { Write-Host "Set env: $k=$v" -ForegroundColor DarkGreen }
  }
}

# 4) Print status
if (-not $Quiet) {
  Write-Host "\nResolved tools:" -ForegroundColor Yellow
  foreach ($name in $obj.resolved_tools.PSObject.Properties.Name) {
    $item = $obj.resolved_tools.$name
    $ok = if ($item.path) { 'OK' } else { 'MISS' }
    Write-Host (" - {0,-16} [{1}] {2} {3}" -f $name, $ok, $item.version, $item.path)
  }
}

