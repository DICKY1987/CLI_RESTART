# AI Tools + DeepSeek Quick Reference

All three CLI tools (Aider, Continue, OpenCode) are now configured to use **DeepSeek Coder V2 Lite** via Ollama running locally.

## Quick Commands

### Aider
```bash
# Start aider (auto-uses DeepSeek)
aider

# With specific files
aider src/main.py tests/test_main.py

# Read-only mode
aider --read-only
```

### Continue
Continue is configured via VS Code extension. The config at `C:\Users\Richard Wilks\.continue\config.json` automatically uses DeepSeek.

**VS Code usage:**
- Press `Ctrl+L` to open Continue chat
- Press `Ctrl+I` to use inline editing
- Autocomplete is powered by DeepSeek

### OpenCode (via wrapper scripts)

#### Interactive TUI Mode
```bash
# From anywhere (if added to PATH)
opencode-deepseek

# From user directory
C:\Users\Richard Wilks\opencode-deepseek.cmd

# With project path
opencode-deepseek C:\path\to\project

# Continue last session
opencode-deepseek -c
```

#### Quick Command Mode
```bash
# From anywhere (if added to PATH)
opencode-deepseek-run "your message here"

# From user directory
C:\Users\Richard Wilks\opencode-deepseek-run.cmd "your message here"

# Examples
opencode-deepseek-run "explain the code in main.py"
opencode-deepseek-run "add unit tests for the database module"
opencode-deepseek-run "refactor this function to be more efficient"
```

## Configuration Files

| Tool | Config Location | Status |
|------|----------------|--------|
| **Aider** | `C:\Users\Richard Wilks\.aider.conf.yml` | ✅ Configured |
| **Continue** | `C:\Users\Richard Wilks\.continue\config.json` | ✅ Configured |
| **OpenCode** | Wrapper scripts in user directory | ✅ Ready |
| **Ollama** | Running on `http://localhost:11434` | ✅ Active |

## Wrapper Scripts Location

```
C:\Users\Richard Wilks\
├── opencode-deepseek.cmd          # Batch file for TUI mode
├── opencode-deepseek.ps1          # PowerShell for TUI mode
├── opencode-deepseek-run.cmd      # Batch file for command mode
├── opencode-deepseek-run.ps1      # PowerShell for command mode
└── OPENCODE-DEEPSEEK-SETUP.md     # Detailed setup guide
```

## Add to PATH (Optional)

**PowerShell (recommended):**
```powershell
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = "C:\Users\Richard Wilks"
if ($userPath -notlike "*$newPath*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$newPath", "User")
    Write-Host "Added to PATH. Restart terminal to use commands from anywhere."
}
```

**Command Prompt (as Administrator):**
```cmd
setx PATH "%PATH%;C:\Users\Richard Wilks"
```

After adding to PATH, restart your terminal.

## Verify Setup

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check DeepSeek model is available
# Should show: deepseek-coder-v2:lite

# Test aider
aider --version

# Test opencode
opencode --version

# Test wrapper (from user directory)
cd C:\Users\Richard Wilks
opencode-deepseek.cmd --help
```

## Model Details

**DeepSeek Coder V2 Lite**
- Parameters: 15.7B
- Size: 8.9 GB (Q4_0 quantization)
- Running: Locally via Ollama
- API: `http://localhost:11434`
- Cost: Free (local inference)

## Common Use Cases

### Code Review
```bash
# Aider
aider --read-only src/module.py
# Ask: "Review this code for bugs and improvements"

# OpenCode
opencode-deepseek-run "review src/module.py for security issues"
```

### Code Generation
```bash
# Aider
aider
# Ask: "Create a REST API endpoint for user authentication"

# OpenCode
opencode-deepseek-run "generate a FastAPI endpoint for user login"
```

### Refactoring
```bash
# Aider (interactive)
aider src/legacy_code.py
# Ask: "Refactor this to use modern Python best practices"

# OpenCode (quick)
opencode-deepseek-run "refactor src/legacy_code.py to improve readability"
```

### Testing
```bash
# Aider
aider src/calculator.py
# Ask: "Add pytest unit tests for all functions"

# OpenCode
opencode-deepseek-run "generate pytest tests for src/calculator.py"
```

## Troubleshooting

### Ollama not responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama if needed
# (Check system services or restart Ollama application)
```

### Model not found
```bash
# List installed models
curl http://localhost:11434/api/tags

# Pull DeepSeek if missing
ollama pull deepseek-coder-v2:lite
```

### PowerShell execution policy
```powershell
# Allow running local scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Resources

- **Aider docs**: https://aider.chat/docs/
- **Continue docs**: https://continue.dev/docs
- **OpenCode docs**: https://opencode.ai/docs
- **Ollama docs**: https://ollama.ai/docs
- **DeepSeek**: https://deepseek.com/

## Support

For detailed setup information, see `OPENCODE-DEEPSEEK-SETUP.md` in your user directory.
