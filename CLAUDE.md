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

## Core Architecture

### Key Components
- **Workflow Runner**: Executes schema-validated YAML workflows (`src/cli_multi_rapid/workflow_runner.py:1`)
- **Router System**: Routes steps between deterministic tools and AI adapters (`src/cli_multi_rapid/router.py:1`)
- **Adapter Framework**: Unified interface for tools and AI services (`src/cli_multi_rapid/adapters/`)
- **Schema Validation**: JSON Schema validation for workflows and artifacts (`.ai/schemas/`)
- **Cost Tracking**: Token usage and budget enforcement (`src/cli_multi_rapid/cost_tracker.py:1`)
- **Gate System**: Verification and quality gates (`src/cli_multi_rapid/verifier.py:1`)

### Directory Structure
- `src/cli_multi_rapid/`: Core orchestrator implementation
  - `adapters/`: Adapter implementations (AI, code fixers, git ops, etc.)
  - `contracts/`: Data models and contract definitions
- `src/eafix/`: EA (Expert Advisor) trading system integration
  - `apps/cli/`: CLI commands for trading operations
  - `system/`: Health checking and system monitoring
- `src/contracts/`: Trading contract models (signals, orders, execution)
- `.ai/`: AI and workflow configuration
  - `workflows/`: YAML workflow definitions (schema-validated)
  - `schemas/`: JSON Schema definitions for validation
  - `bundles/`: Atomic change bundles for code modifications
  - `scripts/`: AI-related scripts and automation
  - `prompts/`: Prompt templates for AI interactions
- `artifacts/`: Workflow execution artifacts (patches, reports)
- `logs/`: JSONL execution logs and telemetry
- `cost/`: Token usage tracking and budget reports
- `workflows/`: Workflow templates and phase definitions
- `CLI_PY_GUI/`: Python GUI components
  - `gui_terminal/`: Terminal GUI with PTY backend
- `vscode-extension/`: VS Code extension for IDE integration
- `scripts/`: Build, deployment, and automation scripts
- `config/`: Configuration files (pipelines, tools, policies)

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
cd vscode-extension && npm ci
```

### CLI Usage
```bash
# Check where the repository thinks it's located
python3 scripts/show_directory_detection.py

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

**Note**: Always run commands from the repository root directory. See [Directory Detection](docs/directory_detection.md) for details.

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

### Available Actors
Core adapters available in `src/cli_multi_rapid/adapters/`:

- **vscode_diagnostics**: Run diagnostic analysis (ruff, mypy, etc.)
- **code_fixers**: Apply deterministic fixes (black, isort, ruff --fix)
- **ai_editor**: AI-powered code editing (aider, claude, gemini)
- **ai_analyst**: AI-powered code analysis and insights
- **pytest_runner**: Run tests with coverage reporting
- **verifier**: Check gates and validate artifacts
- **git_ops**: Enhanced git operations with GitHub API integration (repos, issues, PRs, releases)
- **github_integration**: Specialized GitHub repository analysis, issue triage, and automation
- **security_scanner**: Security vulnerability scanning
- **syntax_validator**: Syntax validation for multiple languages
- **type_checker**: Static type checking
- **import_resolver**: Import path resolution and fixing
- **contract_validator**: Validate contracts against schemas
- **bundle_loader**: Load and apply code modification bundles
- **cost_estimator**: Estimate token costs before execution
- **backup_manager**: Create and restore backups
- **state_capture**: Capture repository state for rollback

### Gate Types
- **tests_pass**: Verify tests pass from test report
- **diff_limits**: Check diff size within bounds
- **schema_valid**: Validate artifacts against schemas

## Architecture Principles

1. **Determinism First**: Prefer scripts and static analyzers over AI
2. **Schema-Driven**: All workflows validated by JSON Schema
3. **Idempotent & Safe**: Dry-run, patch previews, rollback support
4. **Auditable**: Every step emits structured artifacts and logs
5. **Cost-Aware**: Track token spend, enforce budgets
6. **Git Integration**: Lane-based development, signed commits

## Extending the System

### Adding New Adapters
1. Extend `BaseAdapter` in `src/cli_multi_rapid/adapters/base_adapter.py`
2. Implement `execute()` method returning `AdapterResult`
3. Register in `Router._initialize_adapters()`
4. Add actor to workflow schema enum

### Adding New Gate Types
1. Add gate logic to `Verifier._check_single_gate()`
2. Update workflow schema with new gate type
3. Create corresponding JSON schema for artifacts

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
cd vscode-extension

# Install dependencies
npm ci

# Build extension
npm run build

# Package extension
npm run package

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
- Cost and budget limits
- Service endpoints and ports
