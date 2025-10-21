"""State management CLI commands."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from ..state.state_manager import StateManager

app = typer.Typer(help="State persistence and management commands")
console = Console()


@app.command("list")
def list_state(
    pattern: str = typer.Option("*.json", "--pattern", "-p", help="File pattern to match"),
    workflow_id: str | None = typer.Option(None, "--workflow", "-w", help="Filter by workflow ID"),
    session_id: str | None = typer.Option(None, "--session", "-s", help="Filter by session ID"),
):
    """List all state files with metadata."""
    manager = StateManager()
    state_files = manager.list_state_files(
        pattern=pattern, workflow_id=workflow_id, session_id=session_id
    )

    if not state_files:
        console.print("[yellow]No state files found[/yellow]")
        return

    table = Table(title="State Files")
    table.add_column("Path", style="cyan")
    table.add_column("Size", style="magenta")
    table.add_column("Modified", style="green")
    table.add_column("Workflow", style="blue")
    table.add_column("Session", style="yellow")

    for state in state_files:
        size_kb = round(state.size_bytes / 1024, 2)
        modified = state.modified_at.split("T")[0]  # Just the date
        table.add_row(
            state.path,
            f"{size_kb} KB",
            modified,
            state.workflow_id or "-",
            state.session_id or "-",
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(state_files)} files[/dim]")


@app.command("show")
def show_state(
    state_id: str = typer.Argument(..., help="State identifier (filename without .json)"),
):
    """Show contents of a specific state file."""
    manager = StateManager()
    state_data = manager.get_state(state_id)

    if state_data is None:
        console.print(f"[red]State not found: {state_id}[/red]")
        raise typer.Exit(1)

    console.print(json.dumps(state_data, indent=2))


@app.command("clean")
def clean_state(
    older_than: int = typer.Option(30, "--older-than", help="Delete files older than N days"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted"),
):
    """Clean old state files based on retention policy."""
    manager = StateManager()

    console.print(f"[bold blue]Cleaning state files older than {older_than} days[/bold blue]")
    if dry_run:
        console.print("[yellow]DRY RUN - No files will be deleted[/yellow]")

    result = manager.clean_old_state(older_than_days=older_than, dry_run=dry_run)

    console.print("\n[cyan]Cleanup Summary:[/cyan]")
    console.print(f"  Files deleted: {result['deleted_count']}")
    console.print(f"  Files archived: {result['archived_count']}")
    console.print(f"  Space freed: {result['space_freed_mb']} MB")

    if result["deleted_files"]:
        console.print("\n[dim]Deleted files:[/dim]")
        for file in result["deleted_files"][:10]:  # Show first 10
            console.print(f"  - {file}")
        if len(result["deleted_files"]) > 10:
            console.print(f"  ... and {len(result['deleted_files']) - 10} more")

    if not dry_run and result["deleted_count"] > 0:
        console.print("\n[green]✓ Cleanup completed[/green]")


@app.command("usage")
def show_usage():
    """Show disk usage by state files."""
    manager = StateManager()
    usage = manager.get_disk_usage()

    console.print("[bold blue]State Storage Usage[/bold blue]")
    console.print(f"\n  Directory: {usage['state_dir']}")
    console.print(f"  Total files: {usage['total_files']}")
    console.print(f"  Total size: {usage['total_size_mb']} MB")

    # Load policy to show limits
    policy = manager.policy
    console.print("\n[cyan]Retention Policy:[/cyan]")
    console.print(f"  Max age: {policy.max_age_days} days")
    console.print(f"  Max size: {policy.max_size_mb} MB")
    console.print(f"  Archive before delete: {policy.archive_before_delete}")

    # Show usage percentage
    usage_pct = (usage['total_size_mb'] / policy.max_size_mb) * 100 if policy.max_size_mb > 0 else 0
    color = "green" if usage_pct < 70 else "yellow" if usage_pct < 90 else "red"
    console.print(f"\n  Usage: [{color}]{usage_pct:.1f}%[/{color}] of limit")


@app.command("enforce-limit")
def enforce_limit(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted"),
):
    """Enforce size limit by deleting oldest files."""
    manager = StateManager()

    console.print("[bold blue]Enforcing size limit policy[/bold blue]")
    if dry_run:
        console.print("[yellow]DRY RUN - No files will be deleted[/yellow]")

    result = manager.enforce_size_limit(dry_run=dry_run)

    if result["action"] == "none":
        console.print(f"[green]✓ Storage is under limit ({result['current_size_mb']} MB / {result['limit_size_mb']} MB)[/green]")
        return

    console.print("\n[cyan]Enforcement Summary:[/cyan]")
    console.print(f"  Files deleted: {result['deleted_count']}")
    console.print(f"  Space freed: {result['space_freed_mb']} MB")
    console.print(f"  New size: {result['new_size_mb']} MB / {result['limit_size_mb']} MB")

    if result.get("deleted_files"):
        console.print("\n[dim]Deleted files:[/dim]")
        for file in result["deleted_files"][:10]:
            console.print(f"  - {file}")
        if len(result["deleted_files"]) > 10:
            console.print(f"  ... and {len(result['deleted_files']) - 10} more")

    if not dry_run:
        console.print("\n[green]✓ Size limit enforced[/green]")


@app.command("delete")
def delete_state(
    state_id: str = typer.Argument(..., help="State identifier to delete"),
    no_archive: bool = typer.Option(False, "--no-archive", help="Skip archival before deletion"),
):
    """Delete a specific state file."""
    manager = StateManager()

    archive = not no_archive
    success = manager.delete_state(state_id, archive=archive)

    if success:
        action = "archived and deleted" if archive else "deleted"
        console.print(f"[green]✓ State {action}: {state_id}[/green]")
    else:
        console.print(f"[red]✗ Failed to delete state: {state_id}[/red]")
        raise typer.Exit(1)


@app.command("archive")
def archive_state(
    state_id: str = typer.Argument(..., help="State identifier to archive"),
):
    """Archive a state file without deleting it."""
    manager = StateManager()

    state_file = manager.state_dir / f"{state_id}.json"
    if not state_file.exists():
        console.print(f"[red]State not found: {state_id}[/red]")
        raise typer.Exit(1)

    success = manager._archive_file(state_file)

    if success:
        console.print(f"[green]✓ State archived: {state_id}[/green]")
        console.print(f"[dim]Archive location: {manager.policy.archive_path}[/dim]")
    else:
        console.print(f"[red]✗ Failed to archive state: {state_id}[/red]")
        raise typer.Exit(1)
