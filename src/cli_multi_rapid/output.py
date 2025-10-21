"""Output formatting for CLI commands with JSON and Rich console support."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


class OutputFormatter:
    """Handles output formatting for CLI commands."""

    def __init__(self, json_mode: bool = False):
        """Initialize output formatter.

        Args:
            json_mode: If True, output JSON. If False, use Rich console formatting.
        """
        self.json_mode = json_mode
        self.console = Console() if not json_mode else None

    def print(self, message: str, style: str | None = None):
        """Print a message.

        Args:
            message: Message to print
            style: Rich style string (ignored in JSON mode)
        """
        if self.json_mode:
            self._json_output({"type": "message", "content": message})
        else:
            self.console.print(message, style=style)

    def print_success(self, message: str):
        """Print a success message."""
        if self.json_mode:
            self._json_output({"type": "success", "message": message})
        else:
            self.console.print(f"✓ {message}", style="bold green")

    def print_error(self, message: str, error: Exception | None = None):
        """Print an error message."""
        data: dict[str, Any] = {"type": "error", "message": message}
        if error:
            data["error_type"] = type(error).__name__
            data["error_details"] = str(error)

        if self.json_mode:
            self._json_output(data)
        else:
            self.console.print(f"✗ {message}", style="bold red")
            if error:
                self.console.print(f"  {error}", style="red")

    def print_warning(self, message: str):
        """Print a warning message."""
        if self.json_mode:
            self._json_output({"type": "warning", "message": message})
        else:
            self.console.print(f"⚠ {message}", style="bold yellow")

    def print_info(self, message: str):
        """Print an info message."""
        if self.json_mode:
            self._json_output({"type": "info", "message": message})
        else:
            self.console.print(f"ℹ {message}", style="bold blue")

    def print_result(self, result: dict[str, Any]):
        """Print a structured result."""
        if self.json_mode:
            self._json_output({"type": "result", "data": result})
        else:
            panel = Panel.fit(
                json.dumps(result, indent=2),
                title="Result",
                border_style="green",
            )
            self.console.print(panel)

    def print_table(self, title: str, columns: list[str], rows: list[list[Any]]):
        """Print a table.

        Args:
            title: Table title
            columns: Column headers
            rows: Table rows
        """
        if self.json_mode:
            self._json_output({
                "type": "table",
                "title": title,
                "columns": columns,
                "rows": rows,
            })
        else:
            table = Table(title=title)
            for col in columns:
                table.add_column(col, style="cyan")
            for row in rows:
                table.add_row(*[str(cell) for cell in row])
            self.console.print(table)

    def print_code(self, code: str, language: str = "python", title: str | None = None):
        """Print syntax-highlighted code.

        Args:
            code: Source code to display
            language: Programming language for syntax highlighting
            title: Optional title
        """
        if self.json_mode:
            self._json_output({
                "type": "code",
                "language": language,
                "content": code,
                "title": title,
            })
        else:
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            if title:
                panel = Panel(syntax, title=title, border_style="blue")
                self.console.print(panel)
            else:
                self.console.print(syntax)

    def print_list(self, items: list[str], title: str | None = None):
        """Print a list of items.

        Args:
            items: List items to display
            title: Optional title
        """
        if self.json_mode:
            self._json_output({"type": "list", "items": items, "title": title})
        else:
            if title:
                self.console.print(f"\n[bold]{title}[/bold]")
            for item in items:
                self.console.print(f"  • {item}")

    def _json_output(self, data: dict[str, Any]):
        """Output JSON to stdout."""
        json.dump(data, sys.stdout)
        sys.stdout.write("\n")
        sys.stdout.flush()


# Global formatter instance
_formatter: OutputFormatter | None = None


def init_formatter(json_mode: bool = False):
    """Initialize global formatter."""
    global _formatter
    _formatter = OutputFormatter(json_mode=json_mode)


def get_formatter() -> OutputFormatter:
    """Get global formatter instance."""
    if _formatter is None:
        init_formatter()
    return _formatter
