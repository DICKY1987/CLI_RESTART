from __future__ import annotations

import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

try:
    # Optional import to allow tests to release SQLite file handles
    from src.db.connection import get_engine  # type: ignore
except Exception:  # pragma: no cover
    get_engine = None  # type: ignore


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def backup_database(database_url: str, dest_dir: str) -> Path:
    parsed = urlparse(database_url)
    dest = Path(dest_dir)
    _ensure_dir(dest)
    if parsed.scheme.startswith("sqlite"):
        p = parsed.path
        # On Windows, URLs may look like /C:/path/to/db.db; strip leading slash
        if os.name == "nt" and p.startswith("/") and len(p) > 2 and p[2] == ":":
            p = p.lstrip("/")
        db_path = Path(p)
        if not db_path.exists():
            raise FileNotFoundError(f"SQLite DB not found: {db_path}")
        out = dest / f"sqlite-backup-{db_path.stem}.db"
        shutil.copy2(db_path, out)
        # On SQLite/Windows, dispose engine to release file handle for callers
        try:
            if get_engine:
                get_engine().dispose()
        except Exception:
            pass
        return out
    raise NotImplementedError("Only SQLite backup is implemented in utils; use pg_dump for Postgres")


def restore_database(database_url: str, backup_file: str) -> None:
    parsed = urlparse(database_url)
    if parsed.scheme.startswith("sqlite"):
        p = parsed.path
        if os.name == "nt" and p.startswith("/") and len(p) > 2 and p[2] == ":":
            p = p.lstrip("/")
        db_path = Path(p)
        src = Path(backup_file)
        shutil.copy2(src, db_path)
        return
    raise NotImplementedError("Only SQLite restore is implemented in utils; use psql/pg_restore for Postgres")
