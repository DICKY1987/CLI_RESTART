#!/usr/bin/env python3
"""
Workflow Commands - CLI commands for workflow execution

Provides commands for running and listing workflows using the new core modules.
Part of Phase 3 CLI modularization.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Workflow execution commands")
console = Console()


@app.command("run")
def run_workflow(
    workflow_path: Path = typer.Argument(..., help="Path to workflow YAML file"),
    files: Optional[str] = typer.Option(None, "--files", help="File pattern to process"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate execution without changes"),
    lane: Optional[str] = typer.Option(None, "--lane", help="Git workflow lane"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Maximum token budget"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run a workflow from YAML file.

    Examples:
        cli-orchestrator workflow run .ai/workflows/PY_EDIT_TRIAGE.yaml
        cli-orchestrator workflow run workflow.yaml --files "src/**/*.py" --dry-run
        cli-orchestrator workflow run workflow.yaml --lane lane/ai-coding/fix-imports
    """
    if not workflow_path.exists():
        console.print(f"[red]Error: Workflow file not found: {workflow_path}[/red]")
        raise typer.Exit(1)

    # Import core modules
    from ..core.coordinator import WorkflowCoordinator
    from ..core.executor import StepExecutor
    from ..cost_tracker import CostTracker
    from ..router import Router

    # Display execution info
    console.print(f"[bold]Executing workflow:[/bold] {workflow_path.name}")
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")
    if files:
        console.print(f"[dim]Files pattern:[/dim] {files}")
    if lane:
        console.print(f"[dim]Lane:[/dim] {lane}")

    # Initialize core modules
    try:
        router = Router()
        cost_tracker = CostTracker()
        executor = StepExecutor(router, cost_tracker, dry_run=dry_run)
        coordinator = WorkflowCoordinator(executor)

        # Build extra context
        extra_context = {}
        if lane:
            extra_context["lane"] = lane
        if max_tokens:
            extra_context["max_tokens"] = max_tokens

        # Execute workflow
        result = coordinator.execute_workflow(
            str(workflow_path),
            files=files,
            extra_context=extra_context if extra_context else None
        )

        # Display results
        console.print()
        if result.success:
            console.print("[green]Workflow completed successfully[/green]")
        else:
            console.print(f"[red]Workflow failed: {result.error}[/red]")

        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Steps: {result.steps_succeeded}/{result.steps_executed} succeeded")
        console.print(f"  Tokens: {result.total_tokens_used:,}")
        console.print(f"  Time: {result.total_execution_time_seconds:.2f}s")

        if result.artifacts:
            console.print("\n[bold]Artifacts generated:[/bold]")
            for artifact in result.artifacts:
                console.print(f"  - {artifact}")

        if verbose and result.step_results:
            console.print("\n[bold]Step Details:[/bold]")
            for step_result in result.step_results:
                status = "[green]OK[/green]" if step_result.success else "[red]FAILED[/red]"
                console.print(f"  {step_result.step_id}: {status}")
                if step_result.error:
                    console.print(f"    Error: {step_result.error}")

        if not result.success:
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error executing workflow: {e}[/red]")
        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


@app.command("list")
def list_workflows(
    workflow_dir: Path = typer.Option(
        ".ai/workflows",
        "--dir",
        "-d",
        help="Workflow directory to search"
    ),
    pattern: str = typer.Option(
        "*.yaml",
        "--pattern",
        "-p",
        help="File pattern (e.g., '*.yaml', '*.yml')"
    ),
):
    """
    List available workflows in a directory.

    Examples:
        cli-orchestrator workflow list
        cli-orchestrator workflow list --dir workflows/
        cli-orchestrator workflow list --pattern "*.yml"
    """
    if not workflow_dir.exists():
        console.print(f"[red]Workflow directory not found: {workflow_dir}[/red]")
        raise typer.Exit(1)

    # Find workflows
    workflows = list(workflow_dir.glob(pattern))
    if pattern == "*.yaml":  # Also include .yml if searching for .yaml
        workflows.extend(workflow_dir.glob("*.yml"))

    if not workflows:
        console.print(f"[yellow]No workflows found in {workflow_dir} matching '{pattern}'[/yellow]")
        return

    # Create table
    table = Table(title=f"Available Workflows in {workflow_dir}")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("File", style="green")
    table.add_column("Size", justify="right", style="dim")

    # Add workflows to table
    for workflow in sorted(workflows):
        size_kb = workflow.stat().st_size / 1024
        table.add_row(
            workflow.stem,
            workflow.name,
            f"{size_kb:.1f} KB"
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(workflows)} workflow(s)[/dim]")


@app.command("validate")
def validate_workflow(
    workflow_path: Path = typer.Argument(..., help="Path to workflow YAML file"),
    schema_path: Optional[Path] = typer.Option(
        None,
        "--schema",
        "-s",
        help="Path to workflow schema (defaults to .ai/schemas/workflow.schema.json)"
    ),
):
    """
    Validate a workflow file against the schema.

    Examples:
        cli-orchestrator workflow validate workflow.yaml
        cli-orchestrator workflow validate workflow.yaml --schema custom.schema.json
    """
    if not workflow_path.exists():
        console.print(f"[red]Error: Workflow file not found: {workflow_path}[/red]")
        raise typer.Exit(1)

    # Default schema path
    if schema_path is None:
        schema_path = Path(".ai/schemas/workflow.schema.json")

    if not schema_path.exists():
        console.print(f"[red]Error: Schema file not found: {schema_path}[/red]")
        raise typer.Exit(1)

    # Import coordinator
    from ..core.coordinator import WorkflowCoordinator
    from ..core.executor import StepExecutor
    from ..router import Router

    console.print(f"[bold]Validating workflow:[/bold] {workflow_path.name}")
    console.print(f"[dim]Schema:[/dim] {schema_path}")

    try:
        # Initialize coordinator
        executor = StepExecutor(Router())
        coordinator = WorkflowCoordinator(executor)

        # Validate workflow
        validation_result = coordinator.validate_workflow_file(str(workflow_path))

        if validation_result["valid"]:
            console.print("[green]Workflow is valid[/green]")
            console.print(f"  Steps: {validation_result.get('steps_count', 0)}")
            console.print(f"  Policy defined: {validation_result.get('has_policy', False)}")
        else:
            console.print("[red]Workflow is invalid[/red]")
            if "errors" in validation_result:
                console.print("\n[bold]Validation errors:[/bold]")
                for error in validation_result["errors"]:
                    console.print(f"  - {error}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Validation error: {e}[/red]")
        raise typer.Exit(1)


@app.command("cost")
def estimate_cost(
    workflow_path: Path = typer.Argument(..., help="Path to workflow YAML file"),
    files: Optional[str] = typer.Option(None, "--files", help="File pattern to process"),
):
    """
    Estimate token cost for a workflow without executing it.

    Examples:
        cli-orchestrator workflow cost workflow.yaml
        cli-orchestrator workflow cost workflow.yaml --files "src/**/*.py"
    """
    if not workflow_path.exists():
        console.print(f"[red]Error: Workflow file not found: {workflow_path}[/red]")
        raise typer.Exit(1)

    # Import core modules
    from ..core.coordinator import WorkflowCoordinator
    from ..core.executor import StepExecutor
    from ..router import Router

    console.print(f"[bold]Estimating cost for:[/bold] {workflow_path.name}")
    if files:
        console.print(f"[dim]Files pattern:[/dim] {files}")

    try:
        # Initialize coordinator
        executor = StepExecutor(Router())
        coordinator = WorkflowCoordinator(executor)

        # Estimate cost
        cost_estimate = coordinator.estimate_workflow_cost(str(workflow_path))

        console.print("\n[bold]Cost Estimate:[/bold]")
        console.print(f"  Total tokens: {cost_estimate['total_tokens']:,}")
        console.print(f"  Steps analyzed: {cost_estimate['steps_analyzed']}")

        if "steps" in cost_estimate:
            console.print("\n[bold]Per-step breakdown:[/bold]")
            for step in cost_estimate["steps"]:
                console.print(f"  {step['step_id']}: {step['estimated_tokens']:,} tokens")

        # Show cost in USD (rough estimate)
        # Assuming $0.015 per 1K tokens (typical for Claude Sonnet)
        est_cost_usd = (cost_estimate['total_tokens'] / 1000) * 0.015
        console.print(f"\n[dim]Estimated cost: ~${est_cost_usd:.2f} USD[/dim]")
        console.print("[dim](Based on Claude Sonnet pricing)[/dim]")

    except Exception as e:
        console.print(f"[red]Cost estimation error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
