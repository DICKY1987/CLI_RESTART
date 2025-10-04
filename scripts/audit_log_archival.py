from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Any, Optional


def load_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "active_days": 90,
            "archive_years": 7,
            "archive_dir": "artifacts/audit_archive",
            "cloud": {"provider": None},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def rotate_if_needed(log_file: Path, archive_dir: Path, active_days: int) -> Optional[Path]:
    if not log_file.exists():
        return None
    age_days = (dt.datetime.now() - dt.datetime.fromtimestamp(log_file.stat().st_mtime)).days
    if age_days < active_days:
        return None
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    archived = archive_dir / f"audit-{ts}.log"
    shutil.move(str(log_file), str(archived))
    ensure_dir(log_file.parent)
    log_file.touch(exist_ok=True)
    return archived


def prune_archives(archive_dir: Path, archive_years: int) -> int:
    cutoff = dt.datetime.now() - dt.timedelta(days=archive_years * 365)
    removed = 0
    if not archive_dir.exists():
        return 0
    for p in archive_dir.glob("audit-*.log"):
        try:
            mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
            if mtime < cutoff:
                p.unlink(missing_ok=True)
                removed += 1
        except Exception:
            continue
    return removed


def maybe_upload(_provider: Optional[str], _file: Path, _cfg: dict[str, Any]) -> None:
    return


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit log archival and retention")
    parser.add_argument("--log-file", default=str(Path("logs") / "audit" / "audit.log"))
    parser.add_argument("--policy", default=str(Path("config") / "audit_retention_policy.json"))
    args = parser.parse_args()

    log_file = Path(args.log_file)
    policy = load_policy(Path(args.policy))
    archive_dir = Path(policy.get("archive_dir", "artifacts/audit_archive"))
    active_days = int(policy.get("active_days", 90))
    archive_years = int(policy.get("archive_years", 7))

    ensure_dir(archive_dir)

    archived = rotate_if_needed(log_file, archive_dir, active_days)
    if archived is not None:
        cloud_cfg = policy.get("cloud") or {}
        provider = cloud_cfg.get("provider")
        try:
            maybe_upload(provider, archived, cloud_cfg)
        except Exception:
            pass

    removed = prune_archives(archive_dir, archive_years)
    print(json.dumps({
        "rotated": archived is not None,
        "archived_path": str(archived) if archived else None,
        "pruned_archives": removed,
        "archive_dir": str(archive_dir)
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
