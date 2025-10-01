#!/usr/bin/env python3
"""Generate shell completion scripts for cli-orchestrator."""

from __future__ import annotations

from pathlib import Path

import typer

from src.cli_multi_rapid.main import app


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    # Typer exposes click shell completion utilities
    bash = typer.main.get_completion_script(app, "bash")  # type: ignore[attr-defined]
    zsh = typer.main.get_completion_script(app, "zsh")  # type: ignore[attr-defined]
    pwsh = typer.main.get_completion_script(app, "powershell")  # type: ignore[attr-defined]

    write(Path("completions/bash/cli-orchestrator"), bash)
    write(Path("completions/zsh/_cli-orchestrator"), zsh)
    write(Path("completions/powershell/cli-orchestrator.ps1"), pwsh)
    print("Wrote completion scripts under completions/")


if __name__ == "__main__":
    main()

