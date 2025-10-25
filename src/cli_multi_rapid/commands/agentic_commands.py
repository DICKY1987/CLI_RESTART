"""Agentic code-intel commands.

Provides per-repo agentic initialization, retrieval, and dev loop helpers.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(help="Agentic development commands (.code-intel)")
console = Console()


def repo_root(start: Optional[Path] = None) -> Path:
    """Detect repository root from current directory upward."""
    p = (start or Path.cwd()).resolve()
    for _ in range(10):
        if (p / ".git").exists() or (p / "pyproject.toml").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return (start or Path.cwd()).resolve()


def template_dir() -> Path:
    override = os.getenv("AGENTIC_TEMPLATE_DIR")
    if override:
        return Path(override).resolve()
    here = Path(__file__).resolve()
    # Default to package scaffold within src tree to avoid .gitignore conflicts
    return (here.parents[1] / "scaffold" / "code-intel-template").resolve()


def run_cmd(cmd: list[str], cwd: Optional[Path] = None) -> int:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None).returncode


def ensure_gitignore(root: Path) -> None:
    gi = root / ".gitignore"
    lines = []
    if gi.exists():
        lines = gi.read_text(encoding="utf-8").splitlines()
    add = [".code-intel/db/", ".code-intel/cache/"]
    changed = False
    for a in add:
        if a not in lines:
            lines.append(a)
            changed = True
    if changed:
        gi.write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_template(dst_root: Path, force: bool = False) -> Path:
    src = template_dir()
    dst = dst_root / ".code-intel"
    if dst.exists() and not force:
        return dst
    if dst.exists() and force:
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    (dst / "db").mkdir(parents=True, exist_ok=True)
    (dst / "cache").mkdir(parents=True, exist_ok=True)
    return dst


def build_index(dst_root: Path) -> None:
    code_intel = dst_root / ".code-intel"
    ps = code_intel / "build_index.ps1"
    py = code_intel / "build_index.py"
    if platform.system().lower() == "windows" and ps.exists():
        run_cmd(["pwsh", "-NoLogo", "-NoProfile", "-File", str(ps)], cwd=dst_root)
    else:
        run_cmd([sys.executable, str(py)], cwd=dst_root)


def retrieve(dst_root: Path, query: str) -> dict:
    code_intel = dst_root / ".code-intel"
    py = code_intel / "retrieve.py"
    proc = subprocess.run([sys.executable, str(py), "--query", query], cwd=dst_root, capture_output=True, text=True)
    if proc.returncode != 0:
        raise typer.Exit(1)
    try:
        return json.loads(proc.stdout)
    except Exception:
        return {"results": []}


def ask(dst_root: Path, question: str, context_json: Optional[Path] = None) -> str:
    code_intel = dst_root / ".code-intel"
    py = code_intel / "ask_deepseek.py"
    cmd = [sys.executable, str(py), "--question", question]
    if context_json:
        cmd += ["--context_json", str(context_json)]
    proc = subprocess.run(cmd, cwd=dst_root, capture_output=True, text=True)
    if proc.returncode != 0:
        raise typer.Exit(1)
    return proc.stdout.strip()


@app.command("init")
def agentic_init(
    path: Optional[str] = typer.Option(None, "--path", help="Target repository path (defaults to CWD)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing .code-intel"),
    no_build: bool = typer.Option(False, "--no-build", help="Skip initial index build"),
):
    """Bootstrap .code-intel/ in the target repository and build the index."""
    dst = repo_root(Path(path) if path else None)
    console.print(f"[cyan]Target repo:[/cyan] {dst}")
    dst_ci = copy_template(dst, force=force)
    ensure_gitignore(dst)
    console.print(f"[green]OK[/green] Installed template to {dst_ci}")
    if not no_build:
        console.print("[cyan]Building initial index...[/cyan]")
        build_index(dst)
        console.print("[green]OK[/green] Index build complete")


@app.command("analyze")
def agentic_analyze(
    question: str = typer.Argument(..., help="Analysis question"),
    path: Optional[str] = typer.Option(None, "--path", help="Target repository path"),
    answer: bool = typer.Option(True, "--answer/--no-answer", help="Ask model to answer using retrieved context"),
):
    """Retrieve RAG context and optionally ask the model for an answer."""
    dst = repo_root(Path(path) if path else None)
    res = retrieve(dst, question)
    # Print plain JSON to avoid Windows console encoding issues
    print(json.dumps(res, ensure_ascii=True))
    if answer:
        tmp = dst / "artifacts"
        tmp.mkdir(parents=True, exist_ok=True)
        ctx = tmp / "agentic_last_retrieve.json"
        ctx.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
        console.print("[cyan]Asking model...[/cyan]\n")
        out = ask(dst, question, ctx)
        console.print(out)
    else:
        # Provide a brief plain-text summary of top hits for convenience
        try:
            items = res.get("results", [])
            top = items[:5]
            lines = []
            for it in top:
                path = str(it.get("path", ""))
                ch = str(it.get("chunk", ""))
                txt = str(it.get("text", "")).replace("\n", " ")
                if len(txt) > 120:
                    txt = txt[:117] + "..."
                lines.append(f"- {path}:{ch} :: {txt}")
            if lines:
                print("\nSUMMARY:\n" + "\n".join(lines))
        except Exception:
            pass


def tool_exists(name: str) -> bool:
    try:
        return subprocess.run(["where" if platform.system() == "Windows" else "which", name], capture_output=True).returncode == 0
    except Exception:
        return False


def run_validations(dst: Path, fix: bool = False, skip_tests: bool = False, skip_lint: bool = False) -> None:
    if not skip_tests and tool_exists("pytest"):
        console.print("[cyan]Running tests (pytest)...[/cyan]")
        rc = run_cmd(["pytest", "-q"], cwd=dst)
        if rc != 0:
            console.print("[red]Tests failed[/red]")
            raise typer.Exit(rc)
    if not skip_lint and tool_exists("ruff"):
        console.print("[cyan]Running lint (ruff)...[/cyan]")
        rc = run_cmd(["ruff", "check", "."], cwd=dst)
        if rc != 0:
            console.print("[yellow]Lint issues found[/yellow]")
            if fix:
                run_cmd(["ruff", "format", "."], cwd=dst)
    if fix and tool_exists("black"):
        console.print("[cyan]Formatting (black)...[/cyan]")
        run_cmd(["black", "."], cwd=dst)


@app.command("dev")
def agentic_dev(
    task: str = typer.Option(..., "--task", help="Task description"),
    path: Optional[str] = typer.Option(None, "--path", help="Target repository"),
    skip_tests: bool = typer.Option(False, "--skip-tests", help="Skip running pytest"),
    skip_lint: bool = typer.Option(False, "--skip-lint", help="Skip running ruff/black"),
    fix: bool = typer.Option(False, "--fix", help="Apply formatting fixes when possible"),
    watch: bool = typer.Option(False, "--watch", help="Run the incremental watcher"),
    aider: bool = typer.Option(False, "--aider", help="Launch aider for interactive edits"),
):
    """Agentic development loop helper: build index, retrieve context, optional edits, and validations."""
    dst = repo_root(Path(path) if path else None)
    console.print(f"[cyan]Repo:[/cyan] {dst}")

    if not (dst / ".code-intel" / "db" / "docs.jsonl").exists():
        console.print("[cyan]No index found, building...[/cyan]")
        build_index(dst)

    res = retrieve(dst, task)
    tmp = dst / "artifacts"
    tmp.mkdir(parents=True, exist_ok=True)
    ctx = tmp / "agentic_last_retrieve.json"
    ctx.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    console.print("[green]OK[/green] Retrieved context -> artifacts/agentic_last_retrieve.json")

    if aider and tool_exists("aider"):
        console.print("[cyan]Launching aider (CTRL+C to exit)...[/cyan]")
        run_cmd(["aider"], cwd=dst)

    run_validations(dst, fix=fix, skip_tests=skip_tests, skip_lint=skip_lint)

    if watch:
        console.print("[cyan]Starting incremental watcher... (Ctrl+C to stop)[/cyan]")
        py = dst / ".code-intel" / "watch_and_incremental.py"
        subprocess.run([sys.executable, str(py)], cwd=dst)
