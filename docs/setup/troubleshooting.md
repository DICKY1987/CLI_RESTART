# 🔧 CLI Orchestrator Troubleshooting Guide

Comprehensive troubleshooting guide for CLI Orchestrator setup, configuration, and operation issues.

## **📋 Quick Diagnosis**

Run these commands to quickly identify issues:

```bash
# 1. System health check
python -m cli_multi_rapid.main setup validate --comprehensive

# 2. Tool availability check
python -m cli_multi_rapid.main tools doctor

# 3. Configuration validation
python -m cli_multi_rapid.main tools list

# 4. Basic functionality test
python -m cli_multi_rapid.main --help
```

## **🐍 Python & Installation Issues**

### **Python Version Problems**

**Issue**: `Python version 3.8 or older detected`
```bash
# Check Python version
python --version
python3 --version

# Solutions:
# 1. Install Python 3.9+
# 2. Use Python 3.9+ explicitly
python3.9 -m pip install -e .[dev,ai]
python3.9 -m cli_multi_rapid.main --help
```

**Issue**: `Multiple Python versions conflict`
```bash
# Check all Python installations
which -a python
which -a python3

# Use virtual environment
python3 -m venv cli_orchestrator_env
source cli_orchestrator_env/bin/activate  # Unix
cli_orchestrator_env\Scripts\activate     # Windows

pip install -e .[dev,ai]
```

### **Package Installation Issues**

**Issue**: `ModuleNotFoundError: No module named 'cli_multi_rapid'`
```bash
# Verify installation
pip list | grep cli-orchestrator

# Reinstall if missing
pip uninstall cli-orchestrator
pip install -e .[dev,ai]

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

**Issue**: `Permission denied during installation`
```bash
# Use user installation
pip install --user -e .[dev,ai]

# Or use virtual environment (recommended)
python -m venv env
source env/bin/activate  # Unix
env\Scripts\activate     # Windows
pip install -e .[dev,ai]
```

**Issue**: `Dependency conflicts`
```bash
# Check for conflicts
pip check

# Clean install
pip uninstall cli-orchestrator
pip cache purge
pip install -e .[dev,ai]

# Use conda if pip issues persist
conda create -n cli_orchestrator python=3.11
conda activate cli_orchestrator
pip install -e .[dev,ai]
```

## **🔍 Tool Discovery Issues**

### **Few Tools Discovered**

**Issue**: `Found only 2-3 tools, expected 10+`
```bash
# Add custom scan paths
python -m cli_multi_rapid.main tools discover --scan-paths "/usr/local/bin,~/.local/bin,~/scoop/shims"

# Check specific tool locations
ls -la ~/.local/bin
ls -la ~/AppData/Local/Programs  # Windows
ls -la /opt/homebrew/bin         # macOS

# Verify PATH
echo $PATH                       # Unix
echo $env:PATH                   # Windows PowerShell
```

**Issue**: `Tools exist but not discovered`
```bash
# Test tool accessibility
which ruff     # Unix
where ruff     # Windows

# Check execution permissions
ls -la $(which ruff)

# Test tool execution
ruff --version
mypy --version
```

### **Windows-Specific Discovery Issues**

**Issue**: `PowerShell execution policy blocked`
```powershell
# Check current policy
Get-ExecutionPolicy

# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
PowerShell -ExecutionPolicy Bypass -File setup_script.ps1
```

**Issue**: `Tools in non-standard locations`
```powershell
# Check common Windows locations
ls "C:\ProgramData\chocolatey\bin"
ls "$env:LOCALAPPDATA\Microsoft\WindowsApps"
ls "$env:USERPROFILE\scoop\shims"

# Add to discovery paths
python -m cli_multi_rapid.main tools discover --scan-paths "C:\tools,C:\ProgramData\chocolatey\bin"
```

## **📁 File Structure & Git Issues**

### **Repository Structure Problems**

**Issue**: `Not in a git repository`
```bash
# Check if in correct directory
ls -la .git

# Initialize if needed
git init
git remote add origin https://github.com/DICKY1987/cli_multi_rapid_DEV.git

# Clone if starting fresh
git clone https://github.com/DICKY1987/cli_multi_rapid_DEV.git
cd cli_multi_rapid_DEV
```

**Issue**: `Missing required files/directories`
```bash
# Check required structure
ls -la src/cli_multi_rapid/
ls -la .ai/schemas/
ls -la .ai/workflows/

# Download missing files
git fetch origin
git reset --hard origin/main  # WARNING: This will overwrite local changes
```

### **Git Configuration Issues**

**Issue**: `Git operations fail`
```bash
# Check git configuration
git config --list
git config user.name
git config user.email

# Configure if missing
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Test git operations
git status
git log --oneline -5
```

**Issue**: `GitHub authentication problems`
```bash
# Check GitHub CLI authentication
gh auth status

# Re-authenticate if needed
gh auth login

# Test GitHub access
gh repo view DICKY1987/cli_multi_rapid_DEV
```

## **⚙️ Workflow Execution Issues**

### **Workflow File Problems**

**Issue**: `Workflow file not found`
```bash
# Check workflow file exists
ls -la .ai/workflows/
ls -la .ai/workflows/templates/

# Use absolute path
python -m cli_multi_rapid.main run /full/path/to/workflow.yaml

# Check current directory
pwd
```

**Issue**: `YAML syntax errors`
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.ai/workflows/CODE_QUALITY.yaml'))"

# Check for common issues
# - Incorrect indentation
# - Missing quotes around special characters
# - Tab characters instead of spaces
```

### **Schema Validation Failures**

**Issue**: `Schema validation failed`
```bash
# Check schema files exist
ls -la .ai/schemas/

# Validate specific schema
python -m cli_multi_rapid.main verify artifacts/analysis.json --schema .ai/schemas/diagnostics.schema.json

# Use built-in validation
python -c "
import json, jsonschema
with open('artifacts/analysis.json') as f: data = json.load(f)
with open('.ai/schemas/diagnostics.schema.json') as f: schema = json.load(f)
jsonschema.validate(data, schema)
print('Valid!')
"
```

### **Adapter Execution Failures**

**Issue**: `Actor 'vscode_diagnostics' failed`
```bash
# Test adapter directly
python -m cli_multi_rapid.main step execute --actor vscode_diagnostics --files "src/cli_multi_rapid/main.py"

# Check adapter logs
ls -la logs/
tail -f logs/workflow_execution.log

# Verify required tools
ruff --version
mypy --version
```

## **🤖 AI Integration Issues**

### **API Token Problems**

**Issue**: `Anthropic API key not configured`
```bash
# Check environment variables
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Set environment variables
export ANTHROPIC_API_KEY="your_key_here"         # Unix
$env:ANTHROPIC_API_KEY = "your_key_here"         # Windows PowerShell

# Test API connectivity
python -c "
import anthropic
client = anthropic.Client()
print('Anthropic API: OK')
"
```

**Issue**: `Token usage exceeded budget`
```bash
# Check current usage
python -m cli_multi_rapid.main cost report --detailed

# Reset cost tracking (if needed)
rm -rf cost/
rm -rf logs/cost_*.json

# Set budget limits
python -m cli_multi_rapid.main run workflow.yaml --max-tokens 1000
```

### **AI Tool Installation**

**Issue**: `aider not found`
```bash
# Install aider
pip install aider-chat

# Verify installation
aider --version
which aider

# Test with CLI orchestrator
python -m cli_multi_rapid.main step execute --actor ai_editor --with '{"tool": "aider"}'
```

## **💾 Performance & Memory Issues**

### **Slow Execution**

**Issue**: `Workflow takes too long`
```bash
# Use parallel execution
python -m cli_multi_rapid.main run workflow.yaml --files "src/**/*.py" --coordination-mode parallel

# Reduce scope
python -m cli_multi_rapid.main run workflow.yaml --files "src/cli_multi_rapid/main.py"

# Enable caching
# Set environment variable
export CLI_ORCHESTRATOR_CACHE=true
```

**Issue**: `High memory usage`
```bash
# Monitor memory usage
top -p $(pgrep -f cli_multi_rapid)  # Unix
# Use Task Manager on Windows

# Reduce parallel workers
# Edit workflow.yaml:
# resources:
#   max_parallel: 2
#   max_memory: "2GB"
```

### **Disk Space Issues**

**Issue**: `No space left on device`
```bash
# Check disk usage
df -h .                    # Unix
dir                        # Windows

# Clean up artifacts
rm -rf artifacts/old/
rm -rf logs/*.log

# Configure artifact retention
# Edit workflow.yaml:
# artifacts:
#   retention_days: 7
#   compression: true
```

## **🔄 Platform-Specific Issues**

### **Windows Issues**

**Issue**: `Path too long error`
```powershell
# Enable long paths (requires admin)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# Use shorter paths
# Move project to C:\cli\ instead of deep nested path
```

**Issue**: `Windows Defender blocking execution`
```powershell
# Add exclusion for project directory
Add-MpPreference -ExclusionPath "C:\path\to\cli_multi_rapid_DEV"

# Temporarily disable real-time protection (use with caution)
Set-MpPreference -DisableRealtimeMonitoring $true
```

### **macOS Issues**

**Issue**: `Command not found despite installation`
```bash
# Check PATH includes Homebrew
echo $PATH | grep homebrew

# Add to PATH if missing
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For Intel Macs
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
```

**Issue**: `Permission denied for tool execution`
```bash
# Fix permissions
chmod +x /opt/homebrew/bin/ruff
chmod +x ~/.local/bin/*

# Check and fix ownership
ls -la ~/.local/bin/
sudo chown $USER ~/.local/bin/*
```

### **Linux Issues**

**Issue**: `Snap/Flatpak tool isolation`
```bash
# Check if tools are in snap
snap list | grep -E "(code|git)"

# Use classic snaps when possible
sudo snap install code --classic

# Or use alternative installation methods
# APT: sudo apt install code
# Download: wget https://...
```

## **🚨 Emergency Recovery**

### **Complete Reset**

If everything is broken:

```bash
# 1. Back up any important work
cp -r artifacts/ ~/backup_artifacts/
cp config/discovered_tools.yaml ~/backup_config.yaml

# 2. Clean slate reinstall
rm -rf .venv env/                    # Remove virtual environment
pip uninstall cli-orchestrator      # Remove package
rm -rf config/ artifacts/ logs/     # Remove generated files

# 3. Fresh setup
git reset --hard origin/main        # Reset to clean state
python -m venv fresh_env
source fresh_env/bin/activate       # Unix
fresh_env\Scripts\activate          # Windows
pip install -e .[dev,ai]

# 4. Re-run setup
python -m cli_multi_rapid.main setup quick-start
```

### **Restore from Backup**

```bash
# Restore configuration
cp ~/backup_config.yaml config/discovered_tools.yaml

# Restore important artifacts
cp -r ~/backup_artifacts/ artifacts/

# Test functionality
python -m cli_multi_rapid.main setup validate
```

## **📞 Getting Additional Help**

### **Diagnostic Information Collection**

```bash
# Generate comprehensive diagnostic report
python -m cli_multi_rapid.main setup validate --comprehensive --generate-guide

# System information
python --version
pip list | grep -E "(cli-orchestrator|typer|rich|pydantic)"
git --version

# Platform information
uname -a                # Unix
systeminfo              # Windows
```

### **Log Analysis**

```bash
# Check recent logs
ls -la logs/
tail -50 logs/workflow_execution.log
tail -50 logs/error.log

# Search for specific errors
grep -i "error" logs/*.log
grep -i "failed" logs/*.log
```

### **Community Resources**

- **GitHub Issues**: Report bugs and get help
- **Documentation**: Check updated docs in `docs/`
- **Examples**: Look at working examples in `.ai/workflows/`
- **Code**: Review source code for understanding

---

**Need More Help?**

If this guide doesn't solve your issue:

1. **Check GitHub Issues**: Search existing issues for your problem
2. **Create Detailed Issue**: Include error messages, system info, and steps to reproduce
3. **Provide Context**: Share relevant logs and configuration files
4. **Test Minimal Case**: Try to reproduce with minimal example

**Generated by CLI Orchestrator Enhanced Setup System**
*Version 1.1.0 - Troubleshooting Guide*
