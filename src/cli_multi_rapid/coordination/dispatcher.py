from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List

from .queue import PriorityQueue, _QItem
from .worker import run_task


def dispatch(queue: PriorityQueue, func: Callable[[dict[str, Any]], Any], *, workers: int = 4) -> List[Any]:
    results: List[Any] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = []
        while not queue.empty():
            item: _QItem = queue.get()
            futures.append(pool.submit(run_task, item.workstream_id, func, item.payload))
        for fut in as_completed(futures):
            results.append(fut.result())
    return results

