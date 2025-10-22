# CLI Orchestrator GUI - User Guide

## Overview

The CLI Orchestrator GUI provides a professional, full-featured graphical interface for workflow management, execution monitoring, cost tracking, and artifact viewing. Built with PyQt6, it offers an intuitive alternative to the command-line interface while maintaining full access to all orchestrator features.

## Installation

### Prerequisites
- Python 3.9 or higher
- CLI Orchestrator installed (`pip install -e .` from the repository root)

### Installing GUI Dependencies

```bash
# Install with GUI support
pip install -e .[gui]

# Or explicitly install PyQt6
pip install PyQt6>=6.4.0
```

### Verifying Installation

```bash
# Launch the GUI
cli-orchestrator-gui

# Or run directly from Python
python -m gui_terminal.main
```

## Interface Overview

The CLI Orchestrator GUI features a modern tabbed interface with six main sections:

### 1. 📋 Workflows Tab
Browse, configure, and execute workflows.

**Components:**
- **Workflow Browser** (Left Panel)
  - Categorized tree view of available workflows
  - Search/filter functionality
  - Workflow metadata display (steps, type, description)

- **Configuration Panel** (Right Panel)
  - Dynamic input form generation based on workflow requirements
  - File pickers for path inputs
  - Validation before execution
  - Dry-run option for safe testing

**Usage:**
1. Browse workflows in the left panel
2. Click to select a workflow
3. Configure inputs in the right panel
4. Click "▶ Execute Workflow" to run

### 2. ▶ Execution Tab
Monitor workflow execution in real-time.

**Features:**
- Execution history list (last 20 runs)
- Real-time progress bar with step tracking
- Live output streaming with color coding
- Execution metadata (duration, tokens, status)
- Cancel execution capability

**Status Color Coding:**
- 🔵 Blue: Running
- 🟢 Green: Completed successfully
- 🔴 Red: Failed
- 🟡 Yellow: Cancelled

### 3. 📦 Artifacts Tab
Browse and view workflow execution artifacts.

**Features:**
- File tree browser for artifacts directory
- Syntax-highlighted JSON/JSONL viewer
- Schema validation status indicators
- File metadata display (size, modified time)
- Copy to clipboard functionality

**Supported Formats:**
- JSON with pretty-printing and validation
- JSONL (one JSON per line)
- YAML workflow files
- Python, JavaScript, TypeScript source code
- Markdown documentation

### 4. 💰 Cost Tracking Tab
Monitor token usage and manage budgets.

**Displays:**
- **Budget Overview Card**
  - Progress bar showing % of budget used
  - Total tokens consumed
  - Budget limit
  - Remaining tokens
  - Estimated cost in USD

- **Usage Metrics**
  - Session tokens
  - Daily usage
  - Weekly usage
  - Monthly usage

- **Provider Breakdown**
  - Tokens and cost by AI provider
  - Highlighting of free providers (DeepSeek)

- **Recent Activity**
  - List of recent workflow executions with token counts

**Budget Alerts:**
- 🟢 Green (< 75%): Normal usage
- 🟡 Yellow (75-90%): Warning
- 🔴 Red (> 90%): Critical

### 5. 💻 Terminal Tab
Direct command-line interface within the GUI.

**Features:**
- Command input with history (arrow keys)
- Real-time output streaming
- Security policy enforcement
- Command history widget
- Syntax highlighting for output

**Usage:**
```bash
# Execute orchestrator commands
cli-orchestrator run .ai/workflows/PY_EDIT_TRIAGE.yaml --files "src/**/*.py"

# Or any system command
git status
pytest tests/
```

### 6. ⚙ Settings Tab
Configure GUI preferences and paths.

**Settings:**
- **Paths**
  - Workflows directory (default: `.ai/workflows`)
  - Artifacts directory (default: `artifacts`)

- **Preferences**
  - Auto-refresh workflows on tab change
  - Confirm before workflow execution

## Common Workflows

### Executing a Python Workflow

1. Go to **Workflows** tab
2. Select "Python" category in browser
3. Click "PY_EDIT_TRIAGE.yaml"
4. Configure inputs:
   - Files: `src/**/*.py`
   - Lane: `lane/ai-coding/fix-imports`
5. Optional: Check "Dry Run" to validate without executing
6. Click "▶ Execute Workflow"
7. Switch to **Execution** tab to monitor progress

### Running DeepSeek Analysis (Free!)

1. **Workflows** tab → DeepSeek category
2. Select "DEEPSEEK_ANALYSIS.yaml"
3. Configure:
   - Files: `src/module.py`
   - Prompt: "Analyze for bugs and improvements"
4. Execute
5. View results in **Artifacts** tab (0 cost!)

### Analyzing a GitHub Repository

1. **Workflows** tab → GitHub category
2. Select "GITHUB_REPO_ANALYSIS.yaml"
3. Configure:
   - Repo: `owner/repo`
   - Analysis types: `repository,security,code_quality`
4. Execute
5. Review analysis in **Artifacts** tab

### Monitoring Token Usage

1. Go to **Cost Tracking** tab
2. Click "Refresh" for latest data
3. Review budget usage percentage
4. Check provider breakdown (note free DeepSeek usage!)
5. Set budget alerts if needed

## Keyboard Shortcuts

### Global
- `F5`: Refresh workflows
- `Ctrl+Q`: Exit application

### Terminal Tab
- `↑/↓`: Navigate command history
- `Enter`: Execute command

### Artifacts Tab
- `Ctrl+C`: Copy content to clipboard

## Tips & Best Practices

### 1. Use Dry Run First
Always test workflows with "Dry Run" enabled before executing on production code.

### 2. Monitor Cost Early
Check the Cost Tracking tab regularly when using paid AI providers (Claude, GPT-4).

### 3. Leverage DeepSeek for Free
Use DeepSeek workflows for analysis, review, and refactoring without incurring API costs.

### 4. Review Artifacts
After workflow execution, always check the Artifacts tab to:
- Verify schema validation
- Review generated code changes
- Check analysis reports

### 5. Use Search in Workflow Browser
With many workflows, use the search box to quickly filter by name or category.

### 6. Watch Execution Progress
Switch to Execution tab immediately after starting a workflow to monitor real-time progress.

## Troubleshooting

### GUI Won't Launch

**Error**: `ModuleNotFoundError: No module named 'PyQt6'`

**Solution**:
```bash
pip install PyQt6>=6.4.0
# Or install with all GUI dependencies
pip install -e .[gui]
```

### Workflows Not Found

**Error**: "Workflows directory not found"

**Solution**:
1. Check Settings tab
2. Verify workflows directory path
3. Ensure `.ai/workflows/` exists in project root
4. Click refresh button in Workflow Browser

### Execution Fails Immediately

**Possible Causes**:
1. Invalid workflow configuration
2. Missing required files
3. Budget limit exceeded
4. Backend not available

**Debugging**:
1. Check Execution tab output for error messages
2. Try with "Dry Run" enabled
3. Verify file paths exist
4. Check Cost Tracking tab for budget status

### Artifacts Not Displaying

**Solution**:
1. Click refresh button in Artifacts tab
2. Check Settings → Artifacts directory path
3. Ensure workflows are completing successfully
4. Check Execution tab for workflow errors

### High Token Usage

**Analysis**:
1. Go to Cost Tracking tab
2. Check "Provider Breakdown" table
3. Review "Recent Activity" list
4. Identify expensive workflows

**Mitigation**:
- Use DeepSeek workflows for analysis (free)
- Set lower token limits in workflow policy
- Use "Dry Run" to validate before executing
- Break large workflows into smaller steps

## Advanced Features

### Workflow Browser Search
Supports fuzzy search across:
- Workflow names
- File names
- Descriptions (when implemented)

### Artifact Schema Validation
Automatically validates JSON artifacts against schemas in `.ai/schemas/`:
- ✅ Green checkmark: Valid
- ❌ Red X: Validation errors displayed

### Execution History
Maintains last 100 executions with:
- Workflow name
- Duration
- Token usage
- Success/failure status
- Timestamp

### Cost Estimation
Estimates costs using average pricing:
- Claude Sonnet: ~$9/M tokens
- GPT-4: ~$30/M tokens
- DeepSeek: $0 (local inference)

## Integration with CLI

The GUI complements the CLI. You can:
- Execute GUI workflows from CLI:
  ```bash
  cli-orchestrator run .ai/workflows/PY_EDIT_TRIAGE.yaml
  ```

- View GUI-generated artifacts from CLI:
  ```bash
  cli-orchestrator verify artifacts/diagnostics.json
  ```

- Both share the same:
  - Workflow definitions
  - Artifact storage
  - Cost tracking
  - Configuration

## Getting Help

### In-App Help
- Menu → Help → About
- Menu → Help → Documentation

### External Resources
- GitHub: https://github.com/DICKY1987/cli_multi_rapid_DEV
- Issues: File bug reports or feature requests
- CLAUDE.md: Comprehensive project documentation

## Feature Roadmap

### Coming Soon
- Workflow creation wizard
- Real-time log tailing
- Diff viewer for code changes
- Workflow scheduling
- Export execution reports
- GitHub integration panel (in progress)
- Advanced syntax highlighting
- Theme customization

### Future Enhancements
- Multi-workflow execution
- Workflow templates
- Custom adapters UI
- Metrics dashboards
- WebSocket live updates
