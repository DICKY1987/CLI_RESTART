from __future__ import annotations

"""FastAPI server exposing operational endpoints.

Provides `/health` and `/ready` for Kubernetes probes and supports graceful
shutdown via signal handlers.
"""

import asyncio
import signal
from typing import Callable

from fastapi import FastAPI

from cli_multi_rapid.config.validation import validate_and_build_settings
from src.api.health import router as health_router

app = FastAPI(title="CLI Multi-Rapid API")
app.include_router(health_router)


shutdown_callbacks: list[Callable[[], asyncio.Future]] = []


@app.on_event("startup")
async def on_startup() -> None:
    # Validate configuration at server startup
    validate_and_build_settings(None)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Run registered async cleanup callbacks
    for cb in shutdown_callbacks:
        try:
            await cb()
        except Exception:  # best-effort
            pass


def register_shutdown_callback(cb: Callable[[], asyncio.Future]) -> None:
    shutdown_callbacks.append(cb)


def _install_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    stop_event = asyncio.Event()

    def _handle_signal() -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_signal)
        except NotImplementedError:
            # Windows event loop may not support signal handlers
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

