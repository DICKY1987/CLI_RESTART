import os
import tempfile
from pathlib import Path

import pytest

# Alembic may not be installed/configured in unit environments
try:
    from alembic import command as _alembic_command  # type: ignore
    from alembic.config import Config as _AlembicConfig  # type: ignore
    ALEMBIC_AVAILABLE = True
except Exception:  # pragma: no cover - defensive for test envs
    _alembic_command = None
    _AlembicConfig = None
    ALEMBIC_AVAILABLE = False

from scripts.backup_utils import backup_database, restore_database
from src.cli_multi_rapid.coordination.registry import create_workstream, get_workstream


def _get_alembic_command(fallback):
    # Always use fallback mock in unit tests to avoid real Alembic side effects
    return fallback


def _get_alembic_config(fallback):
    return fallback


def _migrate(db_url: str, command_mod, ConfigCls) -> None:
    cfg = ConfigCls("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", "alembic")
    command_mod.upgrade(cfg, "head")


def test_backup_and_restore_sqlite(mock_alembic_command, mock_alembic_config) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "bk.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        os.environ["DATABASE_URL"] = db_url
        cmd = _get_alembic_command(mock_alembic_command)
        cfg_cls = _get_alembic_config(mock_alembic_config)
        _migrate(db_url, cmd, cfg_cls)

        ws = create_workstream("to-backup")
        assert ws.id is not None

        backup_file = backup_database(db_url, str(Path(tmp) / "backups"))

        db_path.unlink()

        restore_database(db_url, str(backup_file))
        fetched = get_workstream(ws.id)
        assert fetched is not None and fetched.name == "to-backup"
