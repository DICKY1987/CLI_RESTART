#!/usr/bin/env python3
"""
Cancellation utilities.

Provides a simple file-based cancellation token consumed by adapters.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


class CancellationToken:
    """Simple file-based cancellation token.

    If a file named `.cancel` exists in the project root, `is_cancelled()` returns True.
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or Path(".cancel")

    def is_cancelled(self) -> bool:
        try:
            return self._path.exists()
        except Exception:
            return False

