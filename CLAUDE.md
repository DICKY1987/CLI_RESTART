# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **CLI Orchestrator** - a deterministic, schema-driven CLI orchestrator that stitches together multiple developer tools and AI agents into predefined, auditable workflows. It prioritizes scripts first, escalates to AI only where judgment is required, and emits machine-readable artifacts with gates and verification at every hop.

The project is multi-faceted, combining:
1. **Core CLI Orchestrator**: Workflow engine with adapter-based architecture
2. **Trading System Integration**: EA (Expert Advisor) system with contract models for algorithmic trading
3. **Agentic Framework**: Symbiotic AI system for automated code modifications
4. **GUI Components**: Python-based terminal GUI with PTY backend
5. **VS Code Extension**: IDE integration for orchestrator workflows
6. **DevOps Infrastructure**: Docker, Kubernetes, monitoring, and CI/CD pipelines

## Requirements

- **Python**: 3.9+ (tested on 3.11-3.12)
- **Platform**: Cross-platform (Linux, macOS, Windows)
- **Node.js**: 16+ (for VS Code extension development)
- **Git**: 2.30+ (for git operations and GitHub integration)

## Core Architecture

### Key Components
- **Workflow Runner**: Executes schema-validated YAML workflows (`src/cli_multi_rapid/workflow_runner.py:1`)
- **Router System**: Routes steps between deterministic tools and AI adapters (`src/cli_multi_rapid/router.py:1`)
- **Adapter Framework**: Unified interface for tools and AI services (`src/cli_multi_rapid/adapters/`)
- **Schema Validation**: JSON Schema validation for workflows and artifacts (`.ai/schemas/`)
- **Cost Tracking**: Token usage and budget enforcement (`src/cli_multi_rapid/cost_tracker.py:1`)
- **Gate System**: Verification and quality gates (`src/cli_multi_rapid/verifier.py:1`)

### Directory Structure
- `src/`: All source code
  - `cli_multi_rapid/`: Core orchestrator implementation
    - `adapters/`: Adapter implementations (AI, code fixers, git ops, etc.)
    - `contracts/`: Data models and contract definitions
  - `contracts/`: Trading contract models (signals, orders, execution)
  - `services/`: Microservices (event bus, security gateway)
  - `trading/mql4/`: MT4 trading system code
- `.ai/`: AI and workflow configuration
  - `workflows/`: YAML workflow definitions (schema-validated)
  - `schemas/`: JSON Schema definitions for validation
  - `bundles/`: Atomic change bundles for code modifications
  - `scripts/`: AI-related scripts and automation
  - `prompts/`: Prompt templates for AI interactions
- `docs/`: All documentation (consolidated)
  - `setup/`: Setup and installation guides
  - `guides/`: User guides and how-tos
  - `architecture/`: Architecture and design docs
  - `integration/`: Integration documentation
  - `specs/`: Specifications (API, CODEX)
- `tests/`: Test suite
  - `trading/`: Trading system tests
- `workflows/`: Workflow templates and phase definitions
- `CLI_PY_GUI/`: Python GUI components
  - `gui_terminal/`: Terminal GUI with PTY backend
- `tools/`: Development tools and utilities
  - `vscode-extension/`: VS Code extension for IDE integration
  - `atomic-workflow-system/`: Atomic workflow execution system
  - `frontend/`: Frontend components
- `scripts/`: All scripts (build, deployment, automation)
  - `validation/`: Validation scripts (pytest, ruff, schema)
  - `TradingOps/`: Trading operations scripts
- `config/`: All configuration files
  - `capabilities/`: Tool capabilities and bindings
  - `catalog/`: Domain catalog and maturity models
  - `policy/`: Compliance and policy rules
- `monitoring/`: Monitoring and observability
  - `dashboards/`: Grafana dashboards
- `deploy/`: Deployment configurations (Kubernetes, Helm)
- `examples/`: Example workflows and contracts
- `artifacts/`: Workflow execution artifacts (runtime, in .gitignore)
- `logs/`: JSONL execution logs (runtime, in .gitignore)
- `cost/`: Token usage tracking (runtime, in .gitignore)
- `archive/`: Historical/deprecated content

## Common Development Commands

### Installation and Setup
```bash
# Install in development mode
pip install -e .

# Install with AI tools support
pip install -e .[ai]

# Install with all development tools
pip install -e .[dev,ai,test]

# Set up development environment (includes pre-commit hooks)
nox -s dev_setup

# Install VS Code extension dependencies
cd tools/vscode-extension && npm ci
```

### CLI Usage
```bash
# Run a workflow with dry-run
cli-orchestrator run .ai/workflows/PY_EDIT_TRIAGE.yaml --files "src/**/*.py" --lane lane/ai-coding/fix-imports --dry-run

# Execute workflow
cli-orchestrator run .ai/workflows/PY_EDIT_TRIAGE.yaml --files "src/**/*.py"

# Verify an artifact against schema
cli-orchestrator verify artifacts/diagnostics.json --schema .ai/schemas/diagnostics.schema.json

# Create PR from artifacts
cli-orchestrator pr create --from artifacts/ --title "Auto triage & fixes" --lane lane/ai-coding/fix-imports

# Generate cost report
cli-orchestrator cost report --last-run

# Run simplified workflow
simplified-run --workflow .ai/workflows/SIMPLE_PY_FIX.yaml

# Check budget/cost limits
cost-check
```

### Alternative Build Systems

#### Make (Cross-platform)
```bash
# See all available commands
make help

# Install development dependencies
make install-dev

# Run full test suite with coverage
make test-all

# Run linting and formatting
make lint format

# Run full CI pipeline locally
make ci
```

#### Task (Go Task)
```bash
# Quick local validation (lint + tests)
task local

# Run CI checks
task ci

# Run Docker Compose smoke test
task e2e

# Create .env from template
task dotenv
```

#### Nox (Python sessions)
```bash
# Run tests across Python versions
nox -s tests

# Run integration tests (cost-controlled)
nox -s integration_tests

# Run linting and formatting
nox -s lint

# Run security checks
nox -s security
```

### Development Tools
```bash
# Run tests
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_workflow_runner.py -v

# Run tests with markers
pytest tests/integration/ -m "not expensive"

# Code quality checks
ruff check src/ tests/ --fix
black src/ tests/
isort src/ tests/ --profile black
mypy src/ --ignore-missing-imports

# Run pre-commit hooks
pre-commit run --all-files

# Security scanning
bandit -r src/ -f json -o bandit-report.json
safety check
```

## Workflow Development

### Creating Workflows
Workflows are defined in `.ai/workflows/*.yaml` and validated against `.ai/schemas/workflow.schema.json`:

```yaml
name: "Python Edit + Triage"
inputs:
  files: ["src/**/*.py"]
  lane: "lane/ai-coding/fix-imports"
policy:
  max_tokens: 120000
  prefer_deterministic: true
steps:
  - id: "1.001"
    name: "VS Code Diagnostic Analysis"
    actor: vscode_diagnostics
    with:
      analyzers: ["python", "ruff", "mypy"]
    emits: ["artifacts/diagnostics.json"]
```

### Available Actors (Adapters)

The Router maintains a registry of 25+ adapters across four categories. All adapters implement the `BaseAdapter` interface and are registered in `Router._initialize_adapters()`.

**Category 1: Deterministic Tools**
- **code_fixers**: Code formatting (black, isort, ruff --fix)
- **vscode_diagnostics**: Linting & analysis (ruff, mypy, pylint, eslint)
- **pytest_runner**: Test execution with coverage reporting
- **git_ops**: Git operations + GitHub API integration (repos, issues, PRs, releases)
- **syntax_validator**: Multi-language syntax validation
- **type_checker**: Static type checking (mypy, pyright)
- **import_resolver**: Python import path resolution
- **security_scanner**: Security vulnerability scanning (bandit, safety)
- **verifier**: Artifact verification & quality gates

**Category 2: AI-Powered Tools**
- **ai_editor**: AI code editing via Aider (Claude, GPT-4, Gemini)
- **ai_analyst**: AI code analysis and insights
- **deepseek**: Local DeepSeek Coder V2 Lite via Ollama (free, private, offline)

**Category 3: Codex Pipeline (Atomic Modifications)**
- **contract_validator**: Validate contracts against schemas
- **bundle_loader**: Load code modification bundles
- **enhanced_bundle_applier**: Apply bundles with verification

**Category 4: Infrastructure**
- **github_integration**: Advanced GitHub repository analysis and automation
- **tool_adapter_bridge**: Generic tool integration bridge
- **cost_estimator**: Token cost estimation before execution
- **certificate_generator**: Generate certificates and attestations

### Router & Adapter Selection

The Router (`src/cli_multi_rapid/router.py`) uses **intelligent routing** based on:

1. **Complexity Analysis** (0.0-1.0 score):
   - File count and total size
   - Operation type (read < format < lint < test < edit < refactor < generate < analyze)
   - Parameter complexity
   - Context dependencies

2. **Adapter Performance Profiles**:
   - Each adapter defines `complexity_threshold` (max complexity it handles well)
   - `preferred_file_types`, `max_files`, `max_file_size` constraints
   - `operation_types` supported (e.g., ["lint", "format"])
   - Historical `success_rate` and `avg_execution_time`

3. **Policy Enforcement**:
   - `prefer_deterministic: true` - Route to scripts/tools when possible
   - `max_tokens` - Budget constraints
   - Adapter availability checks

**Routing Example:**

```yaml
# Simple formatting (complexity ~0.2) → code_fixers (deterministic)
- actor: code_fixers
  with:
    tools: ["black", "isort"]

# Complex refactoring (complexity ~0.8) → ai_editor (AI)
- actor: ai_editor
  with:
    operation: refactor
    prompt: "Extract reusable utilities"
```

The Router can **auto-select** adapters or **validate** explicit actor choices against step complexity.

### Gate Types
- **tests_pass**: Verify tests pass from test report
- **diff_limits**: Check diff size within bounds
- **schema_valid**: Validate artifacts against schemas

## Architecture Principles

1. **Determinism First**: Prefer scripts and static analyzers over AI
2. **Schema-Driven**: All workflows validated by JSON Schema
3. **Idempotent & Safe**: Dry-run and patch previews before execution
4. **Auditable**: Every step emits structured artifacts and logs
5. **Cost-Aware**: Track token spend, enforce budgets
6. **Git Integration**: Lane-based development, signed commits

## Extending the System

### Adding New Adapters

The adapter framework is the core extensibility mechanism. All workflow steps execute through adapters.

**1. Create Adapter Class** (extend `BaseAdapter` in `src/cli_multi_rapid/adapters/base_adapter.py`):

```python
from .base_adapter import BaseAdapter, AdapterType, AdapterResult, AdapterPerformanceProfile

class MyNewAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            name="my_adapter",
            adapter_type=AdapterType.DETERMINISTIC,  # or AdapterType.AI
            description="What this adapter does"
        )

    def get_performance_profile(self) -> AdapterPerformanceProfile:
        """Define performance characteristics for router decisions."""
        return AdapterPerformanceProfile(
            complexity_threshold=0.5,  # 0.0-1.0, max complexity it handles well
            preferred_file_types=[".py", ".ts"],
            max_files=100,
            operation_types=["lint", "format", "test"],
            avg_execution_time=2.0,  # seconds
            success_rate=0.95,  # 0.0-1.0
            cost_efficiency=0,  # tokens per operation (0 for deterministic)
            parallel_capable=True,
            requires_network=False,
            requires_api_key=False
        )

    def is_available(self) -> bool:
        """Check if adapter dependencies are available."""
        return shutil.which("my_tool") is not None

    def validate_step(self, step: Dict[str, Any]) -> bool:
        """Validate step definition compatibility."""
        return self.is_available() and "required_param" in step.get("with", {})

    def estimate_cost(self, step: Dict[str, Any]) -> int:
        """Return estimated tokens (0 for deterministic)."""
        return 0

    def execute(self, step: Dict, context: Optional[Dict] = None, files: Optional[str] = None) -> AdapterResult:
        """Execute the adapter logic."""
        self._log_execution_start(step)

        try:
            params = self._extract_with_params(step)
            emit_paths = self._extract_emit_paths(step)

            # Do work here
            output = self._do_work(params, files)

            result = AdapterResult(
                success=True,
                tokens_used=0,
                artifacts=emit_paths,
                output=output,
                metadata={"key": "value"}
            )

            self._log_execution_complete(result)
            return result

        except Exception as e:
            return AdapterResult(success=False, error=str(e))
```

**2. Register Adapter** in `Router._initialize_adapters()`:

```python
self.registry.register(MyNewAdapter())
```

**3. Add to Workflow Schema** (`.ai/schemas/workflow.schema.json`):

Add `"my_adapter"` to the `actor` enum in the step schema.

**4. Use in Workflows**:

```yaml
steps:
  - id: "1.001"
    name: "Run My Tool"
    actor: my_adapter
    with:
      required_param: "value"
    emits: ["artifacts/my_output.json"]
```

**Key Adapter Conventions:**
- Always return `AdapterResult` (never raise exceptions in `execute()`)
- Use `_extract_with_params()` and `_extract_emit_paths()` helpers
- Log execution start/complete for audit trail
- Implement `is_available()` to check dependencies
- Define accurate `get_performance_profile()` for optimal routing
- Deterministic adapters should have `cost_efficiency=0`

### Adding New Gate Types
1. Add gate logic to `Verifier._check_single_gate()` in `src/cli_multi_rapid/verifier.py`
2. Update workflow schema with new gate type in `.ai/schemas/workflow.schema.json`
3. Create corresponding JSON schema for artifacts in `.ai/schemas/`

## Testing Strategy

- Unit tests for core components (`tests/`)
- Integration tests for workflow execution (`tests/integration/`)
- Schema validation tests for all artifacts
- Mock adapters for isolated testing
- Cost-controlled integration tests (marked with `not expensive`)
- Coverage requirements: ≥85% for CI

## Agentic Drop-In System

The repository includes a symbiotic agentic system for automated code modifications:

### Setup
```bash
# Install hooks (POSIX)
bash scripts/install_hooks.sh

# Install hooks (Windows PowerShell)
./scripts/install_hooks.ps1

# Or manually configure
git config core.hooksPath .githooks
```

### Usage
```bash
# Run symbiotic workflow
python scripts/symbiotic.py "Feature description"

# Inspect results
cat .ai/manifest.json
cat .ai/.ai-audit.jsonl
git diff
```

### Key Components
- **Agentic Router**: Lightweight routing in `agentic/`
- **Validators/Mutators**: Enforced gates with audit logging
- **GitHub Workflow**: `.github/workflows/agentic.yml` runs SAST/SCA
- **VS Code Tasks**: `.vscode/tasks.json` provides IDE integration

## VS Code Integration

### Extension Development
```bash
# Navigate to extension directory
cd tools/vscode-extension

# Install dependencies
npm ci

# Build extension
npm run build

# Package extension (creates .vsix file)
npm run package

# Run tests
npm test

# Lint and format
npm run lint
npm run lint:fix
```

### Available Workflows
- `PY_EDIT_TRIAGE.yaml`: Python code triage and fixes
- `SIMPLE_PY_FIX.yaml`: Quick Python fixes
- `CODE_QUALITY.yaml`: Comprehensive quality checks
- `GITHUB_REPO_ANALYSIS.yaml`: Repository health analysis
- `GITHUB_ISSUE_AUTOMATION.yaml`: Issue triage and labeling
- `GITHUB_PR_REVIEW.yaml`: PR analysis and review
- `GITHUB_RELEASE_MANAGEMENT.yaml`: Release planning

## GitHub Integration

The CLI Orchestrator now includes comprehensive GitHub integration capabilities for repository analysis, issue management, PR automation, and release management.

### GitHub Setup

#### Prerequisites
1. **GitHub Token**: Create a Personal Access Token with required permissions
2. **GitHub CLI** (optional): Install and authenticate for enhanced functionality

#### Environment Configuration
```bash
# Set GitHub token
export GITHUB_TOKEN=your_github_personal_access_token

# Verify GitHub CLI authentication (optional)
gh auth status

# Validate GitHub integration
cli-orchestrator config github --validate
```

#### Required GitHub Token Permissions
- `repo`: Repository access
- `workflow`: GitHub Actions workflow access
- `read:org`: Organization information
- `read:user`: User profile information
- `read:discussion`: Discussion access

### GitHub Workflows

#### Repository Analysis
Comprehensive analysis of repository health, security, and quality:

```bash
# Run repository analysis
cli-orchestrator run .ai/workflows/GITHUB_REPO_ANALYSIS.yaml --repo owner/repo

# Analysis with specific types
cli-orchestrator run .ai/workflows/GITHUB_REPO_ANALYSIS.yaml \
  --repo owner/repo \
  --analysis-types repository,security,code_quality
```

#### Issue Automation
Automated issue triage, categorization, and management:

```bash
# Run issue triage
cli-orchestrator run .ai/workflows/GITHUB_ISSUE_AUTOMATION.yaml \
  --repo owner/repo \
  --state open \
  --create-report-issue true

# Auto-label issues
cli-orchestrator run .ai/workflows/GITHUB_ISSUE_AUTOMATION.yaml \
  --repo owner/repo \
  --auto-label true
```

#### PR Review Automation
Automated pull request analysis and review suggestions:

```bash
# Analyze all open PRs
cli-orchestrator run .ai/workflows/GITHUB_PR_REVIEW.yaml \
  --repo owner/repo \
  --create-summary-issue true

# Analyze specific PR
cli-orchestrator run .ai/workflows/GITHUB_PR_REVIEW.yaml \
  --repo owner/repo \
  --pr-number 123
```

#### Release Management
Automated release planning and management:

```bash
# Generate release plan
cli-orchestrator run .ai/workflows/GITHUB_RELEASE_MANAGEMENT.yaml \
  --repo owner/repo \
  --release-type auto \
  --create-release-issue true

# Create actual release
cli-orchestrator run .ai/workflows/GITHUB_RELEASE_MANAGEMENT.yaml \
  --repo owner/repo \
  --create-release true
```

### GitHub Actions Integration

#### Claude Orchestrator Workflow
Automated execution via GitHub Actions with multiple triggers:

```yaml
# Manual trigger
on:
  workflow_dispatch:
    inputs:
      workflow_name:
        type: choice
        options:
          - 'GITHUB_REPO_ANALYSIS'
          - 'GITHUB_ISSUE_AUTOMATION'
          - 'GITHUB_PR_REVIEW'
          - 'GITHUB_RELEASE_MANAGEMENT'

# Scheduled execution
on:
  schedule:
    - cron: '0 6 * * 0'  # Weekly on Sunday

# Comment triggers
on:
  issue_comment:
    types: [created]
```

#### Comment Commands
Trigger workflows via issue/PR comments:

- `/claude analyze` - Run repository analysis
- `/claude triage` - Run issue automation
- `/claude review` - Run PR review analysis
- `/claude release` - Run release management

#### Enhanced CI/CD
The Claude-enhanced CI workflow provides:

- Automated code quality analysis
- Security vulnerability scanning
- Test coverage reporting with Claude insights
- PR analysis and recommendations
- Cost tracking and budget management

### GitHub Adapter Operations

#### git_ops Enhanced Operations
```yaml
# Repository analysis
- actor: git_ops
  with:
    operation: repo_analysis
    repo: owner/repo

# Issue management
- actor: git_ops
  with:
    operation: create_issue
    title: "Automated Issue"
    body: "Created by CLI Orchestrator"
    labels: ["automation"]

# PR operations
- actor: git_ops
  with:
    operation: pr_review
    pr_number: 123

# Release operations
- actor: git_ops
  with:
    operation: release_info
    tag: "latest"
```

#### github_integration Specialized Analysis
```yaml
# Security analysis
- actor: github_integration
  with:
    analysis_type: security
    repo: owner/repo

# Dependency analysis
- actor: github_integration
  with:
    analysis_type: dependencies
    repo: owner/repo

# Performance analysis
- actor: github_integration
  with:
    analysis_type: performance
    repo: owner/repo
```

### GitHub Schemas

New schemas for GitHub integration artifacts:

- **github_repository_analysis.schema.json**: Repository analysis results
- **github_security_analysis.schema.json**: Security analysis artifacts
- **github_issue_triage.schema.json**: Issue triage results
- **github_pr_review.schema.json**: PR review analysis

### Configuration Management

#### GitHub Configuration
```python
from cli_multi_rapid.config import get_github_config

config = get_github_config()
setup_info = config.setup_configuration()
```

#### Validation and Health Checks
```bash
# Validate GitHub setup
cli-orchestrator config github --validate

# Check token permissions
cli-orchestrator config github --check-permissions

# Test API connectivity
cli-orchestrator config github --test-api
```

### Best Practices

1. **Token Security**: Store GitHub tokens securely in environment variables or secret management
2. **Rate Limiting**: Be mindful of GitHub API rate limits (5000 requests/hour for authenticated users)
3. **Permissions**: Use minimal required permissions for security
4. **Dry Run**: Always test workflows with `--dry-run` first
5. **Cost Monitoring**: Monitor Claude API token usage with cost tracking

### Troubleshooting

#### Common Issues
- **401 Unauthorized**: Check GitHub token validity and permissions
- **403 Forbidden**: Verify token has required repository access
- **404 Not Found**: Ensure repository name is correct and accessible
- **Rate Limit**: Wait for rate limit reset or use authenticated requests

#### Debug Commands
```bash
# Check GitHub configuration
cli-orchestrator config github --debug

# Validate token permissions
cli-orchestrator config github --validate --verbose

# Test specific API endpoints
cli-orchestrator github test-api --repo owner/repo
```

## DeepSeek Local AI Integration

The CLI Orchestrator integrates DeepSeek Coder V2 Lite via Ollama for free, local AI-powered code assistance with complete privacy and no API costs.

### DeepSeek Setup

#### Prerequisites
1. **Ollama**: Install and run Ollama (https://ollama.ai)
2. **DeepSeek Model**: Pull the DeepSeek Coder V2 Lite model
3. **CLI Tools**: Aider and OpenCode (optional, for enhanced functionality)

#### Installation
```bash
# Install Ollama (visit https://ollama.ai for OS-specific instructions)

# Pull DeepSeek Coder V2 Lite model
ollama pull deepseek-coder-v2:lite

# Verify Ollama is running
curl http://localhost:11434/api/tags

# Verify DeepSeek model is available
# Should show deepseek-coder-v2:lite in the model list
```

#### Configuration
```bash
# Aider configuration (already set up)
# Location: ~/.aider.conf.yml
# Model: ollama/deepseek-coder-v2:lite

# Verify setup
powershell -File scripts/verify-deepseek-setup.ps1

# Or use batch script
scripts\verify-deepseek-setup.cmd
```

### Using DeepSeek in Workflows

#### Workflow Example - Code Analysis
```yaml
name: "DeepSeek Code Analysis"
inputs:
  files: ["src/**/*.py"]
steps:
  - id: "1.001"
    name: "AI Code Review with DeepSeek"
    actor: deepseek
    with:
      tool: ollama_direct
      operation: review
      prompt: "Analyze this code for potential bugs, security issues, and improvements"
    emits: ["artifacts/deepseek_review.json"]
```

#### Workflow Example - Code Editing with Aider
```yaml
name: "DeepSeek Code Editing"
inputs:
  files: ["src/module.py"]
steps:
  - id: "1.001"
    name: "Refactor with DeepSeek via Aider"
    actor: deepseek
    with:
      tool: aider
      operation: refactor
      prompt: "Refactor this code to improve readability and maintainability"
      read_only: false
    emits: ["artifacts/deepseek_edit_diff.json"]
```

#### Workflow Example - Read-only Analysis
```yaml
name: "DeepSeek Read-Only Analysis"
inputs:
  files: ["src/**/*.py"]
steps:
  - id: "1.001"
    name: "Code Quality Analysis"
    actor: deepseek
    with:
      tool: aider
      operation: analyze
      prompt: "Analyze code quality and suggest improvements"
      read_only: true
```

### DeepSeek Adapter Operations

#### Supported Tools
- **aider**: Uses Aider CLI with DeepSeek (auto-configured via `.aider.conf.yml`)
- **opencode**: Uses OpenCode CLI with DeepSeek wrapper scripts
- **ollama_direct**: Direct API calls to Ollama for custom operations

#### Supported Operations
- **edit**: Code editing and modifications
- **analyze**: Code analysis and insights
- **review**: Code review and quality assessment
- **generate**: Code generation from requirements
- **refactor**: Code refactoring and restructuring
- **explain**: Code explanation and documentation
- **fix**: Bug fixing and error correction
- **optimize**: Performance optimization
- **document**: Documentation generation
- **test**: Test generation

### CLI Commands

#### Using DeepSeek Wrapper Scripts
```bash
# Interactive TUI mode with DeepSeek
scripts\opencode-deepseek.cmd

# Or from project root with file path
scripts\opencode-deepseek.ps1 "C:\path\to\project"

# Quick command mode
scripts\opencode-deepseek-run.cmd "analyze this codebase"

# PowerShell version
scripts\opencode-deepseek-run.ps1 "review security issues"
```

#### Using Aider with DeepSeek
```bash
# Start aider (automatically uses DeepSeek from config)
aider

# With specific files
aider src/main.py tests/test_main.py

# Read-only analysis
aider --read-only src/module.py
```

#### Direct Workflow Execution
```bash
# Run DeepSeek workflow
cli-orchestrator run .ai/workflows/DEEPSEEK_ANALYSIS.yaml --files "src/**/*.py"

# With dry-run
cli-orchestrator run .ai/workflows/DEEPSEEK_REFACTOR.yaml --files "src/legacy.py" --dry-run
```

### DeepSeek Configuration

#### Environment Variables
```bash
# Ollama endpoint (default: http://localhost:11434)
export OLLAMA_API_BASE=http://localhost:11434

# Or in .env file
OLLAMA_API_BASE=http://localhost:11434
```

#### Aider Configuration
Location: `~/.aider.conf.yml`

```yaml
model: ollama/deepseek-coder-v2:lite
api-base: http://localhost:11434
```

### DeepSeek Workflows

Available in `.ai/workflows/`:

- **DEEPSEEK_CODE_REVIEW.yaml**: Comprehensive code review with DeepSeek
- **DEEPSEEK_REFACTOR.yaml**: Code refactoring with AI assistance
- **DEEPSEEK_ANALYSIS.yaml**: Code quality and security analysis
- **DEEPSEEK_TEST_GEN.yaml**: Test generation with DeepSeek

### Verification and Health Checks

```bash
# Verify DeepSeek setup
powershell -File scripts/verify-deepseek-setup.ps1

# Check Ollama status
curl http://localhost:11434/api/tags

# Test DeepSeek in workflow
cli-orchestrator run .ai/workflows/DEEPSEEK_ANALYSIS.yaml --files "src/test.py" --dry-run

# Check adapter health
cli-orchestrator adapters health deepseek
```

### DeepSeek Benefits

1. **Free Local Inference**: No API costs, runs entirely on your machine
2. **Complete Privacy**: All code stays local, no data sent to external services
3. **Offline Capable**: Works without internet connection once model is downloaded
4. **High Performance**: DeepSeek Coder V2 Lite (15.7B parameters) optimized for code tasks
5. **No Rate Limits**: Use as much as you need without throttling
6. **Integration**: Works seamlessly with Aider, Continue, and OpenCode

### Model Details

**DeepSeek Coder V2 Lite**
- Parameters: 15.7B
- Quantization: Q4_0 (8.9 GB)
- Specialization: Code generation, analysis, and assistance
- Endpoint: `http://localhost:11434`
- Provider: Ollama (local inference)

### Troubleshooting

#### Ollama Not Running
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama service/application if not running
```

#### Model Not Found
```bash
# List installed models
curl http://localhost:11434/api/tags

# Pull DeepSeek model if missing
ollama pull deepseek-coder-v2:lite
```

#### Aider Not Using DeepSeek
```bash
# Check aider configuration
cat ~/.aider.conf.yml

# Verify model setting
# Should show: model: ollama/deepseek-coder-v2:lite
```

#### PowerShell Script Execution
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Documentation Files

- **docs/setup/OPENCODE-DEEPSEEK-SETUP.md**: Detailed setup guide for OpenCode + DeepSeek
- **docs/guides/AI-TOOLS-DEEPSEEK-REFERENCE.md**: Quick reference for all AI tools with DeepSeek
- **docs/setup/SETUP-COMPLETE-SUMMARY.md**: Complete setup verification and examples
- **docs/guides/USE-AI-TOOLS.md**: Quick start guide for AI tools

## Docker and Deployment

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Start with build
docker-compose up -d --build

# Check service health
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Local Stack
```bash
# Start local stack with monitoring
docker-compose -f config/docker-compose.yml up -d

# Run health check
python scripts/healthcheck.py http://localhost:5055/health

# Task runner for e2e testing
task e2e
```

### Kubernetes Deployment
Configuration available in `deploy/k8s/`:
- Helm charts: `deploy/k8s/helm/`
- Network policies: `deploy/k8s/networkpolicy.yaml`
- External secrets: `deploy/k8s/external-secret.yaml`

### Monitoring
- Prometheus configuration: `monitoring/prometheus.yml`
- Grafana dashboards: `monitoring/grafana-dashboards.yml`
- Alerts: `monitoring/alerts.yml`

## Dependencies

- **Core**: typer, pydantic, pydantic-settings, rich, PyYAML, jsonschema, requests, typing-extensions
- **GitHub Integration**: requests (for GitHub API), gh CLI (optional)
- **Optional AI**: aider-chat, anthropic, openai
- **Development**: pytest, pytest-cov, pytest-asyncio, pytest-mock, black, isort, ruff, mypy, pre-commit
- **Security**: bandit, safety
- **Multi-version Testing**: nox

## Environment Configuration

The project uses environment variables for configuration. Copy `.env.template` or `.env.example` to `.env`:

```bash
# Quick setup
cp .env.template .env

# Or use task
task dotenv
```

Key environment variables:
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `ANTHROPIC_API_KEY`: Claude API key (optional)
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `GOOGLE_API_KEY`: Google AI API key (optional)
- `OLLAMA_API_BASE`: Ollama endpoint (default: `http://localhost:11434`)
- `MAX_TOKEN_BUDGET`: Maximum token budget for AI operations (default: 500000)
- `CLI_ORCHESTRATOR_ENV`: Environment mode (development, production, testing)
- `DEFAULT_WORKFLOW_TIMEOUT`: Workflow timeout in minutes (default: 30)
- `DEBUG`: Enable debug logging (true/false)

## Platform-Specific Notes

### Windows
- Use PowerShell for script execution
- MQL4 compilation only supported on Windows
- DeepSeek wrapper scripts available: `scripts\opencode-deepseek.cmd`, `scripts\opencode-deepseek.ps1`
- Set execution policy if needed: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Linux/macOS
- Use bash for script execution
- Aider hooks: `bash scripts/install_hooks.sh`
- All Python and Node.js tooling cross-platform compatible

## Entry Points

The CLI provides three main commands (defined in `pyproject.toml`):

1. **cli-orchestrator** - Main orchestrator CLI
   ```bash
   cli-orchestrator run .ai/workflows/PY_EDIT_TRIAGE.yaml --files "src/**/*.py"
   cli-orchestrator verify artifacts/diagnostics.json --schema .ai/schemas/diagnostics.schema.json
   cli-orchestrator pr create --from artifacts/ --title "Auto fixes"
   cli-orchestrator cost report --last-run
   ```

2. **simplified-run** - Quick workflow execution
   ```bash
   simplified-run --workflow .ai/workflows/SIMPLE_PY_FIX.yaml
   ```

3. **cost-check** - Budget and cost verification
   ```bash
   cost-check
   ```

## Common Issues & Troubleshooting

### Installation Issues
- **Import errors**: Ensure installed with `pip install -e .` from repository root
- **Missing dependencies**: Install dev dependencies with `pip install -e .[dev,ai,test]`
- **Pre-commit hooks failing**: Run `pre-commit install` after installation

### Workflow Execution Issues
- **Schema validation errors**: Ensure workflow YAML matches `.ai/schemas/workflow.schema.json`
- **Adapter not available**: Check adapter dependencies (e.g., `ruff`, `pytest`, `gh` CLI)
- **GitHub API 401**: Verify `GITHUB_TOKEN` is set and has required permissions
- **DeepSeek not working**: Ensure Ollama is running and model is pulled (`ollama pull deepseek-coder-v2:lite`)

### Testing Issues
- **Coverage below threshold**: Minimum 85% required for CI (`pytest --cov-fail-under=85`)
- **Integration tests expensive**: Mark with `@pytest.mark.expensive` and exclude with `-m "not expensive"`
- **Async tests failing**: Ensure `pytest-asyncio` installed

### Build Issues
- **VS Code extension build fails**: Run `npm ci` in `tools/vscode-extension/` first
- **Type checking errors**: Check Python 3.9+ compatibility (use `typing-extensions` for backports)
- **Linting conflicts**: Run `black` before `ruff` (black formats, ruff checks)
