# 🚀 CLI Orchestrator Quick Start Guide

This guide will help you get the CLI Orchestrator up and running quickly with automated tool discovery and validation.

## **🎯 Quick Setup (15-20 minutes)**

### **Prerequisites**
- Python 3.9+ installed
- Git installed and configured
- Access to command line (PowerShell on Windows, bash/zsh on Unix)

### **Step 1: Installation**

```bash
# Clone the repository
git clone https://github.com/DICKY1987/cli_multi_rapid_DEV.git
cd cli_multi_rapid_DEV

# Install with all features
pip install -e .[dev,ai]
```

### **Step 2: Quick Start Setup**

Run the automated quick start command:

```bash
# Automated setup with tool discovery and validation
python -m cli_multi_rapid.main setup quick-start

# Alternative: Step-by-step setup
python -m cli_multi_rapid.main setup validate --comprehensive
python -m cli_multi_rapid.main tools discover --generate-config
```

### **Step 3: Verify Installation**

```bash
# Check system health
python -m cli_multi_rapid.main tools doctor

# List discovered tools
python -m cli_multi_rapid.main tools list

# Run a sample workflow
python -m cli_multi_rapid.main run .ai/workflows/samples/validation_test.yaml --dry-run
```

## **🔧 Platform-Specific Setup**

### **Windows Users**

```powershell
# Use PowerShell for best compatibility
# Run tool discovery with Windows-specific paths
python -m cli_multi_rapid.main tools discover --platform windows

# Generate Windows setup script
python -m cli_multi_rapid.main setup install --platform windows

# Run the generated setup script
PowerShell -ExecutionPolicy Bypass -File scripts/setup/install_cli_orchestrator.ps1
```

### **macOS/Linux Users**

```bash
# Run tool discovery for Unix systems
python -m cli_multi_rapid.main tools discover --platform unix

# Generate Unix setup script
python -m cli_multi_rapid.main setup install --platform unix

# Run the generated setup script
chmod +x scripts/setup/install_cli_orchestrator.sh
./scripts/setup/install_cli_orchestrator.sh
```

## **📋 What Gets Discovered**

The automated setup will find and configure these types of tools:

### **Core Development Tools**
- **Git & GitHub**: `git`, `gh` (GitHub CLI)
- **Editors**: `code` (VS Code), `vim`, `nano`
- **Python**: `python`, `pip`, `pipx`
- **Node.js**: `node`, `npm`, `npx`

### **Python Quality Tools**
- **Linters**: `ruff`, `pylint`, `flake8`
- **Type Checkers**: `mypy`
- **Formatters**: `black`, `isort`
- **Security**: `bandit`, `semgrep`

### **Testing Tools**
- **Test Runners**: `pytest`, `coverage`
- **Build Tools**: `tox`, `nox`

### **AI & Modern Tools**
- **AI CLIs**: `claude`, `aider`, `cursor`
- **Containers**: `docker`, `docker-compose`
- **Package Managers**: `scoop`, `brew`, `chocolatey`

## **🧪 Testing Your Setup**

### **Basic Functionality Test**

```bash
# 1. Check CLI responds
python -m cli_multi_rapid.main --help

# 2. Validate system setup
python -m cli_multi_rapid.main setup validate

# 3. Test tool discovery
python -m cli_multi_rapid.main tools doctor

# 4. Run sample workflow
python -m cli_multi_rapid.main run .ai/workflows/templates/comprehensive_quality_workflow.yaml --dry-run --files "src/**/*.py"
```

### **Advanced Functionality Test**

```bash
# Test individual adapters
python -m cli_multi_rapid.main run .ai/workflows/CODE_QUALITY.yaml --files "src/cli_multi_rapid/main.py" --dry-run

# Test coordination features
python -m cli_multi_rapid.main coordination plan .ai/workflows/PY_EDIT_TRIAGE.yaml .ai/workflows/CODE_QUALITY.yaml

# Test cost tracking
python -m cli_multi_rapid.main cost report --detailed
```

## **🎯 Quick Commands Reference**

### **Setup Commands**
```bash
# Quick start (recommended for new users)
python -m cli_multi_rapid.main setup quick-start

# Comprehensive validation
python -m cli_multi_rapid.main setup validate --comprehensive

# Generate platform installer
python -m cli_multi_rapid.main setup install --platform auto
```

### **Tool Management**
```bash
# Discover tools automatically
python -m cli_multi_rapid.main tools discover

# Check tool health
python -m cli_multi_rapid.main tools doctor

# List all tools with versions
python -m cli_multi_rapid.main tools list
```

### **Workflow Operations**
```bash
# Run workflow with dry-run
python -m cli_multi_rapid.main run <workflow.yaml> --dry-run

# Run with specific files
python -m cli_multi_rapid.main run <workflow.yaml> --files "src/**/*.py"

# Run with budget limit
python -m cli_multi_rapid.main run <workflow.yaml> --max-tokens 1000
```

## **📊 Expected Results**

After successful setup, you should see:

```
🎉 SETUP COMPLETE!
=================
Working tools: 15-25
Tools in PATH: 8-12
Custom paths: 5-10

✅ Core functionality verified
✅ Workflows executable
✅ Configuration generated
✅ Platform setup complete
```

## **🔧 Troubleshooting**

### **Common Issues**

**Tool Discovery Finds Few Tools**
```bash
# Add custom scan paths
python -m cli_multi_rapid.main tools discover --scan-paths "/custom/path,/another/path"

# Check specific locations
ls -la ~/.local/bin
ls -la ~/scoop/shims  # Windows
ls -la /usr/local/bin  # macOS/Linux
```

**Python Import Errors**
```bash
# Reinstall with all dependencies
pip uninstall cli-orchestrator
pip install -e .[dev,ai]

# Verify Python path
python -c "import sys; print(sys.path)"
```

**Permission Issues (Windows)**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
PowerShell -ExecutionPolicy Bypass -File setup_script.ps1
```

**Git Issues**
```bash
# Check git configuration
git config --list
git remote -v

# Re-initialize if needed
git remote set-url origin https://github.com/DICKY1987/cli_multi_rapid_DEV.git
```

### **Getting Help**

**Check System Status**
```bash
python -m cli_multi_rapid.main setup validate --comprehensive --generate-guide
```

**View Generated Documentation**
```bash
# Quick start guide will be generated at:
# docs/setup/quick_start_validation.md
```

**Enable Verbose Output**
```bash
# Most commands support verbose flags
python -m cli_multi_rapid.main tools discover --verbose
python -m cli_multi_rapid.main setup validate --comprehensive
```

## **🎯 Next Steps**

Once setup is complete:

1. **Explore Workflows**: Check `.ai/workflows/` for available workflows
2. **Review Templates**: Look at `.ai/workflows/templates/` for advanced examples
3. **Customize Configuration**: Edit `config/discovered_tools.yaml` as needed
4. **Set Up CI/CD**: Integrate with your development workflow
5. **Join Community**: Contribute to the project and share feedback

## **📚 Additional Resources**

- **Main Documentation**: `README.md`
- **CLAUDE.md**: Project-specific guidance for Claude Code
- **Workflow Examples**: `.ai/workflows/templates/`
- **Scripts**: `scripts/setup/` for platform-specific automation
- **Issues & Support**: GitHub repository issues

---

**Generated by CLI Orchestrator Enhanced Setup System**
*Version 1.1.0 - Last updated: {{ current_date }}*
