@echo off
REM Verify DeepSeek + AI Tools Setup (Batch version)

echo.
echo === DeepSeek AI Tools Setup Verification ===
echo.

REM Check Ollama
echo [1/5] Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Ollama is running
) else (
    echo   [ERROR] Ollama is not running or not accessible
)

REM Check Aider config
echo.
echo [2/5] Checking Aider configuration...
if exist "%USERPROFILE%\.aider.conf.yml" (
    echo   [OK] Aider config found: %USERPROFILE%\.aider.conf.yml
) else (
    echo   [ERROR] Aider config not found
)

REM Check Continue config
echo.
echo [3/5] Checking Continue configuration...
if exist "%USERPROFILE%\.continue\config.json" (
    echo   [OK] Continue config found: %USERPROFILE%\.continue\config.json
) else (
    echo   [ERROR] Continue config not found
)

REM Check OpenCode installation
echo.
echo [4/5] Checking OpenCode installation...
where opencode >nul 2>&1
if %errorlevel% equ 0 (
    opencode --version >nul 2>&1
    echo   [OK] OpenCode is installed
) else (
    echo   [ERROR] OpenCode not found in PATH
)

REM Check OpenCode wrapper scripts
echo.
echo [5/5] Checking OpenCode wrapper scripts...
set WRAPPER_COUNT=0
if exist "%USERPROFILE%\opencode-deepseek.cmd" set /a WRAPPER_COUNT+=1
if exist "%USERPROFILE%\opencode-deepseek.ps1" set /a WRAPPER_COUNT+=1
if exist "%USERPROFILE%\opencode-deepseek-run.cmd" set /a WRAPPER_COUNT+=1
if exist "%USERPROFILE%\opencode-deepseek-run.ps1" set /a WRAPPER_COUNT+=1

echo   Found %WRAPPER_COUNT%/4 wrapper scripts

REM Summary
echo.
echo === Summary ===
echo.
echo Quick Start:
echo   - Aider:    aider
echo   - OpenCode: %USERPROFILE%\opencode-deepseek.cmd
echo   - Continue: Use VS Code extension (Ctrl+L)
echo.
echo Documentation:
echo   - %USERPROFILE%\OPENCODE-DEEPSEEK-SETUP.md
echo   - %USERPROFILE%\CLI_RESTART\AI-TOOLS-DEEPSEEK-REFERENCE.md
echo.
