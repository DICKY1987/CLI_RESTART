#!/usr/bin/env python3
"""
Cost Commands - CLI commands for cost tracking and budget management

Provides commands for tracking token usage, costs, and budget enforcement.
Part of Phase 3 CLI modularization.
"""

import typer
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Cost tracking and budget management commands")
console = Console()


@app.command("report")
def cost_report(
    last_run: bool = typer.Option(
        False,
        "--last-run",
        help="Show cost for last workflow run"
    ),
    last_n: Optional[int] = typer.Option(
        None,
        "--last-n",
        help="Show cost for last N runs"
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Show costs since date (YYYY-MM-DD)"
    ),
    by_adapter: bool = typer.Option(
        False,
        "--by-adapter",
        help="Break down costs by adapter"
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, json, csv)"
    ),
):
    """
    Generate cost report for workflow executions.

    Examples:
        cli-orchestrator cost report --last-run
        cli-orchestrator cost report --last-n 10
        cli-orchestrator cost report --since 2024-01-01
        cli-orchestrator cost report --by-adapter --format json
    """
    console.print("[bold]Cost Report[/bold]")

    try:
        from ..cost_tracker import CostTracker

        cost_tracker = CostTracker()

        # Load cost data
        cost_data = _load_cost_data(last_run, last_n, since)

        if not cost_data:
            console.print("[yellow]No cost data found for specified criteria[/yellow]")
            return

        # Calculate totals
        total_tokens = sum(entry.get("tokens", 0) for entry in cost_data)
        total_cost_usd = _calculate_cost_usd(total_tokens)

        # Display summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Total runs: {len(cost_data)}")
        console.print(f"  Total tokens: {total_tokens:,}")
        console.print(f"  Estimated cost: ${total_cost_usd:.2f} USD")

        if by_adapter:
            # Break down by adapter
            adapter_costs = {}
            for entry in cost_data:
                adapter = entry.get("adapter", "unknown")
                tokens = entry.get("tokens", 0)
                adapter_costs[adapter] = adapter_costs.get(adapter, 0) + tokens

            console.print(f"\n[bold]Cost by Adapter:[/bold]")
            table = Table()
            table.add_column("Adapter", style="cyan")
            table.add_column("Tokens", justify="right")
            table.add_column("Cost (USD)", justify="right", style="green")

            for adapter, tokens in sorted(adapter_costs.items(), key=lambda x: x[1], reverse=True):
                cost_usd = _calculate_cost_usd(tokens)
                table.add_row(adapter, f"{tokens:,}", f"${cost_usd:.2f}")

            console.print(table)

        elif output_format == "table":
            # Display as table
            table = Table()
            table.add_column("Run", style="dim")
            table.add_column("Timestamp", style="dim")
            table.add_column("Adapter", style="cyan")
            table.add_column("Tokens", justify="right")
            table.add_column("Cost (USD)", justify="right", style="green")

            for i, entry in enumerate(cost_data[:20], 1):  # Limit to 20 entries
                timestamp = entry.get("timestamp", "")
                adapter = entry.get("adapter", "unknown")
                tokens = entry.get("tokens", 0)
                cost_usd = _calculate_cost_usd(tokens)

                table.add_row(
                    str(i),
                    timestamp,
                    adapter,
                    f"{tokens:,}",
                    f"${cost_usd:.2f}"
                )

            console.print(f"\n[bold]Recent Runs:[/bold]")
            console.print(table)

            if len(cost_data) > 20:
                console.print(f"[dim]Showing 20 of {len(cost_data)} runs[/dim]")

        elif output_format == "json":
            import json
            output = {
                "total_runs": len(cost_data),
                "total_tokens": total_tokens,
                "total_cost_usd": total_cost_usd,
                "runs": cost_data
            }
            console.print(json.dumps(output, indent=2))

        elif output_format == "csv":
            console.print("timestamp,adapter,tokens,cost_usd")
            for entry in cost_data:
                console.print(
                    f"{entry.get('timestamp', '')},{entry.get('adapter', '')},"
                    f"{entry.get('tokens', 0)},{_calculate_cost_usd(entry.get('tokens', 0)):.2f}"
                )

    except Exception as e:
        console.print(f"[red]Error generating cost report: {e}[/red]")
        raise typer.Exit(1)


@app.command("budget")
def check_budget(
    budget_limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help="Budget limit in tokens"
    ),
    budget_usd: Optional[float] = typer.Option(
        None,
        "--limit-usd",
        help="Budget limit in USD"
    ),
    period: str = typer.Option(
        "day",
        "--period",
        "-p",
        help="Budget period (day, week, month)"
    ),
):
    """
    Check current usage against budget limits.

    Examples:
        cli-orchestrator cost budget --limit 100000
        cli-orchestrator cost budget --limit-usd 10.00 --period week
        cli-orchestrator cost budget --limit 500000 --period month
    """
    console.print(f"[bold]Budget Check ({period})[/bold]")

    try:
        from ..cost_tracker import CostTracker

        # Load cost data for period
        since_date = _get_period_start_date(period)
        cost_data = _load_cost_data_since(since_date)

        # Calculate usage
        current_tokens = sum(entry.get("tokens", 0) for entry in cost_data)
        current_cost_usd = _calculate_cost_usd(current_tokens)

        # Convert budget to tokens if given in USD
        if budget_usd is not None:
            budget_limit = int((budget_usd / 0.015) * 1000)  # Reverse calculation

        if budget_limit is None:
            # Use default budget from environment or config
            from ..config import get_settings
            settings = get_settings()
            budget_limit = settings.max_token_budget

        # Calculate percentage
        usage_pct = (current_tokens / budget_limit * 100) if budget_limit > 0 else 0

        # Display results
        console.print(f"\n[bold]Current Usage:[/bold]")
        console.print(f"  Tokens: {current_tokens:,} / {budget_limit:,} ({usage_pct:.1f}%)")
        console.print(f"  Cost: ${current_cost_usd:.2f} USD")

        # Status indicator
        if usage_pct >= 90:
            console.print("\n[red]WARNING: Budget usage is at {usage_pct:.1f}%[/red]")
            raise typer.Exit(1)
        elif usage_pct >= 75:
            console.print(f"\n[yellow]CAUTION: Budget usage is at {usage_pct:.1f}%[/yellow]")
        else:
            console.print(f"\n[green]Budget usage is healthy at {usage_pct:.1f}%[/green]")

        # Remaining budget
        remaining_tokens = budget_limit - current_tokens
        remaining_usd = _calculate_cost_usd(remaining_tokens)
        console.print(f"\n[bold]Remaining:[/bold]")
        console.print(f"  Tokens: {remaining_tokens:,}")
        console.print(f"  Cost: ${remaining_usd:.2f} USD")

    except Exception as e:
        console.print(f"[red]Error checking budget: {e}[/red]")
        raise typer.Exit(1)


@app.command("trend")
def show_trend(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to analyze"),
    chart_type: str = typer.Option(
        "bar",
        "--chart",
        "-c",
        help="Chart type (bar, line)"
    ),
):
    """
    Show cost trend over time.

    Examples:
        cli-orchestrator cost trend --days 7
        cli-orchestrator cost trend --days 30 --chart line
    """
    console.print(f"[bold]Cost Trend (Last {days} days)[/bold]")

    try:
        # Load cost data
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        cost_data = _load_cost_data_since(since_date)

        if not cost_data:
            console.print("[yellow]No cost data available for the specified period[/yellow]")
            return

        # Group by day
        daily_costs = {}
        for entry in cost_data:
            date = entry.get("timestamp", "")[:10]  # YYYY-MM-DD
            tokens = entry.get("tokens", 0)
            daily_costs[date] = daily_costs.get(date, 0) + tokens

        # Display trend
        table = Table()
        table.add_column("Date", style="cyan")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost (USD)", justify="right", style="green")
        table.add_column("Trend", justify="right")

        max_tokens = max(daily_costs.values()) if daily_costs else 1

        for date in sorted(daily_costs.keys()):
            tokens = daily_costs[date]
            cost_usd = _calculate_cost_usd(tokens)

            # Simple bar chart
            bar_length = int((tokens / max_tokens) * 20)
            bar = "█" * bar_length

            table.add_row(date, f"{tokens:,}", f"${cost_usd:.2f}", bar)

        console.print(table)

        # Summary stats
        total_tokens = sum(daily_costs.values())
        avg_tokens = total_tokens / len(daily_costs) if daily_costs else 0
        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total: {total_tokens:,} tokens")
        console.print(f"  Average: {avg_tokens:,.0f} tokens/day")
        console.print(f"  Peak: {max_tokens:,} tokens")

    except Exception as e:
        console.print(f"[red]Error showing trend: {e}[/red]")
        raise typer.Exit(1)


@app.command("reset")
def reset_costs(
    confirm: bool = typer.Option(
        False,
        "--confirm",
        help="Confirm cost reset"
    ),
):
    """
    Reset cost tracking data.

    WARNING: This will delete all cost tracking history.

    Examples:
        cli-orchestrator cost reset --confirm
    """
    if not confirm:
        console.print("[yellow]This will delete all cost tracking data.[/yellow]")
        console.print("[dim]Use --confirm to proceed[/dim]")
        raise typer.Exit(1)

    console.print("[bold]Resetting cost tracking data...[/bold]")

    try:
        from ..cost_tracker import CostTracker

        cost_tracker = CostTracker()

        # Reset (implementation would clear cost log files)
        cost_dir = Path("cost")
        if cost_dir.exists():
            import shutil
            shutil.rmtree(cost_dir)
            cost_dir.mkdir(exist_ok=True)
            console.print("[green]Cost tracking data reset successfully[/green]")
        else:
            console.print("[yellow]No cost data to reset[/yellow]")

    except Exception as e:
        console.print(f"[red]Error resetting costs: {e}[/red]")
        raise typer.Exit(1)


# Helper functions

def _load_cost_data(last_run=False, last_n=None, since=None):
    """Load cost data based on criteria."""
    cost_dir = Path("cost")

    if not cost_dir.exists():
        return []

    # Find cost log files
    cost_files = list(cost_dir.glob("*.jsonl"))

    if not cost_files:
        return []

    # Load and parse
    import json
    cost_entries = []

    for cost_file in cost_files:
        with open(cost_file) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    cost_entries.append(entry)
                except json.JSONDecodeError:
                    continue

    # Apply filters
    if last_run and cost_entries:
        return [cost_entries[-1]]
    elif last_n:
        return cost_entries[-last_n:]
    elif since:
        return [e for e in cost_entries if e.get("timestamp", "") >= since]
    else:
        return cost_entries


def _load_cost_data_since(since_date):
    """Load cost data since a specific date."""
    return _load_cost_data(since=since_date)


def _calculate_cost_usd(tokens):
    """Calculate cost in USD from tokens."""
    # Using Claude Sonnet pricing: $0.015 per 1K tokens
    return (tokens / 1000) * 0.015


def _get_period_start_date(period):
    """Get start date for budget period."""
    now = datetime.now()

    if period == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now

    return start.strftime("%Y-%m-%d")


if __name__ == "__main__":
    app()
