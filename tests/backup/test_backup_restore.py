import os
import tempfile
from pathlib import Path

from alembic.config import Config

from alembic import command
from scripts.backup_utils import backup_database, restore_database
from src.cli_multi_rapid.coordination.registry import create_workstream, get_workstream


def _migrate(db_url: str) -> None:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", "alembic")
    command.upgrade(cfg, "head")


def test_backup_and_restore_sqlite() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "bk.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        os.environ["DATABASE_URL"] = db_url
        _migrate(db_url)

        ws = create_workstream("to-backup")
        assert ws.id is not None

        backup_file = backup_database(db_url, str(Path(tmp) / "backups"))

        db_path.unlink()

        restore_database(db_url, str(backup_file))
        fetched = get_workstream(ws.id)
        assert fetched is not None and fetched.name == "to-backup"

