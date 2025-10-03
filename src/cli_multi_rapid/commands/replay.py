"""Replay command for viewing AI conversation history."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

app = typer.Typer(help="Replay and analyze AI conversations")
console = Console()


@app.command()
def show(
    conversation_id: str = typer.Argument(..., help="Conversation ID to replay"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full details"),
):
    """Show a specific AI conversation with full details."""
    from cli_multi_rapid.logging.conversation_logger import ConversationLogger

    logger = ConversationLogger()
    entries = logger.get_conversation(conversation_id)

    if not entries:
        console.print(
            f"[red]No conversation found with ID: {conversation_id}[/red]"
        )
        raise typer.Exit(1)

    # Display conversation header
    first_entry = entries[0]
    console.print()
    console.print(
        Panel(
            f"[bold cyan]Conversation: {conversation_id}[/bold cyan]\n"
            f"Adapter: {first_entry.get('adapter_name', 'Unknown')}\n"
            f"Model: {first_entry.get('model', 'Unknown')}\n"
            f"Timestamp: {first_entry.get('timestamp', 'Unknown')}\n"
            f"Turns: {len(entries)}",
            title="Conversation Details",
            border_style="cyan",
        )
    )
    console.print()

    # Display each turn
    for i, entry in enumerate(entries, 1):
        turn_number = entry.get("turn_number", i)
        timestamp = entry.get("timestamp", "Unknown")

        # Turn header
        console.print(f"[bold yellow]Turn {turn_number}[/bold yellow] - {timestamp}")
        console.print()

        # Prompt
        console.print("[bold green]Prompt:[/bold green]")
        prompt = entry.get("prompt", "")
        if len(prompt) > 500 and not verbose:
            prompt = prompt[:500] + "... [truncated]"
        console.print(Panel(prompt, border_style="green"))
        console.print()

        # Response
        console.print("[bold blue]Response:[/bold blue]")
        response = entry.get("response", "")
        if len(response) > 1000 and not verbose:
            response = response[:1000] + "... [truncated]"
        console.print(Panel(response, border_style="blue"))
        console.print()

        # Metadata (if verbose)
        if verbose:
            metadata = entry.get("metadata", {})
            if metadata:
                console.print("[bold magenta]Metadata:[/bold magenta]")
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Key")
                table.add_column("Value")

                for key, value in metadata.items():
                    table.add_row(str(key), str(value))

                console.print(table)
                console.print()

            context = entry.get("context", {})
            if context:
                console.print("[bold cyan]Context:[/bold cyan]")
                import json

                console.print(
                    Syntax(
                        json.dumps(context, indent=2),
                        "json",
                        theme="monokai",
                        line_numbers=True,
                    )
                )
                console.print()

        console.print("[dim]" + "─" * 80 + "[/dim]")
        console.print()


@app.command()
def list(
    date: Optional[str] = typer.Option(
        None, "--date", "-d", help="Filter by date (YYYY-MM-DD)"
    ),
    adapter: Optional[str] = typer.Option(
        None, "--adapter", "-a", help="Filter by adapter name"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Filter by AI model"
    ),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum conversations to show"),
):
    """List recent AI conversations."""
    from cli_multi_rapid.logging.conversation_logger import ConversationLogger

    logger = ConversationLogger()
    conversations = logger.list_conversations(
        date=date, adapter_name=adapter, model=model, limit=limit
    )

    if not conversations:
        console.print("[yellow]No conversations found[/yellow]")
        return

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Conversation ID", style="cyan", no_wrap=True)
    table.add_column("Adapter", style="green")
    table.add_column("Model", style="blue")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Turns", justify="right", style="yellow")

    for conv in conversations:
        table.add_row(
            conv.get("conversation_id", "Unknown"),
            conv.get("adapter_name", "Unknown"),
            conv.get("model", "Unknown"),
            conv.get("timestamp", "Unknown"),
            str(conv.get("turns", 0)),
        )

    console.print()
    console.print(table)
    console.print()
    console.print(
        f"[dim]Showing {len(conversations)} conversation(s). "
        f"Use 'cli-orchestrator replay show <id>' to view details.[/dim]"
    )


@app.command()
def export(
    conversation_id: str = typer.Argument(..., help="Conversation ID to export"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
):
    """Export a conversation to JSON file."""
    from cli_multi_rapid.logging.conversation_logger import ConversationLogger

    logger = ConversationLogger()

    # Determine output path
    if not output:
        output = Path(f"conversation_{conversation_id}.json")

    # Export conversation
    success = logger.export_conversation(conversation_id, output)

    if success:
        console.print(
            f"[green]Conversation exported to: {output}[/green]"
        )
    else:
        console.print(
            f"[red]Failed to export conversation: {conversation_id}[/red]"
        )
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query (regex supported)"),
    date: Optional[str] = typer.Option(
        None, "--date", "-d", help="Filter by date (YYYY-MM-DD)"
    ),
    limit: int = typer.Option(20, "--limit", "-n", help="Maximum results to show"),
):
    """Search conversations by content."""
    import json
    import re

    from cli_multi_rapid.logging.conversation_logger import ConversationLogger

    logger = ConversationLogger()

    # Compile search pattern
    try:
        pattern = re.compile(query, re.IGNORECASE)
    except re.error as e:
        console.print(f"[red]Invalid regex pattern: {e}[/red]")
        raise typer.Exit(1)

    # Search through conversations
    matches = []

    # Determine which log files to search
    if date:
        log_files = [logger.log_dir / f"{date}.jsonl"]
    else:
        log_files = sorted(logger.log_dir.glob("*.jsonl"), reverse=True)

    for log_file in log_files:
        if not log_file.exists():
            continue

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    entry = json.loads(line)

                    # Search in prompt and response
                    prompt = entry.get("prompt", "")
                    response = entry.get("response", "")

                    if pattern.search(prompt) or pattern.search(response):
                        matches.append(entry)

                        if len(matches) >= limit:
                            break

        except Exception as e:
            console.print(f"[yellow]Warning: Error reading {log_file}: {e}[/yellow]")

        if len(matches) >= limit:
            break

    # Display results
    if not matches:
        console.print(f"[yellow]No conversations found matching: {query}[/yellow]")
        return

    console.print()
    console.print(f"[bold cyan]Found {len(matches)} matching conversation(s):[/bold cyan]")
    console.print()

    for match in matches:
        console.print(
            Panel(
                f"[bold]ID:[/bold] {match.get('conversation_id', 'Unknown')}\n"
                f"[bold]Adapter:[/bold] {match.get('adapter_name', 'Unknown')}\n"
                f"[bold]Model:[/bold] {match.get('model', 'Unknown')}\n"
                f"[bold]Timestamp:[/bold] {match.get('timestamp', 'Unknown')}\n"
                f"[bold]Prompt:[/bold] {match.get('prompt', '')[:200]}...",
                border_style="cyan",
            )
        )
        console.print()


@app.command()
def cleanup(
    days: int = typer.Option(
        30, "--days", "-d", help="Delete conversations older than this many days"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview without deleting"
    ),
):
    """Delete old conversation logs."""
    from cli_multi_rapid.logging.conversation_logger import ConversationLogger

    logger = ConversationLogger()

    if dry_run:
        console.print(
            f"[yellow]DRY RUN: Would delete conversations older than {days} days[/yellow]"
        )
        # TODO: Implement dry-run preview
        return

    # Confirm deletion
    confirm = typer.confirm(
        f"Delete conversation logs older than {days} days?",
        abort=True,
    )

    if confirm:
        deleted_count = logger.delete_old_conversations(days=days)
        console.print(
            f"[green]Deleted {deleted_count} old conversation log file(s)[/green]"
        )


@app.command()
def stats(
    date: Optional[str] = typer.Option(
        None, "--date", "-d", help="Show stats for specific date (YYYY-MM-DD)"
    ),
):
    """Show conversation statistics."""
    import json
    from collections import defaultdict

    from cli_multi_rapid.logging.conversation_logger import ConversationLogger

    logger = ConversationLogger()

    # Determine which log files to analyze
    if date:
        log_files = [logger.log_dir / f"{date}.jsonl"]
    else:
        log_files = sorted(logger.log_dir.glob("*.jsonl"))

    # Collect statistics
    stats_data = {
        "total_conversations": 0,
        "total_turns": 0,
        "by_adapter": defaultdict(int),
        "by_model": defaultdict(int),
        "total_prompt_length": 0,
        "total_response_length": 0,
    }

    conversation_ids = set()

    for log_file in log_files:
        if not log_file.exists() or log_file.name == ".gitkeep":
            continue

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    entry = json.loads(line)
                    conv_id = entry.get("conversation_id")

                    if conv_id:
                        conversation_ids.add(conv_id)

                    stats_data["total_turns"] += 1
                    stats_data["by_adapter"][entry.get("adapter_name", "Unknown")] += 1
                    stats_data["by_model"][entry.get("model", "Unknown")] += 1
                    stats_data["total_prompt_length"] += entry.get("prompt_length", 0)
                    stats_data["total_response_length"] += entry.get("response_length", 0)

        except Exception as e:
            console.print(f"[yellow]Warning: Error reading {log_file}: {e}[/yellow]")

    stats_data["total_conversations"] = len(conversation_ids)

    # Display statistics
    console.print()
    console.print(
        Panel(
            f"[bold]Total Conversations:[/bold] {stats_data['total_conversations']}\n"
            f"[bold]Total Turns:[/bold] {stats_data['total_turns']}\n"
            f"[bold]Avg Prompt Length:[/bold] {stats_data['total_prompt_length'] // max(stats_data['total_turns'], 1)}\n"
            f"[bold]Avg Response Length:[/bold] {stats_data['total_response_length'] // max(stats_data['total_turns'], 1)}",
            title="Conversation Statistics",
            border_style="cyan",
        )
    )
    console.print()

    # By adapter
    console.print("[bold cyan]By Adapter:[/bold cyan]")
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Adapter")
    table.add_column("Count", justify="right")

    for adapter, count in sorted(stats_data["by_adapter"].items(), key=lambda x: -x[1]):
        table.add_row(adapter, str(count))

    console.print(table)
    console.print()

    # By model
    console.print("[bold blue]By Model:[/bold blue]")
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Model")
    table.add_column("Count", justify="right")

    for model, count in sorted(stats_data["by_model"].items(), key=lambda x: -x[1]):
        table.add_row(model, str(count))

    console.print(table)
    console.print()


if __name__ == "__main__":
    app()
