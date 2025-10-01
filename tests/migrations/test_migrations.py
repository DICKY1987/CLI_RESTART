import os
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config


def make_alembic_config(db_url: str) -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", "alembic")
    return cfg


def test_alembic_upgrade_and_downgrade_head() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        os.environ["DATABASE_URL"] = db_url
        cfg = make_alembic_config(db_url)

        command.upgrade(cfg, "head")
        command.upgrade(cfg, "head")
        command.downgrade(cfg, "base")

