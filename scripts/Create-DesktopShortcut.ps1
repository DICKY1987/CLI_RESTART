<#
 .SYNOPSIS
   Creates a desktop shortcut for the CLI_RESTART launcher.

 .DESCRIPTION
   Creates a .lnk shortcut on the user's desktop that launches restart.ps1
   with a default or specified configuration file.

 .PARAMETER ConfigPath
   Path to the configuration file (relative to repository root).
   Default: config\workspace.json

 .PARAMETER ShortcutName
   Name for the desktop shortcut (without .lnk extension).
   Default: CLI_RESTART Launcher

 .PARAMETER IconPath
   Optional path to a custom icon file (.ico).

 .EXAMPLE
   .\Create-DesktopShortcut.ps1

 .EXAMPLE
   .\Create-DesktopShortcut.ps1 -ConfigPath "config\production.json" -ShortcutName "Production Launcher"
#>

param(
  [string]$ConfigPath = "config\workspace.json",
  [string]$ShortcutName = "CLI_RESTART Launcher",
  [string]$IconPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Get repository root (parent of scripts directory)
$repoRoot = Split-Path -Parent $PSScriptRoot
$restartScript = Join-Path $repoRoot 'restart.ps1'

# Verify restart.ps1 exists
if (-not (Test-Path -LiteralPath $restartScript)) {
  Write-Error "restart.ps1 not found at: $restartScript"
  exit 1
}

# Build full config path
$fullConfigPath = Join-Path $repoRoot $ConfigPath

# Get desktop path
$desktopPath = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktopPath "$ShortcutName.lnk"

# Create WScript.Shell COM object
$wshell = New-Object -ComObject WScript.Shell

try {
  # Create shortcut
  $shortcut = $wshell.CreateShortcut($shortcutPath)

  # Set target to PowerShell with restart.ps1
  $shortcut.TargetPath = "pwsh.exe"

  # Arguments: -NoProfile -File restart.ps1 -ConfigPath <path>
  $shortcut.Arguments = "-NoProfile -File `"$restartScript`" -ConfigPath `"$fullConfigPath`""

  # Set working directory to repository root
  $shortcut.WorkingDirectory = $repoRoot

  # Set description
  $shortcut.Description = "Launch CLI_RESTART with configuration: $ConfigPath"

  # Set icon if provided
  if ($IconPath -and (Test-Path -LiteralPath $IconPath)) {
    $shortcut.IconLocation = $IconPath
  }
  else {
    # Use PowerShell icon as default
    $pwshPath = (Get-Command pwsh.exe -ErrorAction SilentlyContinue).Source
    if ($pwshPath) {
      $shortcut.IconLocation = "$pwshPath,0"
    }
  }

  # Save shortcut
  $shortcut.Save()

  Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
  Write-Host "  Location: $shortcutPath" -ForegroundColor Cyan
  Write-Host "  Target: $restartScript" -ForegroundColor Cyan
  Write-Host "  Config: $fullConfigPath" -ForegroundColor Cyan

  # Verify shortcut was created
  if (Test-Path -LiteralPath $shortcutPath) {
    Write-Host "`nShortcut verified. You can now launch from your desktop." -ForegroundColor Green
  }
  else {
    Write-Warning "Shortcut file not found after creation. This may be a permissions issue."
  }
}
catch {
  Write-Error "Failed to create desktop shortcut: $($_.Exception.Message)"
  exit 1
}
finally {
  # Release COM object
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wshell) | Out-Null
  [System.GC]::Collect()
  [System.GC]::WaitForPendingFinalizers()
}
