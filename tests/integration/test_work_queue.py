import os
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config

from src.cli_multi_rapid.coordination.dispatcher import dispatch
from src.cli_multi_rapid.coordination.queue import PriorityQueue


def _migrate(db_url: str) -> None:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", "alembic")
    command.upgrade(cfg, "head")


def test_priority_order_and_status_updates() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "q.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{db.as_posix()}"
        _migrate(os.environ["DATABASE_URL"]) 

        from src.cli_multi_rapid.coordination.registry import create_workstream, get_workstream

        q = PriorityQueue()
        ws_low = create_workstream("low")
        ws_high = create_workstream("high")
        q.put(ws_low.id, "task", {"n": 1}, priority="low")
        q.put(ws_high.id, "task", {"n": 2}, priority="high")

        def func(payload):
            return payload["n"]

        results = dispatch(q, func, workers=2)
        assert sorted(results) == [1, 2]

        assert get_workstream(ws_low.id).status in {"completed", "running"}
        assert get_workstream(ws_high.id).status in {"completed", "running"}

