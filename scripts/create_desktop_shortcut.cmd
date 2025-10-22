@echo off
REM Create Desktop Shortcut for CLI Orchestrator GUI
REM Named "CLI_SYSTEM"

echo Creating desktop shortcut: CLI_SYSTEM
powershell -ExecutionPolicy Bypass -File "%~dp0create_desktop_shortcut.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Success! You can now launch CLI Orchestrator GUI from your desktop.
    pause
) else (
    echo.
    echo Error creating shortcut. Please run PowerShell script manually.
    pause
)
