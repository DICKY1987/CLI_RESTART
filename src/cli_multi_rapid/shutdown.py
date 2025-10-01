from __future__ import annotations

"""Graceful shutdown utilities for CLI and server contexts."""

import asyncio
import signal
from typing import Awaitable, Callable, List


class GracefulShutdown:
    def __init__(self, timeout_seconds: float = 15.0) -> None:
        self._callbacks: List[Callable[[], Awaitable[None]]] = []
        self._timeout = timeout_seconds
        self._stop = asyncio.Event()

    def register(self, cb: Callable[[], Awaitable[None]]) -> None:
        self._callbacks.append(cb)

    async def wait(self) -> None:
        await self._stop.wait()

    def install_signal_handlers(self) -> None:
        loop = asyncio.get_event_loop()

        def _trigger() -> None:
            self._stop.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _trigger)
            except NotImplementedError:
                # Windows compatibility
                pass

    async def shutdown(self) -> None:
        async def _run_cb(cb: Callable[[], Awaitable[None]]) -> None:
            try:
                await cb()
            except Exception:
                pass

        tasks = [asyncio.create_task(_run_cb(cb)) for cb in self._callbacks]
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=self._timeout)
        except asyncio.TimeoutError:
            # Best-effort cleanup; let process exit
            pass

