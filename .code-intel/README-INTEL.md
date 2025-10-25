Agentic Code Intelligence Template

Overview

- This directory (.code-intel/) provides per-repo code awareness for an agentic dev loop.
- Scripts build an embeddings index of your codebase and retrieve relevant context for queries/tasks.
- Default models assume Ollama running locally with DeepSeek for chat and an embeddings model (e.g., mxbai-embed-large).

Layout

- config.json: Model and retrieval settings.
- ignore_globs.txt: Paths and patterns to exclude from indexing.
- chunk_rules.yaml: Chunking and ranking configuration.
- db/docs.jsonl: Generated embeddings index (JSONL).
- cache/tags: Optional ctags symbol index.
- build_index.(ps1|py): Build or rebuild the index.
- retrieve.(ps1|py): Retrieve top-k chunks for a query.
- ask_deepseek.(ps1|py): Ask the LLM with retrieved context.
- watch_and_incremental.(ps1|py): Watch filesystem and incrementally update index.

Quick Start

1) Ensure Ollama is running and models are available:
   - ollama pull deepseek-coder
   - ollama pull mxbai-embed-large

2) Build the index from repo root:
   - PowerShell: .\.code-intel\build_index.ps1
   - Python:    python .\.code-intel\build_index.py

3) Query with retrieval:
   - PowerShell: .\.code-intel\retrieve.ps1 -Query "How is routing implemented?"
   - Python:    python .\.code-intel\retrieve.py --query "How is routing implemented?"

4) Ask the model with context:
   - PowerShell: .\.code-intel\ask_deepseek.ps1 -Question "Explain router selection"
   - Python:    python .\.code-intel\ask_deepseek.py --question "Explain router selection"

Notes

- Do not commit .code-intel/db/ or .code-intel/cache/.
- Tune config.json and chunk_rules.yaml per project.
- Large repos: consider narrowing include_ext and boosting key paths.

