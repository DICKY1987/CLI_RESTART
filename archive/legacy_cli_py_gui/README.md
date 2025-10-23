This folder contains the legacy GUI prototype(s) that were previously kept under `CLI_PY_GUI/`.

Status: Deprecated/Archived

- Active, supported GUI lives under `src/gui_terminal/`.
- Launch using `python -m gui_terminal.main` or the packaged entry point `cli-orchestrator-gui`.
- The materials here (legacy PTY runner, basic GUI shell, and related docs) are preserved for reference only and are not part of the current build or release pipeline.

If you had local scripts pointing to `CLI_PY_GUI`, update them to use `src/gui_terminal/main.py` and the `ModernMainWindow` implementation.

