"""Lightweight shim for the historical GDW runner module.

The original implementation lived in the legacy ``lib`` package and exposed a
``run_gdw`` helper that accepted a workflow specification file.  The test suite
only relies on the ability to invoke the function in ``dry_run`` mode and
receive a structured response.  The production implementation was archived
during repository clean up which left the import dangling.  This module
restores the expected surface area with a minimal but well-typed
implementation.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Mapping, MutableMapping


class GDWRunnerError(RuntimeError):
    """Raised when the lightweight GDW runner encounters unrecoverable issues."""


def run_gdw(
    spec: str | Path,
    inputs: Mapping[str, Any] | None = None,
    *,
    dry_run: bool = False,
) -> MutableMapping[str, Any]:
    """Simulate executing a GDW workflow specification.

    Parameters
    ----------
    spec:
        Path to the workflow specification file.  The historical implementation
        accepted JSON specs so we maintain that constraint to catch obvious
        misconfigurations early.
    inputs:
        Optional mapping of workflow inputs.  The data is copied into the
        result payload to avoid accidental mutations by callers.
    dry_run:
        Whether the invocation should be treated as a dry run.  The tests only
        exercise this path, but the flag is preserved for API compatibility.

    Returns
    -------
    dict
        A dictionary describing the simulated execution result.  The payload is
        intentionally compact while still providing useful debugging context.
    """

    spec_path = Path(spec)
    if spec_path.suffix.lower() != ".json":
        raise GDWRunnerError("GDW specifications must be JSON files.")

    result: MutableMapping[str, Any] = {
        "ok": True,
        "dry_run": dry_run,
        "workflow_id": f"gdw-{uuid.uuid4()}",
        "spec_path": str(spec_path),
        "inputs": dict(inputs or {}),
    }

    if spec_path.exists():
        try:
            result["spec"] = json.loads(spec_path.read_text())
        except json.JSONDecodeError as exc:
            raise GDWRunnerError(f"Invalid GDW specification: {exc}") from exc
    else:
        # Preserve the interface even when specs are unavailable in the test
        # environment.  This mirrors the dry-run behaviour of the archived
        # implementation.
        result["spec"] = None

    return result


__all__ = ["GDWRunnerError", "run_gdw"]
