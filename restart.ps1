<#
 .SYNOPSIS
   Validates a workspace configuration before starting any UI panes.

 .DESCRIPTION
   - Parses a JSON configuration file
   - Validates required fields and types
   - On failure, writes .sessions/<SessionId>/error.txt and opens it in Notepad
   - Exits non-zero to fail-fast

 .PARAMETER ConfigPath
   Path to the JSON configuration to validate.

 .PARAMETER SessionId
   Identifier for this run; used to write under .sessions/<SessionId>.

 .PARAMETER NoOpenEditor
   If set, suppresses opening Notepad for error surfacing (useful in CI).

 .EXAMPLE
   .\restart.ps1 -ConfigPath .\config\workspace.json
#>

param(
  [Parameter(Mandatory = $true)]
  [string]$ConfigPath,

  [string]$SessionId = (Get-Date -Format 'yyyyMMddHHmmss'),

  [switch]$NoOpenEditor,

  [switch]$NoLaunch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-SessionPath {
  param(
    [string]$SessionId
  )
  $repoRoot = $PSScriptRoot
  $sessionDir = Join-Path -Path $repoRoot -ChildPath ".sessions/$SessionId"
  if (-not (Test-Path $sessionDir)) {
    New-Item -ItemType Directory -Path $sessionDir | Out-Null
  }
  return $sessionDir
}

function New-SessionId {
  $bytes = New-Object byte[] 4
  [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
  ($bytes | ForEach-Object { '{0:x2}' -f $_ }) -join ''
}

function Write-ValidationError {
  param(
    [string[]]$Errors,
    [string]$SessionId,
    [switch]$NoOpenEditor
  )

  $sessionDir = New-SessionPath -SessionId $SessionId
  $errorFile = Join-Path $sessionDir 'error.txt'
  $content = ($Errors -join [Environment]::NewLine)
  Set-Content -LiteralPath $errorFile -Value $content -Encoding UTF8

  Write-Host "Validation failed. Details: $errorFile" -ForegroundColor Red

  if (-not $NoOpenEditor) {
    try {
      Start-Process -FilePath 'notepad.exe' -ArgumentList @("$errorFile") | Out-Null
    } catch {
      Write-Warning "Failed to open Notepad: $($_.Exception.Message)"
    }
  }

  exit 1
}

function Invoke-LogRotation {
  param(
    [string]$LogPath,
    [int]$MaxSizeMB = 10,
    [int]$MaxFiles = 5
  )

  if (-not (Test-Path -LiteralPath $LogPath)) {
    return  # No log file to rotate
  }

  $logFile = Get-Item -LiteralPath $LogPath
  $logSizeMB = $logFile.Length / 1MB

  if ($logSizeMB -lt $MaxSizeMB) {
    return  # Log is within size limit
  }

  Write-Host "Rotating log: $LogPath (${logSizeMB}MB >= ${MaxSizeMB}MB)" -ForegroundColor Yellow

  # Shift existing rotated logs
  for ($i = $MaxFiles - 1; $i -ge 1; $i--) {
    $oldLog = "$LogPath.$i"
    $newLog = "$LogPath.$($i + 1)"

    if (Test-Path -LiteralPath $oldLog) {
      if ($i -eq ($MaxFiles - 1)) {
        Remove-Item -LiteralPath $oldLog -Force  # Delete oldest
      }
      else {
        Move-Item -LiteralPath $oldLog -Destination $newLog -Force
      }
    }
  }

  # Rotate current log to .1
  Move-Item -LiteralPath $LogPath -Destination "$LogPath.1" -Force
  Write-Host "Log rotated successfully" -ForegroundColor Green
}

function Validate-Config {
  param(
    $Config
  )

  $errors = @()

  function Has-Property {
    param($obj, [string]$name)
    if ($null -eq $obj) { return $false }
    if ($obj -is [hashtable]) { return $obj.ContainsKey($name) }
    if ($obj -is [pscustomobject]) { return $obj.PSObject.Properties.Name -contains $name }
    return $false
  }

  function Get-PropertyValue {
    param($obj, [string]$name)
    if ($obj -is [hashtable]) { return $obj[$name] }
    if ($obj -is [pscustomobject]) {
      $prop = $obj.PSObject.Properties[$name]
      if ($null -ne $prop) { return $prop.Value } else { return $null }
    }
    return $null
  }

  # repository.url required and must be a non-empty string
  if (-not (Has-Property -obj $Config -name 'repository')) {
    $errors += 'repository object is required'
  } else {
    $repo = Get-PropertyValue -obj $Config -name 'repository'
    $url = Get-PropertyValue -obj $repo -name 'url'
    if (-not ($url -is [string]) -or [string]::IsNullOrWhiteSpace($url)) {
      $errors += 'repository.url is required and must be a non-empty string'
    }
  }

  # toggles (optional); if present, all values must be boolean
  if (Has-Property -obj $Config -name 'toggles') {
    $toggles = Get-PropertyValue -obj $Config -name 'toggles'
    if (-not ($toggles -is [hashtable] -or $toggles -is [pscustomobject])) {
      $errors += 'toggles must be an object'
    } else {
      if ($toggles -is [hashtable]) {
        foreach ($k in $toggles.Keys) {
          $v = $toggles[$k]
          if (-not ($v -is [bool])) { $errors += "toggles.$k must be boolean" }
        }
      } else {
        foreach ($p in $toggles.PSObject.Properties) {
          if (-not ($p.Value -is [bool])) { $errors += "toggles.$($p.Name) must be boolean" }
        }
      }
    }
  }

  return ,$errors
}

try {
  if ($NoLaunch -and -not $PSBoundParameters.ContainsKey('SessionId')) {
    $SessionId = New-SessionId
  }
  if (-not (Test-Path -LiteralPath $ConfigPath)) {
    Write-ValidationError -Errors @("Config file not found: $ConfigPath") -SessionId $SessionId -NoOpenEditor:$NoOpenEditor
  }

  $raw = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8
  try {
    $cfg = ConvertFrom-Json -InputObject $raw
  } catch {
    Write-ValidationError -Errors @("Invalid JSON: $($_.Exception.Message)") -SessionId $SessionId -NoOpenEditor:$NoOpenEditor
  }

  $errors = Validate-Config -Config $cfg
  if ($errors.Count -gt 0) {
    Write-ValidationError -Errors $errors -SessionId $SessionId -NoOpenEditor:$NoOpenEditor
  }

  Write-Host 'Configuration valid. Proceeding...' -ForegroundColor Green
  # No-launch mode for test harness: create session artifacts instead of spawning panes
  if ($NoLaunch) {
    $sessionDir = New-SessionPath -SessionId $SessionId
    $manifest = [ordered]@{
      sessionId = $SessionId
      config    = (Resolve-Path -LiteralPath $ConfigPath).Path
      timestamp = (Get-Date).ToString('o')
      mode      = 'no-launch'
    }
    $manifest | ConvertTo-Json -Depth 5 | Out-File -FilePath (Join-Path $sessionDir 'manifest.json') -Encoding UTF8
    $preflight = @(
      '# Preflight Check'
      ""
      "- Workspace: $PSScriptRoot"
      "- Timestamp: $((Get-Date).ToString('s'))"
      "- User: $env:USERNAME"
    ) -join "`n"
    $preflight | Out-File -FilePath (Join-Path $sessionDir 'preflight.md') -Encoding UTF8 -Force
    exit 0
  }

  # Placeholder for actual restart/launch logic
  exit 0

} catch {
  Write-ValidationError -Errors @("Unexpected error: $($_.Exception.Message)") -SessionId $SessionId -NoOpenEditor:$NoOpenEditor
}
