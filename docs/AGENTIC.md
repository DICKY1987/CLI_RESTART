Agentic Integration (Aider + DeepSeek via Ollama)

Overview

- Adds `cli-orchestrator agentic` commands to scaffold a per-repo `.code-intel/` directory and operate a local RAG loop.
- Uses Ollama locally for both chat (DeepSeek) and embeddings.

Prerequisites

- Ollama installed and running at `http://localhost:11434`.
- Models: `ollama pull deepseek-coder` and an embeddings model (e.g. `ollama pull mxbai-embed-large`).
- Optional tooling: `ctags`, `rg`, `pytest`, `ruff`, `black`.

Commands

- `cli-orchestrator agentic init`:
  - Creates `.code-intel/` from template, ensures `.gitignore`, builds initial index.
  - Options: `--path`, `--force`, `--no-build`.

- `cli-orchestrator agentic analyze "<question>"`:
  - Retrieves top-k relevant chunks; prints JSON. With `--answer` (default), asks the model using retrieved context.

- `cli-orchestrator agentic dev --task "<goal>"`:
  - Retrieves context, optionally launches `aider`, then runs validations.
  - Options: `--skip-tests`, `--skip-lint`, `--fix`, `--watch`, `--aider`.

### Aider Quick Start

- This repo includes `.aider.conf.yml` preconfigured for Ollama:
  - `model: openai/deepseek-coder`
  - `openai-api-base: http://localhost:11434/v1`
  - `openai-api-key: ollama`
  - Safe ignore patterns exclude caches, artifacts, and `.code-intel/db`.

- Recommended flow:
  1) `cli-orchestrator agentic init`
  2) `cli-orchestrator agentic dev --task "Your change" --aider --fix`
  3) In aider, iterate on edits; upon exit, tests/lint run automatically.

Template

- Lives at `templates/code-intel-template/` inside this repo.
- Copied to target repos as `.code-intel/`.

Self-Bootstrap

- `python scripts/bootstrap_self_intelligence.py` initializes `.code-intel/` for this orchestrator repo and builds the index.
