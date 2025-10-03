"""Script registry CLI commands."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Script registry and execution commands")
console = Console()


def load_registry(registry_path: str = "scripts/registry.json") -> Dict[str, Any]:
    """Load script registry from JSON file."""
    path = Path(registry_path)
    if not path.exists():
        console.print(f"[red]Registry not found: {registry_path}[/red]")
        console.print("[yellow]Run 'cli-orchestrator scripts init' to create registry[/yellow]")
        raise typer.Exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Failed to load registry: {e}[/red]")
        raise typer.Exit(1)


def validate_registry_schema(registry_data: Dict[str, Any]) -> bool:
    """Validate registry against schema."""
    schema_path = Path("scripts/registry_schema.json")
    if not schema_path.exists():
        console.print("[yellow]Warning: Schema file not found, skipping validation[/yellow]")
        return True

    try:
        import jsonschema

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        jsonschema.validate(registry_data, schema)
        return True
    except ImportError:
        console.print("[yellow]jsonschema not installed, skipping validation[/yellow]")
        return True
    except Exception as e:
        console.print(f"[red]Schema validation failed: {e}[/red]")
        return False


@app.command("list")
def list_scripts(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags (comma-separated)"),
):
    """List all registered scripts with metadata."""
    registry = load_registry()
    scripts = registry.get("scripts", {})

    if not scripts:
        console.print("[yellow]No scripts registered[/yellow]")
        return

    # Apply filters
    filtered_scripts = {}
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    for name, meta in scripts.items():
        if category and meta.get("category") != category:
            continue

        if tag_list:
            script_tags = meta.get("tags", [])
            if not any(tag in script_tags for tag in tag_list):
                continue

        filtered_scripts[name] = meta

    if not filtered_scripts:
        console.print("[yellow]No scripts match the filters[/yellow]")
        return

    table = Table(title="Registered Scripts")
    table.add_column("Name", style="cyan")
    table.add_column("Purpose", style="white")
    table.add_column("Category", style="blue")
    table.add_column("Platform", style="magenta")
    table.add_column("Tags", style="green")

    for name, meta in filtered_scripts.items():
        table.add_row(
            name,
            meta.get("purpose", "")[:50],
            meta.get("category", "-"),
            meta.get("platform", "all"),
            ", ".join(meta.get("tags", [])),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(filtered_scripts)} scripts[/dim]")


@app.command("info")
def script_info(
    name: str = typer.Argument(..., help="Script name"),
):
    """Show detailed information about a script."""
    registry = load_registry()
    scripts = registry.get("scripts", {})

    if name not in scripts:
        console.print(f"[red]Script not found: {name}[/red]")
        raise typer.Exit(1)

    meta = scripts[name]

    console.print(f"[bold cyan]{name}[/bold cyan]")
    console.print(f"\n[bold]Purpose:[/bold] {meta.get('purpose', 'N/A')}")
    console.print(f"[bold]Category:[/bold] {meta.get('category', 'N/A')}")
    console.print(f"[bold]Platform:[/bold] {meta.get('platform', 'all')}")
    console.print(f"[bold]Path:[/bold] {meta.get('path', 'N/A')}")

    if meta.get("description"):
        console.print(f"\n[bold]Description:[/bold]\n{meta['description']}")

    if meta.get("dependencies"):
        console.print(f"\n[bold]Dependencies:[/bold]")
        for dep in meta["dependencies"]:
            console.print(f"  - {dep}")

    if meta.get("parameters"):
        console.print(f"\n[bold]Parameters:[/bold]")
        for param in meta["parameters"]:
            required = " [red](required)[/red]" if param.get("required") else ""
            default = f" (default: {param.get('default')})" if param.get("default") else ""
            console.print(f"  {param['name']}{required}: {param.get('description', 'N/A')}{default}")

    if meta.get("tags"):
        console.print(f"\n[bold]Tags:[/bold] {', '.join(meta['tags'])}")

    if meta.get("examples"):
        console.print(f"\n[bold]Examples:[/bold]")
        for example in meta["examples"]:
            console.print(f"  {example}")


@app.command("run")
def run_script(
    name: str = typer.Argument(..., help="Script name to execute"),
    args: Optional[List[str]] = typer.Argument(None, help="Script arguments"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show command without executing"),
):
    """Execute a registered script."""
    registry = load_registry()
    scripts = registry.get("scripts", {})

    if name not in scripts:
        console.print(f"[red]Script not found: {name}[/red]")
        raise typer.Exit(1)

    meta = scripts[name]
    script_path = Path(meta.get("path", ""))

    if not script_path.exists():
        console.print(f"[red]Script file not found: {script_path}[/red]")
        raise typer.Exit(1)

    # Determine interpreter
    interpreter = meta.get("interpreter", "auto")
    if interpreter == "auto":
        suffix = script_path.suffix.lower()
        if suffix == ".py":
            interpreter = sys.executable
        elif suffix == ".sh":
            interpreter = "bash"
        elif suffix == ".ps1":
            interpreter = "powershell"
        else:
            interpreter = None

    # Build command
    cmd = []
    if interpreter:
        cmd.append(interpreter)
    cmd.append(str(script_path))
    if args:
        cmd.extend(args)

    console.print(f"[bold blue]Running script:[/bold blue] {name}")
    console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")

    if dry_run:
        console.print("[yellow]DRY RUN - Command not executed[/yellow]")
        return

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.stdout:
            console.print(result.stdout)

        if result.stderr:
            console.print(f"[red]{result.stderr}[/red]", file=sys.stderr)

        if result.returncode == 0:
            console.print(f"\n[green]✓ Script completed successfully[/green]")
        else:
            console.print(f"\n[red]✗ Script failed with exit code {result.returncode}[/red]")
            raise typer.Exit(result.returncode)

    except Exception as e:
        console.print(f"[red]Failed to execute script: {e}[/red]")
        raise typer.Exit(1)


@app.command("validate")
def validate_registry(
    registry_path: str = typer.Option("scripts/registry.json", "--registry", help="Registry file path"),
):
    """Validate script registry against schema."""
    console.print(f"[bold blue]Validating registry:[/bold blue] {registry_path}")

    registry = load_registry(registry_path)

    # Schema validation
    schema_valid = validate_registry_schema(registry)

    # Additional checks
    issues = []
    scripts = registry.get("scripts", {})

    for name, meta in scripts.items():
        # Check if script file exists
        script_path = Path(meta.get("path", ""))
        if not script_path.exists():
            issues.append(f"Script file not found for '{name}': {script_path}")

        # Check required fields
        required_fields = ["purpose", "path"]
        for field in required_fields:
            if not meta.get(field):
                issues.append(f"Missing required field '{field}' for script '{name}'")

    # Report results
    if schema_valid and not issues:
        console.print("[green]✓ Registry is valid[/green]")
    else:
        if not schema_valid:
            console.print("[red]✗ Schema validation failed[/red]")

        if issues:
            console.print(f"\n[red]Found {len(issues)} issue(s):[/red]")
            for issue in issues:
                console.print(f"  - {issue}")

        raise typer.Exit(1)


@app.command("init")
def init_registry(
    force: bool = typer.Option(False, "--force", help="Overwrite existing registry"),
):
    """Initialize a new script registry."""
    registry_path = Path("scripts/registry.json")

    if registry_path.exists() and not force:
        console.print(f"[yellow]Registry already exists: {registry_path}[/yellow]")
        console.print("[dim]Use --force to overwrite[/dim]")
        raise typer.Exit(1)

    # Create basic registry structure
    registry = {
        "version": "1.0.0",
        "description": "CLI Orchestrator script registry",
        "scripts": {},
    }

    registry_path.parent.mkdir(parents=True, exist_ok=True)

    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    console.print(f"[green]✓ Registry initialized: {registry_path}[/green]")


@app.command("add")
def add_script(
    name: str = typer.Argument(..., help="Script name"),
    path: str = typer.Argument(..., help="Script file path"),
    purpose: str = typer.Option(..., "--purpose", help="Script purpose"),
    category: Optional[str] = typer.Option(None, "--category", help="Script category"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Tags (comma-separated)"),
):
    """Add a script to the registry."""
    registry_path = Path("scripts/registry.json")
    registry = load_registry()

    if name in registry.get("scripts", {}):
        console.print(f"[yellow]Script '{name}' already exists in registry[/yellow]")
        raise typer.Exit(1)

    script_path = Path(path)
    if not script_path.exists():
        console.print(f"[yellow]Warning: Script file not found: {path}[/yellow]")

    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    registry["scripts"][name] = {
        "purpose": purpose,
        "path": path,
        "category": category or "general",
        "tags": tag_list,
        "platform": "all",
        "dependencies": [],
        "parameters": [],
    }

    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    console.print(f"[green]✓ Script added to registry: {name}[/green]")


@app.command("remove")
def remove_script(
    name: str = typer.Argument(..., help="Script name to remove"),
):
    """Remove a script from the registry."""
    registry_path = Path("scripts/registry.json")
    registry = load_registry()

    if name not in registry.get("scripts", {}):
        console.print(f"[red]Script not found: {name}[/red]")
        raise typer.Exit(1)

    del registry["scripts"][name]

    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    console.print(f"[green]✓ Script removed from registry: {name}[/green]")
