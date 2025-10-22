# Create Desktop Shortcut for CLI Orchestrator GUI
# Creates a shortcut named "CLI_SYSTEM" on the user's desktop

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

# Create icon if it doesn't exist (placeholder)
if (-not (Test-Path $IconPath)) {
    Write-Host "Icon file not found, using default Python icon" -ForegroundColor Yellow
    $IconPath = $PythonExe
}

# Create WScript Shell object
$WScriptShell = New-Object -ComObject WScript.Shell

# Create shortcut
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonExe
$Shortcut.Arguments = "-m gui_terminal.main"
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = $Description
$Shortcut.IconLocation = $IconPath
$Shortcut.WindowStyle = 1  # Normal window

# Save shortcut
$Shortcut.Save()

Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $ShortcutPath" -ForegroundColor Gray
Write-Host "Target: $PythonExe -m gui_terminal.main" -ForegroundColor Gray
Write-Host "Working Directory: $ProjectRoot" -ForegroundColor Gray
Write-Host ""
Write-Host "Double-click 'CLI_SYSTEM' on your desktop to launch the GUI!" -ForegroundColor Cyan
