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


def make_alembic_config(db_url: str, ConfigCls) -> object:
    cfg = ConfigCls("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", "alembic")
    return cfg


def test_alembic_upgrade_and_downgrade_head(mock_alembic_command, mock_alembic_config) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        os.environ["DATABASE_URL"] = db_url
        cfg = make_alembic_config(db_url, _AlembicConfig or mock_alembic_config)

        cmd = _alembic_command or mock_alembic_command
        cmd.upgrade(cfg, "head")
        cmd.upgrade(cfg, "head")
        cmd.downgrade(cfg, "base")
