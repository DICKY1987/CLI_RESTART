#!/usr/bin/env python3
"""
Git lifecycle commands for developer experience.

Wraps common git operations, integrating with git_ops adapter where available.
Supports --dry-run for safe previews and --json via global formatter.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import typer

from ..output import OutputFormatter
from ..adapters.adapter_registry import registry as adapter_registry


repo_app = typer.Typer(name="repo", help="Git repository lifecycle commands")


def _fmt() -> OutputFormatter:
    ctx = typer.get_current_context()
    json_mode = bool((ctx.obj or {}).get("json_mode", False))
    # Reuse console from parent if available
    from rich.console import Console

    return OutputFormatter(json_mode=json_mode, console=Console())


@repo_app.command("init")
def repo_init(path: Path = typer.Argument(Path("."), help="Directory to initialize"), dry_run: bool = typer.Option(False, "--dry-run", help="Preview without changes")):
    """Initialize a git repository in the given path."""
    fmt = _fmt()
    if dry_run:
        raise typer.Exit(fmt.emit({"intent": "git init", "path": str(path)}, exit_code=0))
    try:
        path.mkdir(parents=True, exist_ok=True)
        res = subprocess.run(["git", "init", str(path)], capture_output=True, text=True)
        raise typer.Exit(fmt.emit({"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}, exit_code=res.returncode))
    except Exception as e:
        raise typer.Exit(fmt.error("git init failed", {"exception": str(e)}))


@repo_app.command("clone")
def repo_clone(url: str = typer.Argument(..., help="Repository URL"), dest: Optional[Path] = typer.Option(None, "--dest", help="Destination directory"), depth: Optional[int] = typer.Option(1, "--depth", help="Shallow clone depth"), dry_run: bool = typer.Option(False, "--dry-run", help="Preview without changes")):
    """Clone a git repository."""
    fmt = _fmt()
    if dry_run:
        raise typer.Exit(fmt.emit({"intent": "git clone", "url": url, "dest": str(dest) if dest else None, "depth": depth}, exit_code=0))
    try:
        cmd = ["git", "clone"]
        if depth:
            cmd += ["--depth", str(depth)]
        cmd += [url]
        if dest:
            cmd.append(str(dest))
        res = subprocess.run(cmd, capture_output=True, text=True)
        raise typer.Exit(fmt.emit({"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}, exit_code=res.returncode))
    except Exception as e:
        raise typer.Exit(fmt.error("git clone failed", {"exception": str(e)}))


@repo_app.command("branch")
def repo_branch(name: Optional[str] = typer.Option(None, "--name", help="Branch name"), dry_run: bool = typer.Option(False, "--dry-run", help="Preview without changes")):
    """Create or switch to a branch using git_ops adapter."""
    fmt = _fmt()
    if dry_run:
        raise typer.Exit(fmt.emit({"intent": "create_branch", "name": name}, exit_code=0))
    adapter = adapter_registry.get_adapter("git_ops")
    step = {"actor": "git_ops", "with": {"operation": "create_branch", "name": name}}
    result = adapter.execute(step)
    raise typer.Exit(fmt.emit(result.to_dict() if hasattr(result, "to_dict") else result, exit_code=0 if result.success else 1))


@repo_app.command("commit")
def repo_commit(message: str = typer.Option(..., "-m", "--message", help="Commit message"), add_all: bool = typer.Option(True, "--all/--no-all", help="Add all changes"), dry_run: bool = typer.Option(False, "--dry-run", help="Preview without changes")):
    """Commit changes using git_ops adapter and optional template."""
    fmt = _fmt()
    if dry_run:
        raise typer.Exit(fmt.emit({"intent": "commit", "message": message, "add": ["-A"] if add_all else []}, exit_code=0))
    adapter = adapter_registry.get_adapter("git_ops")
    step = {"actor": "git_ops", "with": {"operation": "commit", "message": message, "add": ["-A"] if add_all else []}}
    result = adapter.execute(step)
    raise typer.Exit(fmt.emit(result.to_dict() if hasattr(result, "to_dict") else result, exit_code=0 if result.success else 1))


@repo_app.command("pr")
def repo_pr(title: str = typer.Option(..., "--title", help="PR title"), body: str = typer.Option("", "--body", help="PR body"), base: str = typer.Option("main", "--base", help="Base branch"), head: Optional[str] = typer.Option(None, "--head", help="Head branch"), real: bool = typer.Option(False, "--real", help="Create real PR via GitHub"), dry_run: bool = typer.Option(False, "--dry-run", help="Preview without changes")):
    """Open a pull request using git_ops adapter. Defaults to mock unless --real is set."""
    fmt = _fmt()
    if dry_run and not real:
        raise typer.Exit(fmt.emit({"intent": "open_pr", "title": title, "base": base, "head": head, "mode": "mock"}, exit_code=0))
    adapter = adapter_registry.get_adapter("git_ops")
    step = {"actor": "git_ops", "with": {"operation": "open_pr", "title": title, "body": body, "base": base, "head": head, "real": real}}
    result = adapter.execute(step)
    raise typer.Exit(fmt.emit(result.to_dict() if hasattr(result, "to_dict") else result, exit_code=0 if result.success else 1))


@repo_app.command("merge")
def repo_merge(target: str = typer.Argument(..., help="Branch to merge into current"), no_ff: bool = typer.Option(True, "--no-ff/--ff", help="No fast-forward"), dry_run: bool = typer.Option(False, "--dry-run", help="Preview without changes")):
    """Merge a branch into current."""
    fmt = _fmt()
    if dry_run:
        raise typer.Exit(fmt.emit({"intent": "merge", "target": target, "no_ff": no_ff}, exit_code=0))
    try:
        args = ["merge"]
        if no_ff:
            args.append("--no-ff")
        args.append(target)
        res = subprocess.run(["git", *args], capture_output=True, text=True)
        raise typer.Exit(fmt.emit({"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}, exit_code=res.returncode))
    except Exception as e:
        raise typer.Exit(fmt.error("git merge failed", {"exception": str(e)}))

