# CLI Orchestrator GUI

## Quick Start

### Installation
```bash
# Install with GUI support
pip install -e .[gui]
```

### Launch
```bash
# Start the GUI
cli-orchestrator-gui
```

## Features

### 📋 Workflow Management
- Browse 15+ pre-built workflows (Python, DeepSeek, GitHub, Code Quality)
- Dynamic configuration forms
- Real-time validation
- Dry-run testing

### ▶ Execution Monitoring
- Live progress tracking
- Step-by-step execution view
- Real-time output streaming
- Execution history (last 100 runs)

### 📦 Artifact Viewing
- File browser for workflow outputs
- JSON/JSONL syntax highlighting
- Schema validation
- Metadata display

### 💰 Cost Tracking
- Real-time token usage monitoring
- Budget alerts (75%, 90% thresholds)
- Provider breakdown (Claude, GPT-4, DeepSeek)
- Cost estimation

### 💻 Integrated Terminal
- Full CLI access within GUI
- Command history
- Security policy enforcement
- Syntax-highlighted output

### ⚙ Configuration
- Customizable paths
- Execution preferences
- Auto-refresh options

## Documentation

- **[Complete User Guide](GUI_USER_GUIDE.md)** - Detailed feature documentation
- **[CLAUDE.md](../../CLAUDE.md)** - Project architecture and development guide

## Architecture

### Components
```
gui_terminal/
├── main.py                          # Entry point
├── gui_bridge.py                    # Backend integration
├── core/
│   └── execution_manager.py         # Workflow execution state
├── ui/
│   ├── main_window_modern.py        # Main tabbed interface
│   ├── workflow_browser.py          # Workflow selector
│   ├── workflow_config.py           # Dynamic input forms
│   ├── execution_dashboard.py       # Execution monitoring
│   ├── cost_dashboard.py            # Token tracking
│   ├── artifact_viewer.py           # File browser/viewer
│   ├── github_panel.py              # GitHub integration
│   └── cli_interface.py             # Terminal widget
└── tests/
    └── gui/                         # GUI unit tests
```

### Technology Stack
- **Framework**: PyQt6
- **Backend**: CLI Orchestrator (cli_multi_rapid)
- **Threading**: QThread for async execution
- **Signals/Slots**: Qt event system

## Workflow Examples

### Execute Python Analysis
1. **Workflows** tab → Select "PY_EDIT_TRIAGE.yaml"
2. Configure: `files: src/**/*.py`
3. Click **Execute**
4. Monitor in **Execution** tab

### Free DeepSeek Review (No API Cost!)
1. **Workflows** tab → DeepSeek → "DEEPSEEK_CODE_REVIEW.yaml"
2. Configure: `files: src/module.py`
3. Execute
4. View results in **Artifacts** tab

### GitHub Repository Analysis
1. **Workflows** tab → GitHub → "GITHUB_REPO_ANALYSIS.yaml"
2. Configure: `repo: owner/repo`
3. Execute
4. Review in **Artifacts** → `github_repo_analysis.json`

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Refresh workflows |
| `Ctrl+Q` | Exit |
| `↑/↓` | Terminal history |

## Troubleshooting

### GUI Won't Start
```bash
# Install PyQt6
pip install PyQt6>=6.4.0

# Verify installation
python -c "from PyQt6 import QtWidgets; print('PyQt6 OK')"
```

### Workflows Not Found
1. Check **Settings** tab → Workflows Directory
2. Ensure `.ai/workflows/` exists
3. Click refresh button

### Cost Tracking Not Updating
1. **Cost Tracking** tab → Click "Refresh"
2. Verify workflows are completing
3. Check execution logs in **Execution** tab

## Development

### Running Tests
```bash
# GUI tests (requires PyQt6)
pytest tests/gui/ -v

# With coverage
pytest tests/gui/ --cov=gui_terminal
```

### Adding New Features

#### New UI Component
1. Create in `src/gui_terminal/ui/`
2. Extend `QtWidgets.QWidget`
3. Use signals for communication
4. Add to main window tabs
5. Write tests in `tests/gui/`

#### New Workflow
1. Add YAML to `.ai/workflows/`
2. Auto-discovered by browser
3. Configure inputs in workflow
4. Test with dry-run

## Contributing

See main project [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT - See [LICENSE](../../LICENSE)

## Support

- **Issues**: https://github.com/DICKY1987/cli_multi_rapid_DEV/issues
- **Documentation**: [GUI_USER_GUIDE.md](GUI_USER_GUIDE.md)
- **CLI Documentation**: [CLAUDE.md](../../CLAUDE.md)
