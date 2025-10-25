#!/usr/bin/env python3
"""
CLI Orchestrator - Main CLI Application

Unified CLI entrypoint that registers all command modules.
Part of Phase 3 CLI modularization.
"""

import typer
from rich.console import Console

# Import command modules
from .commands import (
    cost_commands,
    pr_commands,
    verify_commands,
    workflow_commands,
    agentic_commands,
)

# Create main app
app = typer.Typer(
    name="cli-orchestrator",
    help="CLI Orchestrator - Deterministic, schema-driven workflow automation",
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()


# Register command modules as subcommands
app.add_typer(
    workflow_commands.app,
    name="workflow",
    help="Workflow execution and management"
)

app.add_typer(
    verify_commands.app,
    name="verify",
    help="Artifact verification and quality gates"
)

app.add_typer(
    pr_commands.app,
    name="pr",
    help="Pull request creation and management"
)

app.add_typer(
    cost_commands.app,
    name="cost",
    help="Cost tracking and budget management"
)

app.add_typer(
    agentic_commands.app,
    name="agentic",
    help="Agentic development and code-intel"
)


@app.command()
def version():
    """Show version information."""
    console.print("[bold]CLI Orchestrator[/bold]")
    console.print("Version: 1.0.0 (Phase 3 Refactored)")
    console.print("Python CLI for schema-driven workflow automation")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    validate: bool = typer.Option(False, "--validate", help="Validate configuration"),
):
    """
    Manage CLI configuration.

    Examples:
        cli-orchestrator config --show
        cli-orchestrator config --validate
    """
    if show:
        console.print("[bold]Current Configuration:[/bold]")

        try:
            from .config import get_settings
            settings = get_settings()

            console.print(f"  Environment: {settings.cli_orchestrator_env}")
            console.print(f"  Debug: {settings.debug}")
            console.print(f"  Max Token Budget: {settings.max_token_budget:,}")
            console.print(f"  Workflow Timeout: {settings.default_workflow_timeout} minutes")
            console.print(f"  Workflow Dir: {settings.workflow_dir}")
            console.print(f"  Artifacts Dir: {settings.artifacts_dir}")
            console.print(f"  Logs Dir: {settings.logs_dir}")

            # API keys (masked)
            console.print("\n[bold]API Keys:[/bold]")
            console.print(f"  GitHub Token: {' Set' if settings.github_token else ' Not set'}")
            console.print(f"  Anthropic API Key: {' Set' if settings.anthropic_api_key else ' Not set'}")
            console.print(f"  OpenAI API Key: {' Set' if settings.openai_api_key else ' Not set'}")
            console.print(f"  Google API Key: {' Set' if settings.google_api_key else ' Not set'}")
            console.print(f"  Ollama API Base: {settings.ollama_api_base}")

        except Exception as e:
            console.print(f"[red]Error loading configuration: {e}[/red]")
            raise typer.Exit(1)

    elif validate:
        console.print("[bold]Validating configuration...[/bold]")

        try:
            from .config import get_settings
            settings = get_settings()

            # Validate required directories
            dirs_ok = True
            for dir_name in ["workflow_dir", "artifacts_dir", "logs_dir"]:
                dir_path = getattr(settings, dir_name)
                if not dir_path.exists():
                    console.print(f"[yellow]Warning: {dir_name} does not exist: {dir_path}[/yellow]")
                    dirs_ok = False

            # Check for at least one AI API key
            has_api_key = any([
                settings.anthropic_api_key,
                settings.openai_api_key,
                settings.google_api_key,
            ])

            if not has_api_key:
                console.print("[yellow]Warning: No AI API keys configured[/yellow]")

            if dirs_ok and has_api_key:
                console.print("[green]Configuration is valid[/green]")
            else:
                console.print("[yellow]Configuration has warnings[/yellow]")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Validation error: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[dim]Use --show or --validate[/dim]")


@app.callback()
def callback():
    """
    CLI Orchestrator - Deterministic, schema-driven workflow automation.

    For detailed help on specific commands:
        cli-orchestrator workflow --help
        cli-orchestrator verify --help
        cli-orchestrator pr --help
        cli-orchestrator cost --help
    """
    pass


def main():
    """Main entrypoint."""
    app()


if __name__ == "__main__":
    main()
