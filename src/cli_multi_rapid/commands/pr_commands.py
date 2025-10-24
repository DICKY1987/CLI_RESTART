#!/usr/bin/env python3
"""
PR Commands - CLI commands for pull request management

Provides commands for creating and managing pull requests from workflow artifacts.
Part of Phase 3 CLI modularization.
"""

import typer
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Pull request creation and management commands")
console = Console()


@app.command("create")
def create_pr(
    title: str = typer.Option(..., "--title", "-t", help="PR title"),
    artifact_dir: Path = typer.Option(
        "artifacts",
        "--from",
        "-f",
        help="Directory containing artifacts to include"
    ),
    lane: Optional[str] = typer.Option(
        None,
        "--lane",
        "-l",
        help="Git workflow lane"
    ),
    body: Optional[str] = typer.Option(
        None,
        "--body",
        "-b",
        help="PR body/description"
    ),
    draft: bool = typer.Option(
        False,
        "--draft",
        help="Create as draft PR"
    ),
    labels: Optional[List[str]] = typer.Option(
        None,
        "--label",
        help="Labels to add to PR (can be used multiple times)"
    ),
    reviewers: Optional[List[str]] = typer.Option(
        None,
        "--reviewer",
        help="Reviewers to add (can be used multiple times)"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview PR without creating it"
    ),
):
    """
    Create a pull request from workflow artifacts.

    Examples:
        cli-orchestrator pr create --title "Fix imports" --from artifacts/
        cli-orchestrator pr create -t "Auto triage & fixes" --lane lane/ai-coding/fix-imports
        cli-orchestrator pr create -t "Updates" --draft --label automation
    """
    console.print(f"[bold]Creating pull request:[/bold] {title}")

    if lane:
        console.print(f"[dim]Lane:[/dim] {lane}")

    if not artifact_dir.exists():
        console.print(f"[yellow]Warning: Artifact directory not found: {artifact_dir}[/yellow]")

    # Import git ops adapter
    try:
        from ..adapters.git_ops import GitOpsAdapter

        git_ops = GitOpsAdapter()

        # Build PR body
        if body is None:
            # Auto-generate body from artifacts
            body = _generate_pr_body_from_artifacts(artifact_dir)

        # Add metadata footer
        body += "\n\n---\n\n"
        body += "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\n"
        body += "Co-Authored-By: Claude <noreply@anthropic.com>\n"

        if dry_run:
            console.print("\n[yellow]DRY RUN - PR would be created with:[/yellow]")
            console.print(f"[bold]Title:[/bold] {title}")
            console.print(f"[bold]Body:[/bold]\n{body}")
            console.print(f"[bold]Draft:[/bold] {draft}")
            if labels:
                console.print(f"[bold]Labels:[/bold] {', '.join(labels)}")
            if reviewers:
                console.print(f"[bold]Reviewers:[/bold] {', '.join(reviewers)}")
            return

        # Create PR via git_ops
        console.print("\n[dim]Creating pull request...[/dim]")

        pr_params = {
            "title": title,
            "body": body,
            "draft": draft,
        }

        if labels:
            pr_params["labels"] = labels
        if reviewers:
            pr_params["reviewers"] = reviewers

        # Note: Actual PR creation would use gh CLI or GitHub API
        # This is a simplified placeholder
        result = git_ops.execute(
            {"actor": "git_ops", "with": {"operation": "create_pr", **pr_params}},
            None,
            None
        )

        if result.success:
            console.print("[green]Pull request created successfully[/green]")
            if result.metadata and "pr_url" in result.metadata:
                console.print(f"\n[bold]PR URL:[/bold] {result.metadata['pr_url']}")
        else:
            console.print(f"[red]Failed to create PR: {result.error}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]PR creation error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_prs(
    state: str = typer.Option(
        "open",
        "--state",
        "-s",
        help="PR state (open, closed, all)"
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-n",
        help="Maximum number of PRs to show"
    ),
):
    """
    List pull requests in the repository.

    Examples:
        cli-orchestrator pr list
        cli-orchestrator pr list --state all --limit 50
        cli-orchestrator pr list --state closed
    """
    console.print(f"[bold]Listing {state} pull requests[/bold]")

    try:
        from ..adapters.git_ops import GitOpsAdapter

        git_ops = GitOpsAdapter()

        # Get PRs via git_ops
        result = git_ops.execute(
            {
                "actor": "git_ops",
                "with": {"operation": "list_prs", "state": state, "limit": limit}
            },
            None,
            None
        )

        if not result.success:
            console.print(f"[red]Failed to list PRs: {result.error}[/red]")
            raise typer.Exit(1)

        prs = result.metadata.get("prs", [])

        if not prs:
            console.print(f"[yellow]No {state} pull requests found[/yellow]")
            return

        # Display PRs in table
        table = Table(title=f"{state.capitalize()} Pull Requests")
        table.add_column("Number", style="cyan", justify="right")
        table.add_column("Title")
        table.add_column("Author", style="dim")
        table.add_column("State", style="bold")
        table.add_column("Created", style="dim")

        for pr in prs:
            state_color = "green" if pr.get("state") == "open" else "red"
            table.add_row(
                f"#{pr.get('number', '?')}",
                pr.get("title", ""),
                pr.get("author", ""),
                f"[{state_color}]{pr.get('state', '')}[/{state_color}]",
                pr.get("created_at", "")
            )

        console.print(table)
        console.print(f"\n[dim]Showing {len(prs)} PR(s)[/dim]")

    except Exception as e:
        console.print(f"[red]Error listing PRs: {e}[/red]")
        raise typer.Exit(1)


@app.command("status")
def pr_status(
    pr_number: Optional[int] = typer.Argument(
        None,
        help="PR number (omit to show current branch PR)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Show status of a pull request.

    Examples:
        cli-orchestrator pr status
        cli-orchestrator pr status 123
        cli-orchestrator pr status 123 --verbose
    """
    try:
        from ..adapters.git_ops import GitOpsAdapter

        git_ops = GitOpsAdapter()

        # If no PR number, try to find PR for current branch
        if pr_number is None:
            console.print("[dim]Finding PR for current branch...[/dim]")
            result = git_ops.execute(
                {"actor": "git_ops", "with": {"operation": "get_current_pr"}},
                None,
                None
            )

            if result.success and result.metadata:
                pr_number = result.metadata.get("pr_number")
            else:
                console.print("[yellow]No PR found for current branch[/yellow]")
                console.print("[dim]You can create one with: cli-orchestrator pr create[/dim]")
                raise typer.Exit(1)

        console.print(f"[bold]PR #{pr_number} Status[/bold]")

        # Get PR details
        result = git_ops.execute(
            {"actor": "git_ops", "with": {"operation": "pr_status", "pr_number": pr_number}},
            None,
            None
        )

        if not result.success:
            console.print(f"[red]Failed to get PR status: {result.error}[/red]")
            raise typer.Exit(1)

        pr_data = result.metadata

        # Display PR info
        console.print(f"\n[bold]Title:[/bold] {pr_data.get('title', '')}")
        console.print(f"[bold]Author:[/bold] {pr_data.get('author', '')}")
        console.print(f"[bold]State:[/bold] {pr_data.get('state', '')}")
        console.print(f"[bold]Mergeable:[/bold] {pr_data.get('mergeable', 'unknown')}")

        if pr_data.get("labels"):
            console.print(f"[bold]Labels:[/bold] {', '.join(pr_data.get('labels', []))}")

        # Checks status
        checks = pr_data.get("checks", {})
        if checks:
            console.print(f"\n[bold]Checks:[/bold]")
            console.print(f"  Total: {checks.get('total', 0)}")
            console.print(f"  Passed: {checks.get('passed', 0)}")
            console.print(f"  Failed: {checks.get('failed', 0)}")
            console.print(f"  Pending: {checks.get('pending', 0)}")

        # Reviews
        reviews = pr_data.get("reviews", {})
        if reviews:
            console.print(f"\n[bold]Reviews:[/bold]")
            console.print(f"  Approved: {reviews.get('approved', 0)}")
            console.print(f"  Changes requested: {reviews.get('changes_requested', 0)}")
            console.print(f"  Pending: {reviews.get('pending', 0)}")

        if verbose:
            console.print(f"\n[bold]URL:[/bold] {pr_data.get('url', '')}")
            console.print(f"[bold]Created:[/bold] {pr_data.get('created_at', '')}")
            console.print(f"[bold]Updated:[/bold] {pr_data.get('updated_at', '')}")

    except Exception as e:
        console.print(f"[red]Error getting PR status: {e}[/red]")
        raise typer.Exit(1)


@app.command("close")
def close_pr(
    pr_number: int = typer.Argument(..., help="PR number to close"),
    comment: Optional[str] = typer.Option(
        None,
        "--comment",
        "-c",
        help="Comment to add when closing"
    ),
):
    """
    Close a pull request.

    Examples:
        cli-orchestrator pr close 123
        cli-orchestrator pr close 123 --comment "No longer needed"
    """
    console.print(f"[bold]Closing PR #{pr_number}[/bold]")

    try:
        from ..adapters.git_ops import GitOpsAdapter

        git_ops = GitOpsAdapter()

        params = {
            "operation": "close_pr",
            "pr_number": pr_number
        }

        if comment:
            params["comment"] = comment

        result = git_ops.execute(
            {"actor": "git_ops", "with": params},
            None,
            None
        )

        if result.success:
            console.print(f"[green]PR #{pr_number} closed successfully[/green]")
        else:
            console.print(f"[red]Failed to close PR: {result.error}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error closing PR: {e}[/red]")
        raise typer.Exit(1)


def _generate_pr_body_from_artifacts(artifact_dir: Path) -> str:
    """Generate PR body from artifacts directory."""
    body = "## Summary\n\n"
    body += "Automated changes generated by CLI Orchestrator workflow.\n\n"

    if artifact_dir.exists():
        artifacts = list(artifact_dir.rglob("*"))
        if artifacts:
            body += "## Artifacts Generated\n\n"
            for artifact in artifacts:
                if artifact.is_file():
                    body += f"- `{artifact.name}`\n"

    body += "\n## Test Plan\n\n"
    body += "- [ ] All existing tests pass\n"
    body += "- [ ] Code quality checks pass\n"
    body += "- [ ] Manual testing completed\n"

    return body


if __name__ == "__main__":
    app()
