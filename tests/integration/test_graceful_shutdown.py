import asyncio
import pytest

from cli_multi_rapid.shutdown import GracefulShutdown


@pytest.mark.asyncio
async def test_graceful_shutdown_runs_callbacks():
    gs = GracefulShutdown(timeout_seconds=1.0)

    called = []

    async def cb():
        called.append(True)

    gs.register(cb)
    # Directly call shutdown rather than sending OS signals
    await gs.shutdown()
    assert called == [True]

