#!/usr/bin/env python3
"""
Unified output formatting for CLI commands.

Provides JSON output when requested and rich console output otherwise.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional

from rich.console import Console


class OutputFormatter:
    def __init__(self, json_mode: bool = False, console: Optional[Console] = None) -> None:
        self.json_mode = json_mode
        self.console = console or Console()

    def emit(self, obj: Any, fallback_text: Optional[str] = None, exit_code: Optional[int] = None) -> int:
        """Emit an object as JSON or rich text. Returns suggested exit code (default 0)."""
        if self.json_mode:
            try:
                payload = obj
                if is_dataclass(obj):
                    payload = asdict(obj)  # type: ignore[arg-type]
                self.console.print_json(data=payload)
                return int(exit_code or 0)
            except Exception:
                # Fallback to basic dumps to ensure machine-readable output
                self.console.print(json.dumps({"result": obj}, default=str))
                return int(exit_code or 0)
        # Rich text mode
        if isinstance(obj, str):
            self.console.print(obj)
        else:
            try:
                self.console.print_json(data=obj)  # pretty print if structured
            except Exception:
                self.console.print(fallback_text or str(obj))
        return int(exit_code or 0)

    def error(self, message: str, details: Optional[Dict[str, Any]] = None) -> int:
        payload: Dict[str, Any] = {"success": False, "error": message}
        if details:
            payload["details"] = details
        return self.emit(payload if self.json_mode else f"[red]ERROR[/red] {message}")

