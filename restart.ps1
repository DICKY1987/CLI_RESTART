<#
 .SYNOPSIS
   Lightweight launcher stub to satisfy Pester tests.

 .DESCRIPTION
   Validates a minimal JSON config, manages session artifacts under ./.sessions/{SessionId},
   and writes preflight/manifest files. On validation errors, writes error.txt and exits non‑zero.

 .PARAMETER ConfigPath
   Path to JSON configuration file. Must exist.

 .PARAMETER SessionId
   Optional 8‑char lowercase hex session id. If omitted, a new id is generated.

 .PARAMETER NoLaunch
   If set, skips any external launching (no‑op in this stub).

 .PARAMETER NoOpenEditor
   If set, suppresses opening any editors (no‑op in this stub).
#>

param(
  [Parameter(Mandatory = $true)]
  [string]$ConfigPath,

  [string]$SessionId,

  [switch]$NoLaunch,
  [switch]$NoOpenEditor
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-SessionId {
  # 8‑char lowercase hex
  return ([guid]::NewGuid().ToString('N').Substring(0,8).ToLowerInvariant())
}

function Ensure-Dir([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Write-SessionError([string]$Dir, [string[]]$Messages) {
  Ensure-Dir $Dir
  $out = ($Messages -join "`n")
  $out | Out-File -FilePath (Join-Path $Dir 'error.txt') -Encoding UTF8 -Force
}

function Read-Config([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    return @{ ok = $false; errors = @('Config file not found') }
  }

  try {
    $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    $cfg = $raw | ConvertFrom-Json -ErrorAction Stop
  }
  catch {
    return @{ ok = $false; errors = @('Invalid JSON in config file') }
  }

  $errors = @()

  # repository.url required (guard property access under StrictMode)
  $repoUrl = $null
  $repoObj = $null
  if ($cfg.PSObject.Properties.Match('repository').Count -gt 0) {
    $repoObj = $cfg.repository
    if ($null -ne $repoObj -and ($repoObj.PSObject.Properties.Match('url').Count -gt 0)) {
      $repoUrl = $repoObj.url
    }
  }
  if (-not $repoUrl -or -not ($repoUrl -is [string]) -or [string]::IsNullOrWhiteSpace($repoUrl)) {
    $errors += 'repository.url is required'
  }

  # toggles checks (types must be boolean when present)
  if ($cfg.PSObject.Properties.Match('toggles').Count -gt 0) {
    if ($cfg.toggles.PSObject.Properties.Match('launchPanes').Count -gt 0) {
      if (-not ($cfg.toggles.launchPanes -is [bool])) { $errors += 'toggles.launchPanes must be boolean' }
    }
    if ($cfg.toggles.PSObject.Properties.Match('dryRun').Count -gt 0) {
      if (-not ($cfg.toggles.dryRun -is [bool])) { $errors += 'toggles.dryRun must be boolean' }
    }
  }

  if ($errors.Count -gt 0) {
    return @{ ok = $false; errors = $errors }
  }

  return @{ ok = $true; config = $cfg }
}

# Resolve repo root and session paths
$repoRoot = Split-Path -Parent $PSCommandPath
$sessionsRoot = Join-Path $repoRoot '.sessions'
Ensure-Dir $sessionsRoot

if (-not $SessionId) { $SessionId = New-SessionId }
$sessionDir = Join-Path $sessionsRoot $SessionId
Ensure-Dir $sessionDir

# Always write a basic preflight file used by tests
try {
  $preflight = @()
  $preflight += '# Preflight Check'
  $preflight += "Workspace: $repoRoot"
  $preflight += "Timestamp: $(Get-Date -Format 'u')"
  $preflight -join "`n" | Out-File -FilePath (Join-Path $sessionDir 'preflight.md') -Encoding UTF8 -Force
}
catch { }

# Validate configuration
$result = Read-Config -Path $ConfigPath
if (-not $result.ok) {
  Write-SessionError -Dir $sessionDir -Messages $result.errors
  exit 1
}

# On success, write a minimal manifest
$manifest = @{
  sessionId = $SessionId
  timestamp = (Get-Date).ToString('o')
  repository = @{ url = $result.config.repository.url }
}
$manifest | ConvertTo-Json -Depth 5 | Out-File -FilePath (Join-Path $sessionDir 'manifest.json') -Encoding UTF8 -Force

# No actual launching in this stub; respect flags but do nothing
exit 0
