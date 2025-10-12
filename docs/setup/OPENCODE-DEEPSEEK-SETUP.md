# OpenCode + DeepSeek Setup Guide

## Wrapper Scripts Created

I've created wrapper scripts in `C:\Users\Richard Wilks\` to make OpenCode use DeepSeek automatically:

### 1. **opencode-deepseek.cmd** / **opencode-deepseek.ps1**
Launch OpenCode TUI with DeepSeek model

**Usage:**
```bash
# Batch file (works in cmd, PowerShell, or Terminal)
opencode-deepseek

# Or with a specific project
opencode-deepseek C:\path\to\project

# Continue last session
opencode-deepseek -c

# With additional options
opencode-deepseek --print-logs
```

**PowerShell:**
```powershell
.\opencode-deepseek.ps1
.\opencode-deepseek.ps1 C:\path\to\project
```

### 2. **opencode-deepseek-run.cmd** / **opencode-deepseek-run.ps1**
Run OpenCode with a direct message (non-interactive mode)

**Usage:**
```bash
# Batch file
opencode-deepseek-run "explain this code"
opencode-deepseek-run "add error handling to main.py"

# PowerShell
.\opencode-deepseek-run.ps1 "explain this code"
```

## Adding to PATH (Optional)

To use these scripts from anywhere without specifying the full path:

### Option 1: Add User Directory to PATH (Recommended)

**Using PowerShell:**
```powershell
# Add your user directory to PATH permanently
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = "C:\Users\Richard Wilks"
if ($userPath -notlike "*$newPath*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$newPath", "User")
    echo "Added to PATH. Restart your terminal to use the commands."
}
```

**Using Command Prompt (Run as Administrator):**
```cmd
setx PATH "%PATH%;C:\Users\Richard Wilks"
```

After adding to PATH, restart your terminal, then you can run from anywhere:
```bash
opencode-deepseek
opencode-deepseek-run "your message"
```

### Option 2: Copy to Existing PATH Location

Copy the scripts to a directory already in your PATH (like where npm is installed):

```powershell
Copy-Item "C:\Users\Richard Wilks\opencode-deepseek.*" "C:\Users\Richard Wilks\AppData\Roaming\npm\"
```

### Option 3: Create PowerShell Aliases (Session-based)

Add to your PowerShell profile for session-based aliases:

```powershell
# Edit your PowerShell profile
notepad $PROFILE

# Add these lines:
function opencode-deepseek { opencode -m ollama/deepseek-coder-v2:lite @args }
function opencode-deepseek-run { opencode run -m ollama/deepseek-coder-v2:lite @args }
```

## Configuration Summary

### Aider ✅
- **Config**: `C:\Users\Richard Wilks\.aider.conf.yml`
- **Model**: `ollama/deepseek-coder-v2:lite`
- **Usage**: Just run `aider`

### Continue ✅
- **Config**: `C:\Users\Richard Wilks\.continue\config.json`
- **Model**: `deepseek-coder-v2:lite` via Ollama
- **API**: `http://localhost:11434`
- **Usage**: Use Continue VS Code extension (auto-configured)

### OpenCode ✅
- **Config**: Wrapper scripts in `C:\Users\Richard Wilks\`
- **Model**: `ollama/deepseek-coder-v2:lite`
- **Usage**: Run wrapper scripts as shown above

### Ollama ✅
- **Status**: Running on `http://localhost:11434`
- **Model**: `deepseek-coder-v2:lite` (8.9GB, Q4_0)

## Quick Start Examples

### Interactive TUI Mode
```bash
# Navigate to your project
cd C:\path\to\your\project

# Launch OpenCode with DeepSeek
opencode-deepseek
```

### Quick Command Mode
```bash
# Run a single command
opencode-deepseek-run "analyze this codebase and suggest improvements"

# Generate code
opencode-deepseek-run "create a python function to parse JSON files"

# Review code
opencode-deepseek-run "review the code in main.py for potential bugs"
```

### Using Aider
```bash
cd C:\path\to\your\project
aider
```

## Troubleshooting

### OpenCode doesn't recognize the model
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check DeepSeek model is installed: Should see `deepseek-coder-v2:lite` in the output

### Scripts not found
- Use full path: `C:\Users\Richard Wilks\opencode-deepseek.cmd`
- Or add directory to PATH as shown above

### Permission denied (PowerShell)
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Model Information

**DeepSeek Coder V2 Lite**
- Size: 8.9 GB
- Quantization: Q4_0
- Parameter size: 15.7B
- Optimized for: Code generation, analysis, and assistance
- Running locally via Ollama (no API costs!)
