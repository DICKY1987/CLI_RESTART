"""Git lifecycle CLI commands."""

from __future__ import annotations

import typer

app = typer.Typer(help="Git lifecycle operations")


@app.command()
def init(
    path: str = typer.Argument(".", help="Repository path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Initialize a new git repository."""
    from cli_multi_rapid.adapters.git_ops import GitOpsAdapter

    adapter = GitOpsAdapter()
    result = adapter.execute({"operation": "init", "path": path}, dry_run=dry_run)

    if result.success:
        typer.secho(f"✓ Initialized git repository at {path}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def clone(
    url: str = typer.Argument(..., help="Repository URL"),
    dest: str | None = typer.Argument(None, help="Destination path"),
    init_repo: bool = typer.Option(False, "--init", help="Run initialization after clone"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Clone a git repository with optional automatic initialization."""
    from cli_multi_rapid.adapters.git_ops import GitOpsAdapter

    adapter = GitOpsAdapter()
    result = adapter.execute(
        {"operation": "clone", "url": url, "dest": dest}, dry_run=dry_run
    )

    if result.success:
        typer.secho(f"✓ Cloned {url}", fg=typer.colors.GREEN)

        # Run initialization if requested
        if init_repo and not dry_run:
            typer.secho("Running repository initialization...", fg=typer.colors.BLUE)
            try:
                import os
                import subprocess
                import sys

                # Change to cloned directory
                clone_dir = dest if dest else url.split('/')[-1].replace('.git', '')
                original_dir = os.getcwd()
                os.chdir(clone_dir)

                # Run init command
                result = subprocess.run(
                    [sys.executable, "-m", "cli_multi_rapid.main", "init", "init"],
                    capture_output=True,
                    text=True,
                )

                os.chdir(original_dir)

                if result.returncode == 0:
                    typer.secho("✓ Repository initialized successfully", fg=typer.colors.GREEN)
                else:
                    typer.secho("⚠ Initialization completed with warnings", fg=typer.colors.YELLOW)

            except Exception as e:
                typer.secho(f"⚠ Initialization failed: {e}", fg=typer.colors.YELLOW)

    else:
        typer.secho(f"✗ Failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def branch(
    name: str = typer.Argument(..., help="Branch name"),
    create: bool = typer.Option(False, "--create", "-c", help="Create new branch"),
    workflow: str | None = typer.Option(None, "--workflow", help="Associate with workflow ID"),
    template: str | None = typer.Option(None, "--template", help="Use branch template"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Create or switch git branches with workflow integration support."""
    import json
    from datetime import datetime
    from pathlib import Path

    from cli_multi_rapid.adapters.git_ops import GitOpsAdapter

    adapter = GitOpsAdapter()
    operation = "create_branch" if create else "switch_branch"

    # Prepare metadata for workflow integration
    metadata = {
        "workflow_id": workflow,
        "template": template,
        "created_at": datetime.now().isoformat(),
    }

    result = adapter.execute(
        {
            "operation": operation,
            "branch": name,
            "metadata": metadata if (workflow or template) else None,
        },
        dry_run=dry_run,
    )

    if result.success:
        action = "Created and switched to" if create else "Switched to"
        typer.secho(f"✓ {action} branch: {name}", fg=typer.colors.GREEN)

        # Log activity if workflow integration is enabled
        if create and (workflow or template) and not dry_run:
            try:
                log_dir = Path("logs")
                log_dir.mkdir(parents=True, exist_ok=True)

                activity_log = log_dir / "branch_activity.jsonl"
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "branch_created",
                    "branch": name,
                    "workflow_id": workflow,
                    "template": template,
                }

                with open(activity_log, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")

                typer.secho(f"  Logged to: {activity_log}", fg=typer.colors.BLUE, dim=True)

            except Exception as e:
                typer.secho(f"  Warning: Could not log activity: {e}", fg=typer.colors.YELLOW, dim=True)

        # Show workflow/template info
        if workflow:
            typer.secho(f"  Workflow: {workflow}", fg=typer.colors.BLUE, dim=True)
        if template:
            typer.secho(f"  Template: {template}", fg=typer.colors.BLUE, dim=True)

    else:
        typer.secho(f"✗ Failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def commit(
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
    all: bool = typer.Option(False, "--all", "-a", help="Stage all changes"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Create a git commit."""
    from cli_multi_rapid.adapters.git_ops import GitOpsAdapter

    adapter = GitOpsAdapter()
    result = adapter.execute(
        {"operation": "commit", "message": message, "all": all}, dry_run=dry_run
    )

    if result.success:
        typer.secho(f"✓ Created commit: {message[:50]}...", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def pr(
    title: str = typer.Option(..., "--title", "-t", help="PR title"),
    body: str | None = typer.Option(None, "--body", "-b", help="PR description"),
    draft: bool = typer.Option(False, "--draft", help="Create as draft PR"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Create a GitHub pull request."""
    from cli_multi_rapid.adapters.git_ops import GitOpsAdapter

    adapter = GitOpsAdapter()
    result = adapter.execute(
        {
            "operation": "create_pr",
            "title": title,
            "body": body or "",
            "draft": draft,
        },
        dry_run=dry_run,
    )

    if result.success:
        pr_url = result.data.get("pr_url", "")
        typer.secho(f"✓ Created pull request: {pr_url}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def merge(
    branch: str | None = typer.Argument(None, help="Branch to merge (defaults to current PR)"),
    squash: bool = typer.Option(False, "--squash", help="Squash commits"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Merge a branch or pull request."""
    from cli_multi_rapid.adapters.git_ops import GitOpsAdapter

    adapter = GitOpsAdapter()
    result = adapter.execute(
        {"operation": "merge", "branch": branch, "squash": squash}, dry_run=dry_run
    )

    if result.success:
        typer.secho("✓ Merged successfully", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
