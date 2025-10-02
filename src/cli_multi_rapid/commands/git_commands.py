"""Git lifecycle CLI commands."""

from __future__ import annotations

import typer
from typing import Optional

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
    dest: Optional[str] = typer.Argument(None, help="Destination path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Clone a git repository."""
    from cli_multi_rapid.adapters.git_ops import GitOpsAdapter

    adapter = GitOpsAdapter()
    result = adapter.execute(
        {"operation": "clone", "url": url, "dest": dest}, dry_run=dry_run
    )

    if result.success:
        typer.secho(f"✓ Cloned {url}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def branch(
    name: str = typer.Argument(..., help="Branch name"),
    create: bool = typer.Option(False, "--create", "-c", help="Create new branch"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
):
    """Create or switch git branches."""
    from cli_multi_rapid.adapters.git_ops import GitOpsAdapter

    adapter = GitOpsAdapter()
    operation = "create_branch" if create else "switch_branch"
    result = adapter.execute(
        {"operation": operation, "branch": name}, dry_run=dry_run
    )

    if result.success:
        action = "Created and switched to" if create else "Switched to"
        typer.secho(f"✓ {action} branch: {name}", fg=typer.colors.GREEN)
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
    body: Optional[str] = typer.Option(None, "--body", "-b", help="PR description"),
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
    branch: Optional[str] = typer.Argument(None, help="Branch to merge (defaults to current PR)"),
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
        typer.secho(f"✓ Merged successfully", fg=typer.colors.GREEN)
    else:
        typer.secho(f"✗ Failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
