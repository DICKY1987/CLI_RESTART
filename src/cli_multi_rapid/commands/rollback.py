"""Rollback and undo commands for destructive operations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

app = typer.Typer(help="Rollback and undo operations")


@app.command()
def list(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of snapshots to show"),
):
    """List available rollback snapshots."""
    from cli_multi_rapid.adapters.backup_manager import BackupManager

    manager = BackupManager()
    snapshots = manager.list_snapshots(limit=limit)

    if not snapshots:
        typer.secho("No snapshots available", fg=typer.colors.YELLOW)
        return

    typer.secho("\nAvailable Snapshots:", fg=typer.colors.CYAN, bold=True)
    for snapshot in snapshots:
        typer.echo(
            f"  {snapshot['id']} - {snapshot['timestamp']} - {snapshot.get('description', 'N/A')}"
        )


@app.command()
def restore(
    snapshot_id: str = typer.Argument(..., help="Snapshot ID to restore"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Restore from a snapshot."""
    from cli_multi_rapid.adapters.backup_manager import BackupManager

    manager = BackupManager()

    # Validate snapshot exists
    snapshot = manager.get_snapshot(snapshot_id)
    if not snapshot:
        typer.secho(f"Snapshot not found: {snapshot_id}", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Show snapshot info
    typer.secho(f"\nSnapshot: {snapshot_id}", fg=typer.colors.CYAN)
    typer.echo(f"  Timestamp: {snapshot['timestamp']}")
    typer.echo(f"  Description: {snapshot.get('description', 'N/A')}")
    typer.echo(f"  Files: {snapshot.get('file_count', 'unknown')}")

    # Confirm unless forced
    if not force and not dry_run:
        confirm = typer.confirm("\nRestore from this snapshot?")
        if not confirm:
            typer.secho("Cancelled", fg=typer.colors.YELLOW)
            raise typer.Exit(0)

    # Create backup of current state first
    if not dry_run:
        typer.secho("\nCreating backup of current state...", fg=typer.colors.YELLOW)
        current_backup = manager.create_snapshot(f"pre-restore-{snapshot_id}")
        typer.secho(f"✓ Current state backed up: {current_backup}", fg=typer.colors.GREEN)

    # Restore
    if dry_run:
        typer.secho("\n[DRY RUN] Would restore snapshot", fg=typer.colors.YELLOW)
        typer.echo(f"  Snapshot: {snapshot_id}")
        typer.echo(f"  Files to restore: {snapshot.get('file_count', 'unknown')}")
    else:
        typer.secho("\nRestoring snapshot...", fg=typer.colors.YELLOW)
        try:
            result = manager.restore_snapshot(snapshot_id)
            if result.success:
                typer.secho(f"✓ Restored from snapshot: {snapshot_id}", fg=typer.colors.GREEN)
                typer.secho(f"  Files restored: {result.data.get('restored_count', 0)}", fg=typer.colors.GREEN)
            else:
                typer.secho(f"✗ Restore failed: {result.error}", fg=typer.colors.RED)
                raise typer.Exit(1)
        except Exception as e:
            typer.secho(f"✗ Restore failed: {e}", fg=typer.colors.RED)
            raise typer.Exit(1)


@app.command()
def undo(
    steps: int = typer.Option(1, "--steps", "-n", help="Number of steps to undo"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Undo last N destructive operations."""
    from cli_multi_rapid.adapters.backup_manager import BackupManager

    manager = BackupManager()
    snapshots = manager.list_snapshots(limit=steps)

    if not snapshots:
        typer.secho("No operations to undo", fg=typer.colors.YELLOW)
        return

    if dry_run:
        typer.secho(f"\n[DRY RUN] Would undo {steps} operation(s)", fg=typer.colors.YELLOW)
        for snapshot in snapshots[:steps]:
            typer.echo(f"  - {snapshot['id']}: {snapshot.get('description', 'N/A')}")
    else:
        latest = snapshots[0]
        typer.secho(f"\nUndoing: {latest.get('description', latest['id'])}", fg=typer.colors.YELLOW)
        result = manager.restore_snapshot(latest['id'])

        if result.success:
            typer.secho(f"✓ Undo successful", fg=typer.colors.GREEN)
        else:
            typer.secho(f"✗ Undo failed: {result.error}", fg=typer.colors.RED)
            raise typer.Exit(1)


@app.command()
def clean(
    days: int = typer.Option(30, "--days", help="Delete snapshots older than N days"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Clean up old snapshots."""
    from cli_multi_rapid.adapters.backup_manager import BackupManager

    manager = BackupManager()
    old_snapshots = manager.find_old_snapshots(days=days)

    if not old_snapshots:
        typer.secho(f"No snapshots older than {days} days", fg=typer.colors.GREEN)
        return

    typer.secho(f"\nSnapshots older than {days} days:", fg=typer.colors.YELLOW)
    for snapshot in old_snapshots:
        typer.echo(f"  - {snapshot['id']} ({snapshot['timestamp']})")

    if dry_run:
        typer.secho(f"\n[DRY RUN] Would delete {len(old_snapshots)} snapshot(s)", fg=typer.colors.YELLOW)
    else:
        confirm = typer.confirm(f"\nDelete {len(old_snapshots)} snapshot(s)?")
        if confirm:
            deleted = manager.delete_snapshots(old_snapshots)
            typer.secho(f"✓ Deleted {deleted} snapshot(s)", fg=typer.colors.GREEN)
        else:
            typer.secho("Cancelled", fg=typer.colors.YELLOW)
