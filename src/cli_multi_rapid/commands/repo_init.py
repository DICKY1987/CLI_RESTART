"""Repository initialization command."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Repository initialization commands")
console = Console()


def detect_platform() -> str:
    """Detect current platform."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    else:
        return "linux"


def check_command_exists(command: str) -> bool:
    """Check if a command is available."""
    try:
        result = subprocess.run(
            ["where" if platform.system() == "Windows" else "which", command],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def validate_required_tools() -> List[Tuple[str, bool, str]]:
    """Validate required tools are installed.

    Returns:
        List of (tool_name, is_available, version_or_error)
    """
    tools = []

    # Git
    git_ok = check_command_exists("git")
    git_version = ""
    if git_ok:
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, check=False
            )
            git_version = result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            git_version = "error"
    tools.append(("git", git_ok, git_version))

    # Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    tools.append(("python", True, python_version))

    # GitHub CLI (optional)
    gh_ok = check_command_exists("gh")
    gh_version = ""
    if gh_ok:
        try:
            result = subprocess.run(
                ["gh", "--version"], capture_output=True, text=True, check=False
            )
            gh_version = result.stdout.split("\n")[0] if result.returncode == 0 else "unknown"
        except Exception:
            gh_version = "error"
    tools.append(("gh", gh_ok, gh_version))

    # Docker (optional)
    docker_ok = check_command_exists("docker")
    docker_version = ""
    if docker_ok:
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, check=False
            )
            docker_version = result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            docker_version = "error"
    tools.append(("docker", docker_ok, docker_version))

    return tools


def create_required_directories() -> List[str]:
    """Create required directories for CLI orchestrator.

    Returns:
        List of created directory paths
    """
    required_dirs = [
        "artifacts",
        "artifacts/patches",
        "artifacts/reports",
        "logs",
        "state",
        "state/coordination",
        "state/archive",
        "cost",
    ]

    created = []
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(dir_path)

    return created


# def install_python_dependencies(dev: bool = False) -> bool:
    """Install Python dependencies from pyproject.toml.

    Args:
        dev: Include development dependencies

    Returns:
        True if successful
    """
    try:
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        if not in_venv:
            console.print("[yellow]Warning: Not in a virtual environment[/yellow]")
            console.print("[dim]Consider creating one with: python -m venv venv[/dim]")

        # Install package in editable mode
        cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
        if dev:
            cmd.append("[dev,ai,test]")

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode == 0

    except Exception:
        return False


def run_setup_script(platform_name: str) -> bool:
    """Run platform-specific setup script.

    Args:
        platform_name: Platform identifier (windows/linux/macos)

    Returns:
        True if successful
    """
    setup_script = Path("scripts/cross_platform_setup.sh")

    if not setup_script.exists():
        console.print(f"[yellow]Setup script not found: {setup_script}[/yellow]")
        return False

    try:
        if platform_name == "windows":
            # On Windows, run via bash (Git Bash, WSL, etc.)
            cmd = ["bash", str(setup_script)]
        else:
            cmd = ["bash", str(setup_script)]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[dim]{result.stderr}[/dim]")

        return result.returncode == 0

    except Exception as e:
        console.print(f"[yellow]Could not run setup script: {e}[/yellow]")
        return False


@app.command()
def init(
    skip_deps: bool = typer.Option(True, "--skip-deps", help="Skip Python dependency installation"),
    skip_tools: bool = typer.Option(False, "--skip-tools", help="Skip tool validation"),
    skip_setup: bool = typer.Option(False, "--skip-setup", help="Skip setup script execution"),
    dev: bool = typer.Option(False, "--dev", help="Install development dependencies"),
):
    """Initialize CLI orchestrator repository with one command.

    This command:
    - Detects the platform (Windows/Linux/macOS)
    - Validates required tools (git, python, gh cli, docker)
    - Creates required directories (artifacts/, logs/, state/)
    - Installs Python dependencies from pyproject.toml
    - Runs platform-specific setup script
    """
    console.print("[bold blue]CLI Orchestrator Initialization[/bold blue]\n")

    # Detect platform
    platform_name = detect_platform()
    console.print(f"[cyan]Platform detected:[/cyan] {platform_name}")

    # Validate tools
    if not skip_tools:
        console.print("\n[cyan]Validating required tools...[/cyan]")
        tools = validate_required_tools()

        from rich.table import Table

        table = Table()
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Version/Info", style="dim")

        critical_missing = []
        for tool_name, is_available, version_info in tools:
            status = "✓" if is_available else "✗"
            color = "green" if is_available else "red"

            table.add_row(tool_name, f"[{color}]{status}[/{color}]", version_info)

            # Git is critical
            if tool_name == "git" and not is_available:
                critical_missing.append(tool_name)

        console.print(table)

        if critical_missing:
            console.print(f"\n[red]Critical tools missing: {', '.join(critical_missing)}[/red]")
            console.print("[yellow]Please install missing tools and try again[/yellow]")
            raise typer.Exit(1)

    # Create directories
    console.print("\n[cyan]Creating required directories...[/cyan]")
    created_dirs = create_required_directories()

    if created_dirs:
        for dir_path in created_dirs:
            console.print(f"  [green]✓[/green] Created: {dir_path}")
    else:
        console.print("  [dim]All directories already exist[/dim]")

    # Install dependencies
    if not skip_deps:
        console.print("\n[cyan]Installing Python dependencies...[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing packages...", total=None)

#             deps_ok = install_python_dependencies(dev=dev)
            progress.update(task, completed=True)

        if deps_ok:
            console.print("[green]✓ Dependencies installed successfully[/green]")
        else:
            console.print("[yellow]⚠ Dependency installation had issues[/yellow]")
            console.print("[dim]You may need to install manually: pip install -e .[/dim]")

    # Run setup script
    if not skip_setup:
        console.print("\n[cyan]Running platform setup script...[/cyan]")
        setup_ok = run_setup_script(platform_name)

        if setup_ok:
            console.print("[green]✓ Setup script completed[/green]")
        else:
            console.print("[yellow]⚠ Setup script had issues (optional)[/yellow]")

    # Summary
    console.print("\n[bold green]✓ Initialization complete![/bold green]")
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print("  1. Verify installation: [bold]cli-orchestrator --help[/bold]")
    console.print("  2. Run tool check: [bold]cli-orchestrator tools doctor[/bold]")
    console.print("  3. View available workflows: [bold]ls .ai/workflows/[/bold]")
    console.print("  4. Run a workflow: [bold]cli-orchestrator run .ai/workflows/[workflow].yaml[/bold]")


@app.command("doctor")
def init_doctor():
    """Run diagnostic checks on CLI orchestrator installation."""
    console.print("[bold blue]CLI Orchestrator Diagnostics[/bold blue]\n")

    issues = []

    # Check directories
    console.print("[cyan]Checking required directories...[/cyan]")
    required_dirs = ["artifacts", "logs", "state", "cost", ".ai/workflows"]

    for dir_path in required_dirs:
        path = Path(dir_path)
        exists = path.exists() and path.is_dir()
        status = "[green]✓[/green]" if exists else "[red]✗[/red]"
        console.print(f"  {status} {dir_path}")

        if not exists:
            issues.append(f"Missing directory: {dir_path}")

    # Check key files
    console.print("\n[cyan]Checking key files...[/cyan]")
    key_files = [
        "pyproject.toml",
        "src/cli_multi_rapid/main.py",
        "scripts/cross_platform_setup.sh",
    ]

    for file_path in key_files:
        path = Path(file_path)
        exists = path.exists() and path.is_file()
        status = "[green]✓[/green]" if exists else "[red]✗[/red]"
        console.print(f"  {status} {file_path}")

        if not exists:
            issues.append(f"Missing file: {file_path}")

    # Check tools
    console.print("\n[cyan]Checking tools...[/cyan]")
    tools = validate_required_tools()

    for tool_name, is_available, version_info in tools:
        status = "[green]✓[/green]" if is_available else "[yellow]⚠[/yellow]"
        console.print(f"  {status} {tool_name}: {version_info}")

    # Summary
    if issues:
        console.print(f"\n[yellow]Found {len(issues)} issue(s):[/yellow]")
        for issue in issues:
            console.print(f"  - {issue}")
        console.print("\n[cyan]Run 'cli-orchestrator init' to fix issues[/cyan]")
        raise typer.Exit(1)
    else:
        console.print("\n[bold green]✓ All checks passed![/bold green]")

