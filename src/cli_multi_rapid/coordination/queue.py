from __future__ import annotations

import heapq
import itertools
from dataclasses import dataclass, field
from typing import Any

from src.cli_multi_rapid.coordination.registry import update_status

PRIORITY = {"high": 0, "medium": 1, "low": 2}


_counter = itertools.count()


@dataclass(order=True)
class _QItem:
    sort_index: tuple[int, int] = field(init=False)
    priority: str
    workstream_id: int
    task_name: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        self.sort_index = (PRIORITY[self.priority], next(_counter))


class PriorityQueue:
    def __init__(self) -> None:
        self._heap: list[_QItem] = []

    def put(self, workstream_id: int, task_name: str, payload: dict[str, Any] | None = None, priority: str = "medium") -> None:
        if priority not in PRIORITY:
            raise ValueError("invalid priority")
        heapq.heappush(self._heap, _QItem(priority=priority, workstream_id=workstream_id, task_name=task_name, payload=payload or {}))
        update_status(workstream_id, "pending")

    def get(self) -> _QItem:
        return heapq.heappop(self._heap)

    def empty(self) -> bool:
        return not self._heap

