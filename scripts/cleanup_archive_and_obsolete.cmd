@echo off
REM Batch wrapper for cleanup_archive_and_obsolete.ps1
REM This allows double-clicking or running from cmd.exe

setlocal

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Default to dry-run mode for safety
set DRY_RUN=-DryRun:$true

REM Check for command line arguments
if "%1"=="--execute" set DRY_RUN=-DryRun:$false
if "%1"=="-execute" set DRY_RUN=-DryRun:$false
if "%1"=="--force" set DRY_RUN=-DryRun:$false -Force

echo ================================================
echo   Archive and Obsolete Files Cleanup
echo ================================================
echo.

if "%DRY_RUN%"=="-DryRun:$true" (
    echo MODE: DRY-RUN ^(safe preview, no files deleted^)
    echo.
    echo To actually delete files, run:
    echo   cleanup_archive_and_obsolete.cmd --execute
    echo.
) else (
    echo MODE: EXECUTE ^(files will be deleted^)
    echo.
)

REM Run the PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%cleanup_archive_and_obsolete.ps1" %DRY_RUN%

endlocal
pause
