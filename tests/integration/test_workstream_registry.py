import os
import tempfile
from pathlib import Path

import pytest

try:
    from alembic import command as _alembic_command  # type: ignore
    from alembic.config import Config as _AlembicConfig  # type: ignore
    ALEMBIC_AVAILABLE = True
except Exception:  # pragma: no cover
    _alembic_command = None
    _AlembicConfig = None
    ALEMBIC_AVAILABLE = False

from src.cli_multi_rapid.coordination.registry import (
    create_workstream,
    get_workstream,
    list_workstreams,
    update_status,
)


def _migrate(db_url: str, command_mod, ConfigCls) -> None:
    cfg = ConfigCls("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", "alembic")
    command_mod.upgrade(cfg, "head")


def _get_alembic_command(fallback):
    return fallback


def _get_alembic_config(fallback):
    return fallback


def test_workstream_lifecycle_and_queries(mock_alembic_command, mock_alembic_config) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "ws.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        os.environ["DATABASE_URL"] = db_url
        cmd = _get_alembic_command(mock_alembic_command)
        cfg_cls = _get_alembic_config(mock_alembic_config)
        _migrate(db_url, cmd, cfg_cls)

        ws = create_workstream("ws-a", metadata={"k": "v"}, correlation_id="corr-1")
        assert ws.id is not None

        ws2 = update_status(ws.id, "running")
        assert ws2.status == "running"

        fetched = get_workstream(ws.id)
        assert fetched is not None and fetched.name == "ws-a"

        all_ws = list_workstreams()
        assert any(w.id == ws.id for w in all_ws)

        running = list_workstreams(status="running")
        assert len(running) == 1 and running[0].id == ws.id

        by_corr = list_workstreams(correlation_id="corr-1")
        assert len(by_corr) == 1 and by_corr[0].id == ws.id
