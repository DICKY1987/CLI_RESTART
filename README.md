# CLI Orchestrator

A deterministic, schema-driven CLI orchestrator that stitches together multiple developer tools and AI agents into predefined, auditable workflows.

## Quick Start

```bash
# Check where the repository is located
python3 scripts/show_directory_detection.py

# Install dependencies
pip install -e .[dev,ai,test]

# Run a workflow
cli-orchestrator run .ai/workflows/PY_EDIT_TRIAGE.yaml --files "src/**/*.py"
```

## Documentation

- [CLAUDE.md](CLAUDE.md) - Development guide and project overview
- [Directory Detection](docs/directory_detection.md) - Understanding where the repo detects its location
- [Configuration](docs/configuration.md) - Configuration and environment setup
- Combined script utilities: see `scripts/Combined-PowerShell-Scripts.ps1` for discovery/setup helpers. Do not run destructive modules without review.

## Repository Location

The repository is currently located at: `/home/runner/work/CLI_RESTART/CLI_RESTART`

All components detect this location using either:
1. Git root detection (`git rev-parse --show-toplevel`)
2. Current working directory (`Path.cwd()`) as fallback

See [docs/directory_detection.md](docs/directory_detection.md) for complete details.

## Key Components

- **WorkflowRunner**: Executes schema-validated YAML workflows
- **Router System**: Routes between deterministic tools and AI adapters
- **Adapter Framework**: Unified interface for tools and AI services
- **Cost Tracking**: Token usage and budget enforcement
- **Gate System**: Verification and quality gates

## Project Structure

```
├── src/cli_multi_rapid/    # Core orchestrator
├── workflows/              # Workflow templates
├── .ai/workflows/          # AI workflow definitions
├── config/                 # Configuration files
├── scripts/                # Utility scripts
├── tests/                  # Test suite
└── docs/                   # Documentation
```

For complete documentation, see [CLAUDE.md](CLAUDE.md).
