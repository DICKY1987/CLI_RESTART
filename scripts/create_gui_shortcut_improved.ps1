# Create Desktop Shortcut for CLI Orchestrator GUI - Improved Version
# This version includes error handling and shows error messages if GUI fails

param(
    [string]$ShortcutName = "CLI_SYSTEM",
    [string]$Description = "CLI Orchestrator - Professional Workflow Management"
)

Write-Host "Creating desktop shortcut: $ShortcutName" -ForegroundColor Cyan

# Get paths
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "$ShortcutName.lnk"
$PythonExe = (Get-Command python).Source
$ScriptDir = $PSScriptRoot
$ProjectRoot = Split-Path $ScriptDir -Parent
$IconPath = Join-Path $ProjectRoot "docs\gui\cli_system.ico"

# Create a launcher batch file that shows errors
$LauncherBat = Join-Path $ProjectRoot "launch_gui.bat"
$LauncherContent = @"
@echo off
cd /d "$ProjectRoot"
python -m gui_terminal.main %*
if errorlevel 1 (
    echo.
    echo ERROR: GUI failed to launch. Press any key to close...
    pause >nul
)
"@

Write-Host "Creating launcher script: $LauncherBat" -ForegroundColor Gray
Set-Content -Path $LauncherBat -Value $LauncherContent -Encoding ASCII

# Create icon if it doesn't exist (placeholder)
if (-not (Test-Path $IconPath)) {
    Write-Host "Icon file not found, using default Python icon" -ForegroundColor Yellow
    $IconPath = $PythonExe
}

# Create WScript Shell object
$WScriptShell = New-Object -ComObject WScript.Shell

# Create shortcut
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $LauncherBat
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = $Description
$Shortcut.IconLocation = $IconPath
$Shortcut.WindowStyle = 1  # Normal window

# Save shortcut
$Shortcut.Save()

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "SUCCESS: Desktop shortcut created!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "Shortcut Location: " -NoNewline
Write-Host $ShortcutPath -ForegroundColor Cyan
Write-Host "Launcher Script:   " -NoNewline
Write-Host $LauncherBat -ForegroundColor Cyan
Write-Host "Working Directory: " -NoNewline
Write-Host $ProjectRoot -ForegroundColor Cyan
Write-Host ""
Write-Host "Double-click 'CLI_SYSTEM' on your desktop to launch!" -ForegroundColor Yellow
Write-Host ""
