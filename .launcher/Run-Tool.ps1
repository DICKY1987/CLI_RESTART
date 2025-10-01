<#
 .SYNOPSIS
   Launches a tool with hardened quoting for paths containing spaces and non-ASCII characters.

 .DESCRIPTION
   Provides safe execution of tools via wt.exe or Start-Process with proper argument escaping.
   Handles:
   - Paths with spaces
   - Non-ASCII characters
   - Special characters requiring escaping

 .PARAMETER ToolPath
   Full path to the executable to launch.

 .PARAMETER Arguments
   Array of arguments to pass to the tool.

 .PARAMETER WorkingDirectory
   Working directory for the process (optional).

 .PARAMETER UseWindowsTerminal
   If set, launches via wt.exe. Otherwise uses Start-Process.

 .EXAMPLE
   .\Run-Tool.ps1 -ToolPath "C:\Program Files\My Tool\app.exe" -Arguments @("--config", "C:\Users\User Name\config.json")
#>

param(
  [Parameter(Mandatory = $true)]
  [string]$ToolPath,

  [string[]]$Arguments = @(),

  [string]$WorkingDirectory = $PWD,

  [switch]$UseWindowsTerminal
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Escape-Argument {
  param([string]$arg)

  # If argument contains spaces, quotes, or special characters, quote it
  if ($arg -match '[\s"'']') {
    # Escape internal quotes
    $escaped = $arg -replace '"', '\"'
    return "`"$escaped`""
  }
  return $arg
}

function Invoke-ToolSafe {
  param(
    [string]$Path,
    [string[]]$Args,
    [string]$WorkDir,
    [bool]$UseWT
  )

  # Quote the path if it contains spaces
  $quotedPath = if ($Path -match '\s') { "`"$Path`"" } else { $Path }

  # Escape all arguments
  $escapedArgs = $Args | ForEach-Object { Escape-Argument $_ }

  if ($UseWT) {
    # Windows Terminal launch with proper quoting
    $wtArgs = @(
      'new-tab'
      '--title', (Escape-Argument "Tool: $(Split-Path -Leaf $Path)")
      '-d', (Escape-Argument $WorkDir)
      $quotedPath
    )
    if ($escapedArgs.Count -gt 0) {
      $wtArgs += $escapedArgs
    }

    Write-Host "Launching via Windows Terminal: wt $($wtArgs -join ' ')" -ForegroundColor Cyan
    & wt.exe $wtArgs
  }
  else {
    # Start-Process with proper quoting
    Write-Host "Launching: $quotedPath $($escapedArgs -join ' ')" -ForegroundColor Cyan

    $processArgs = @{
      FilePath = $Path
      WorkingDirectory = $WorkDir
      PassThru = $true
    }

    if ($escapedArgs.Count -gt 0) {
      $processArgs['ArgumentList'] = $escapedArgs
    }

    Start-Process @processArgs
  }
}

# Validate tool path exists
if (-not (Test-Path -LiteralPath $ToolPath)) {
  Write-Error "Tool not found: $ToolPath"
  exit 1
}

# Validate working directory
if (-not (Test-Path -LiteralPath $WorkingDirectory)) {
  Write-Warning "Working directory not found, using current: $PWD"
  $WorkingDirectory = $PWD
}

# Launch the tool
try {
  Invoke-ToolSafe -Path $ToolPath -Args $Arguments -WorkDir $WorkingDirectory -UseWT:$UseWindowsTerminal
  Write-Host "Tool launched successfully" -ForegroundColor Green
}
catch {
  Write-Error "Failed to launch tool: $($_.Exception.Message)"
  exit 1
}
