from __future__ import annotations

from typing import Any, Callable

from src.cli_multi_rapid.coordination.registry import update_status


def run_task(workstream_id: int, func: Callable[[dict[str, Any]], Any], payload: dict[str, Any]) -> Any:
    try:
        update_status(workstream_id, "running")
        result = func(payload)
        update_status(workstream_id, "completed")
        return result
    except Exception:
        update_status(workstream_id, "failed")
        raise

