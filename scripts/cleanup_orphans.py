from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


def list_stale_branches(days: int) -> list[str]:
    cutoff = time.time() - days * 86400
    out = subprocess.check_output(["git", "for-each-ref", "--format=%(refname:short)|%(committerdate:unix)", "refs/heads/"])  # nosec B603
    stale = []
    for line in out.decode().splitlines():
        name, ts = line.split("|")
        if float(ts) < cutoff and name not in {"main", "master"}:
            stale.append(name)
    return stale


def list_abandoned_locks(hours: int, base_dir: str = ".locks") -> list[Path]:
    cutoff = time.time() - hours * 3600
    p = Path(base_dir)
    if not p.exists():
        return []
    return [f for f in p.glob("*.lock") if f.stat().st_mtime < cutoff]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Do not make changes")
    ap.add_argument("--branch-days", type=int, default=7)
    ap.add_argument("--lock-hours", type=int, default=1)
    args = ap.parse_args()

    stale = list_stale_branches(args.branch_days)
    locks = list_abandoned_locks(args.lock_hours)

    for b in stale:
        print(f"Stale branch: {b}")
        if not args.dry_run:
            subprocess.check_call(["git", "branch", "-D", b])  # nosec B603

    for lf in locks:
        print(f"Abandoned lock: {lf}")
        if not args.dry_run:
            lf.unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

