import os
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config

from src.cli_multi_rapid.coordination.registry import (
    create_workstream,
    get_workstream,
    list_workstreams,
    update_status,
)


def _migrate(db_url: str) -> None:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", "alembic")
    command.upgrade(cfg, "head")


def test_workstream_lifecycle_and_queries() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "ws.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        os.environ["DATABASE_URL"] = db_url
        _migrate(db_url)

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

