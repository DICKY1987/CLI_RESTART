from __future__ import annotations

import shutil
from pathlib import Path
from urllib.parse import urlparse


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def backup_database(database_url: str, dest_dir: str) -> Path:
    parsed = urlparse(database_url)
    dest = Path(dest_dir)
    _ensure_dir(dest)
    if parsed.scheme.startswith("sqlite"):
        db_path = Path(parsed.path)
        if db_path.drive == "":
            db_path = Path(".") / db_path.relative_to("/")
        if not db_path.exists():
            raise FileNotFoundError(f"SQLite DB not found: {db_path}")
        out = dest / f"sqlite-backup-{db_path.stem}.db"
        shutil.copy2(db_path, out)
        return out
    raise NotImplementedError("Only SQLite backup is implemented in utils; use pg_dump for Postgres")


def restore_database(database_url: str, backup_file: str) -> None:
    parsed = urlparse(database_url)
    if parsed.scheme.startswith("sqlite"):
        db_path = Path(parsed.path)
        if db_path.drive == "":
            db_path = Path(".") / db_path.relative_to("/")
        src = Path(backup_file)
        shutil.copy2(src, db_path)
        return
    raise NotImplementedError("Only SQLite restore is implemented in utils; use psql/pg_restore for Postgres")

