#!/usr/bin/env python
"""Generate shell completion scripts for CLI orchestrator."""

from __future__ import annotations

import typer
from pathlib import Path

app = typer.Typer()


@app.command()
def generate(
    shell: str = typer.Argument(..., help="Shell type (bash, zsh, powershell)"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Generate shell completion script."""
    from cli_multi_rapid.main import app as main_app

    completions_map = {
        "bash": "_cli-orchestrator-complete.sh",
        "zsh": "_cli-orchestrator",
        "powershell": "cli-orchestrator.ps1",
    }

    if shell not in completions_map:
        typer.secho(
            f"Unsupported shell: {shell}. Supported: {', '.join(completions_map.keys())}",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Generate completion
    try:
        import click

        ctx = click.Context(main_app)
        completion_class = click.shell_completion.get_completion_class(shell)
        if completion_class:
            completion = completion_class(main_app, {}, "cli-orchestrator", "_CLI_ORCHESTRATOR_COMPLETE")
            script = completion.source()

            if output:
                Path(output).write_text(script)
                typer.secho(f"✓ Generated {shell} completion: {output}", fg=typer.colors.GREEN)
            else:
                print(script)
        else:
            typer.secho(f"Could not generate completion for {shell}", fg=typer.colors.RED)
            raise typer.Exit(1)

    except Exception as e:
        typer.secho(f"Error generating completion: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def install(shell: str = typer.Argument(..., help="Shell type (bash, zsh, powershell)")):
    """Install completion script to standard location."""
    import os
    import shutil

    home = Path.home()
    locations = {
        "bash": home / ".bash_completion.d" / "cli-orchestrator",
        "zsh": home / ".zsh" / "completions" / "_cli-orchestrator",
        "powershell": home / "Documents" / "PowerShell" / "Scripts" / "cli-orchestrator-completion.ps1",
    }

    if shell not in locations:
        typer.secho(f"Unsupported shell: {shell}", fg=typer.colors.RED)
        raise typer.Exit(1)

    dest = locations[shell]
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Generate and install
    from cli_multi_rapid.main import app as main_app
    import click

    ctx = click.Context(main_app)
    completion_class = click.shell_completion.get_completion_class(shell)
    if completion_class:
        completion = completion_class(main_app, {}, "cli-orchestrator", "_CLI_ORCHESTRATOR_COMPLETE")
        script = completion.source()
        dest.write_text(script)
        typer.secho(f"✓ Installed {shell} completion to: {dest}", fg=typer.colors.GREEN)
        typer.secho(f"\nAdd to your {shell} config:", fg=typer.colors.YELLOW)
        if shell == "bash":
            typer.echo(f"  source {dest}")
        elif shell == "zsh":
            typer.echo(f"  fpath=({dest.parent} $fpath)")
            typer.echo("  autoload -Uz compinit && compinit")
        elif shell == "powershell":
            typer.echo(f"  . {dest}")
    else:
        typer.secho(f"Could not install completion for {shell}", fg=typer.colors.RED)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
