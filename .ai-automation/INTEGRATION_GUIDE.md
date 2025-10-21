# AI Automation Framework - Integration Guide

## Quick Start

This framework provides universal prompt-driven automation for AI coding tools (Aider, Open Interpreter, OpenCode, Claude Code, Codex, Gemini) with a consistent interface and Git-based workflow.

### Prerequisites

**Required:**
- Git 2.30+
- PowerShell 5.1+ (Windows)
- At least one AI tool installed (see Tool Installation below)

**Optional:**
- Ollama with DeepSeek model for local AI (`ollama pull deepseek-coder-v2:lite`)
- GitHub CLI (`gh`) for enhanced Git operations

### Tool Installation

```bash
# Aider (Python-based pair programming)
pipx install aider-chat

# Open Interpreter (Python-based code execution)
pipx install open-interpreter

# OpenCode (TUI + one-shot runs)
npm install -g @opencode/cli

# Claude Code CLI
npm install -g @anthropic/claude-code

# Codex CLI (if available)
npm install -g @openai/codex

# Gemini CLI
pipx install gemini-cli

# Ollama (for local DeepSeek)
# Download from https://ollama.ai
ollama pull deepseek-coder-v2:lite
```

## Directory Structure

```
.ai-automation/
├── ToolAdapter.ps1              # Core execution engine
├── README.md                    # Universal prompt guide
├── INTEGRATION_GUIDE.md         # This file
├── config/
│   └── defaults.json            # Configuration settings
├── prompts/
│   └── testing/                 # Testing workflow templates
│       ├── generate-tests.json
│       ├── fix-failing-tests.json
│       └── improve-coverage.json
├── runs/                        # Execution logs (gitignored)
│   └── executions.jsonl         # Append-only execution log
└── scripts/
    ├── run-task.ps1             # User-friendly task runner
    └── validate-prompt.ps1      # Prompt validation tool
```

## Universal Prompt Shape

All tasks follow this standard structure:

```
Task:        <one-sentence objective>
Scope:       <allow-list of files/dirs to modify>
Constraints: <style, APIs, dependency rules, quality bars>
Checks:      <shell commands to prove success>
Artifacts:   <files/paths that must be created or updated>
Commit:      <short imperative commit message>
Context:     <read-only references: docs, configs, standards>
Limits:      <iteration/time/token guards>
Success:     <pass/fail acceptance criteria>
```

## Usage Examples

### Example 1: Run Testing Workflow Template

```powershell
# Generate tests for a module
cd C:\Users\Richard Wilks\CLI_RESTART
.\.ai-automation\scripts\run-task.ps1 `
  -Template testing/generate-tests `
  -Variables @{
    TARGET_MODULE = "src/utils/logger.py"
    TARGET_FILE = "logger"
  }
```

### Example 2: Fix Failing Tests

```powershell
# Repair broken test suite
.\.ai-automation\scripts\run-task.ps1 `
  -Template testing/fix-failing-tests `
  -Variables @{DATE = "2025-10-20"}
```

### Example 3: Improve Test Coverage

```powershell
# Increase coverage to 90%
.\.ai-automation\scripts\run-task.ps1 `
  -Template testing/improve-coverage `
  -Variables @{
    TARGET_COVERAGE = "90"
    TARGET_SCOPE = "src/core"
  }
```

### Example 4: Custom Task with Aider

```json
// custom-refactor.json
{
  "tool": "aider",
  "repo": "C:/Users/Richard Wilks/CLI_RESTART",
  "model": "ollama_chat/deepseek-coder:latest",
  "prompt": "Task: Extract duplicate code into reusable utilities\nScope: src/utils/**; src/helpers/**\nConstraints: Maintain backward compatibility; add type hints; update docstrings\nChecks: pytest -q; ruff check .; mypy src/\nArtifacts: src/utils/common.py\nCommit: refactor: extract common utilities\nSuccess: All tests pass; no new linting errors; type checking passes",
  "args": ["src/utils/parser.py", "src/helpers/formatter.py"],
  "env": {
    "OLLAMA_API_BASE": "http://127.0.0.1:11434"
  },
  "timeoutSec": 600
}
```

```powershell
# Run custom task
.\.ai-automation\scripts\run-task.ps1 -TaskFile custom-refactor.json -OutputJson result.json
```

### Example 5: Direct ToolAdapter Execution

```powershell
# Execute via ToolAdapter directly
Get-Content task.json | .\.ai-automation\ToolAdapter.ps1
```

### Example 6: Claude Code CLI

```json
{
  "tool": "claude",
  "repo": ".",
  "prompt": "Task: Add comprehensive error handling to API client\nScope: src/api/**\nConstraints: Use custom exception classes; add retry logic; maintain API compatibility\nChecks: pytest tests/api/ -v\nArtifacts: src/api/exceptions.py; docs/api/error-handling.md\nCommit: feat(api): add comprehensive error handling\nSuccess: All API tests pass; new exception classes documented",
  "model": "claude-sonnet-4-5",
  "timeoutSec": 900
}
```

### Example 7: Gemini CLI for Documentation

```json
{
  "tool": "gemini",
  "repo": ".",
  "prompt": "Task: Generate comprehensive API documentation\nScope: docs/api/**\nConstraints: Follow Google documentation style; include code examples; generate from docstrings\nArtifacts: docs/api/reference.md; docs/api/quickstart.md\nCommit: docs: generate API reference documentation\nSuccess: Documentation files exist; all public APIs documented",
  "model": "gemini-pro",
  "timeoutSec": 600
}
```

### Example 8: Git Enforcement Workflow

```json
{
  "tool": "git",
  "repo": ".",
  "scope": ["src/logging/**", "tests/logging/**"],
  "checks": ["ruff check .", "pytest -q", "mypy src/"],
  "commit": "refactor(logging): extract handlers and add tests"
}
```

### Example 9: Generic LLM via Ollama

```json
{
  "tool": "llm",
  "repo": ".",
  "prompt": "Task: Outline comprehensive test plan for authentication module\nScope: tests/auth/**\nArtifacts: docs/testing/auth-test-plan.md\nSuccess: Test plan covers all auth flows; includes security test cases",
  "args": ["http://127.0.0.1:11434/api/chat", "deepseek-coder"],
  "timeoutSec": 300
}
```

## Validation

### Validate Task Before Execution

```powershell
# Validate task JSON structure
.\.ai-automation\scripts\validate-prompt.ps1 -TaskFile task.json

# Strict validation (requires all recommended fields)
.\.ai-automation\scripts\validate-prompt.ps1 -TaskFile task.json -Strict
```

### Expected Validation Output

```
✓ Required field present: tool
✓ Recommended field present: repo
✓ Recommended field present: prompt
✓ Recommended field present: timeoutSec
✓ Valid tool: aider
✓ Prompt follows universal shape (found 7/7 sections)

---
✓ Validation passed with no issues!
```

## Result Handling

### Execution Result Structure

```json
{
  "ok": true,
  "tool": "aider",
  "started": "2025-10-20T10:30:00.000Z",
  "finished": "2025-10-20T10:35:23.456Z",
  "duration_ms": 323456,
  "exit_code": 0,
  "stdout": "...",
  "stderr": "...",
  "repo_state": {
    "branch": "main",
    "head_before": "abc123...",
    "head_after": "def456...",
    "dirty_after": false,
    "new_commits": ["def456..."]
  },
  "meta": {
    "command": "aider --model ollama_chat/deepseek-coder:latest ...",
    "cwd": "C:/Users/Richard Wilks/CLI_RESTART"
  }
}
```

### Checking Results

```powershell
# Save result and check exit code
.\.ai-automation\scripts\run-task.ps1 -TaskFile task.json -OutputJson result.json
if ($LASTEXITCODE -eq 0) {
    Write-Host "Task succeeded!"
    $result = Get-Content result.json | ConvertFrom-Json
    Write-Host "New commits: $($result.repo_state.new_commits -join ', ')"
} else {
    Write-Host "Task failed with exit code: $LASTEXITCODE"
}
```

## Execution Logging

All executions are logged to `.ai-automation/runs/executions.jsonl` (JSONL format, append-only):

```jsonl
{"timestamp":"2025-10-20T10:35:23.456Z","tool":"aider","exit_code":0,"duration_ms":323456,"repo":"C:/Users/Richard Wilks/CLI_RESTART","new_commits":["def456..."]}
```

### Analyzing Logs

```powershell
# View recent executions
Get-Content .ai-automation\runs\executions.jsonl -Tail 10

# Parse and filter
Get-Content .ai-automation\runs\executions.jsonl |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Where-Object { $_.exit_code -ne 0 } |
  Select-Object timestamp, tool, exit_code
```

## Configuration

### Customize Defaults

Edit `.ai-automation/config/defaults.json`:

```json
{
  "ollama": {
    "api_base": "http://127.0.0.1:11434",
    "default_model": "deepseek-coder",
    "timeout_sec": 600
  },
  "tools": {
    "aider": {
      "default_model": "ollama_chat/deepseek-coder:latest"
    },
    "claude": {
      "default_model": "claude-sonnet-4-5"
    }
  },
  "execution": {
    "default_timeout_sec": 600,
    "log_runs": true
  }
}
```

## Creating Custom Templates

### Template Structure

```json
{
  "name": "My Custom Workflow",
  "description": "What this workflow does",
  "tool": "aider",
  "repo": ".",
  "model": "ollama_chat/deepseek-coder:latest",
  "prompt": "Task: {TASK_DESCRIPTION}\nScope: {TARGET_FILES}\nConstraints: {CONSTRAINTS}\nChecks: {VALIDATION_COMMANDS}\nArtifacts: {EXPECTED_OUTPUTS}\nCommit: {COMMIT_MESSAGE}\nSuccess: {SUCCESS_CRITERIA}",
  "args": [],
  "env": {
    "OLLAMA_API_BASE": "http://127.0.0.1:11434"
  },
  "timeoutSec": 600,
  "placeholders": {
    "TASK_DESCRIPTION": "What to do",
    "TARGET_FILES": "Files to modify",
    "CONSTRAINTS": "Rules to follow",
    "VALIDATION_COMMANDS": "How to verify",
    "EXPECTED_OUTPUTS": "Files that should be created/modified",
    "COMMIT_MESSAGE": "Git commit message",
    "SUCCESS_CRITERIA": "How to know it worked"
  },
  "usage": "Replace placeholders before execution"
}
```

### Save to Templates Directory

```powershell
# Save custom template
$template | ConvertTo-Json -Depth 4 |
  Set-Content .ai-automation\prompts\custom\my-workflow.json
```

## Troubleshooting

### Common Issues

**Tool Not Found**
```
Error: Unsupported tool 'aider'
```
Solution: Install the tool or check PATH configuration

**Ollama Connection Failed**
```
Error: Cannot connect to http://127.0.0.1:11434
```
Solution: Start Ollama service/application

**Git Checks Failed**
```
Check failed: pytest -q
```
Solution: Fix failing tests before committing; review stdout/stderr in result

**Timeout Exceeded**
```
TIMEOUT 600s
```
Solution: Increase `timeoutSec` in task JSON or split into smaller tasks

**Out of Scope Changes**
```
Staged change outside Scope: src/other/file.py
```
Solution: Expand `scope` array or review why tool modified unexpected files

### Debug Mode

```powershell
# Enable verbose output in ToolAdapter
$VerbosePreference = 'Continue'
.\.ai-automation\ToolAdapter.ps1 -RequestPath task.json -Verbose
```

## Best Practices

1. **Start Small**: Test workflows with `--dry-run` or simple tasks first
2. **Use Templates**: Leverage pre-built templates for common workflows
3. **Validate First**: Always run `validate-prompt.ps1` before execution
4. **Check Results**: Inspect `repo_state.new_commits` and `exit_code`
5. **Review Diffs**: Use `git diff HEAD~1` to review changes before pushing
6. **Scope Tightly**: Keep `scope` narrow to prevent unintended modifications
7. **Enable Checks**: Always include validation commands in `checks`
8. **Log Everything**: Keep execution logs for auditing and debugging
9. **Version Control**: Commit framework files and custom templates to Git
10. **Iterate**: Refine prompts based on execution results

## Integration with CLI_RESTART

This framework integrates with the CLI_RESTART orchestrator project:

### Using with CLI Orchestrator Workflows

```yaml
# .ai/workflows/AI_AUTOMATION.yaml
name: "AI-Powered Code Automation"
steps:
  - id: "1.001"
    name: "Run AI automation task"
    actor: external_script
    with:
      script: ".ai-automation/scripts/run-task.ps1"
      args: ["-Template", "testing/generate-tests", "-Variables", "@{TARGET_MODULE='src/module.py'}"]
    emits: ["artifacts/ai_result.json"]
```

### Adapter Integration

The framework can be integrated as a custom adapter:

```python
# src/cli_multi_rapid/adapters/ai_automation_adapter.py
from .base_adapter import BaseAdapter, AdapterResult
import subprocess
import json

class AIAutomationAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            name="ai_automation",
            adapter_type=AdapterType.AI,
            description="Universal AI tool automation"
        )

    def execute(self, step, context=None, files=None):
        template = step.get("with", {}).get("template")
        variables = step.get("with", {}).get("variables", {})

        # Call run-task.ps1
        result = subprocess.run([
            "powershell", "-File",
            ".ai-automation/scripts/run-task.ps1",
            "-Template", template,
            "-Variables", json.dumps(variables),
            "-OutputJson", "artifacts/ai_result.json"
        ], capture_output=True, text=True)

        return AdapterResult(
            success=result.returncode == 0,
            output=result.stdout,
            artifacts=["artifacts/ai_result.json"]
        )
```

## Next Steps

1. **Explore Templates**: Review existing templates in `prompts/testing/`
2. **Create Custom Workflows**: Build templates for your common tasks
3. **Integrate Tools**: Install and configure additional AI tools
4. **Automate CI/CD**: Use framework in GitHub Actions workflows
5. **Extend Framework**: Add new tools to ToolAdapter.ps1
6. **Share Templates**: Contribute useful templates back to the project

## Resources

- **Universal Prompt Guide**: `.ai-automation/README.md`
- **Configuration Reference**: `.ai-automation/config/defaults.json`
- **Tool Documentation**:
  - Aider: https://aider.chat
  - Open Interpreter: https://docs.openinterpreter.com
  - OpenCode: https://opencode.dev
  - Claude Code: https://claude.ai/code
  - Ollama: https://ollama.ai

## Support

For issues, questions, or contributions:
- Review logs in `.ai-automation/runs/executions.jsonl`
- Check validation with `validate-prompt.ps1`
- Refer to CLI_RESTART documentation in `docs/`
- Submit issues to repository issue tracker
