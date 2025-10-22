@echo off
echo Testing GUI Launch...
echo.
cd /d "C:\Users\Richard Wilks\CLI_RESTART"
python -m gui_terminal.main
if errorlevel 1 (
    echo.
    echo ERROR: GUI failed to launch!
    pause
) else (
    echo.
    echo GUI closed successfully
)
