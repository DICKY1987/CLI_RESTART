from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable, List


def run_parallel(tasks: Iterable[Callable[[], Any]], *, workers: int = 4) -> List[Any]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(t) for t in tasks]
        return [f.result() for f in as_completed(futures)]

