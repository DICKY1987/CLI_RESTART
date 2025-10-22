@echo off
cd /d "C:\Users\Richard Wilks\CLI_RESTART"
python -m gui_terminal.main %*
if errorlevel 1 (
    echo.
    echo ERROR: GUI failed to launch. Press any key to close...
    pause >nul
)
