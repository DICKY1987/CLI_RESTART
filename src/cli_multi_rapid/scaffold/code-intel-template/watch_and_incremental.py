from __future__ import annotations

import argparse
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = (HERE / "..").resolve()


def file_snapshot(root: Path) -> dict[str, float]:
    snap: dict[str, float] = {}
    for p in root.rglob("*"):
        if p.is_file():
            try:
                snap[p.as_posix()] = p.stat().st_mtime
            except Exception:
                pass
    return snap


def rebuild() -> None:
    import subprocess, sys
    subprocess.run([sys.executable, str(HERE / "build_index.py")], check=False)


def main() -> None:
    ap = argparse.ArgumentParser(description="Incremental index updater (polling)")
    ap.add_argument("--interval", type=float, default=2.0, help="Polling interval seconds")
    args = ap.parse_args()

    last = file_snapshot(ROOT)
    print("watch: initial snapshot")
    while True:
        time.sleep(args.interval)
        cur = file_snapshot(ROOT)
        if cur.keys() != last.keys():
            print("watch: file added/removed -> rebuild")
            rebuild()
            last = cur
            continue
        changed = [p for p in cur if cur[p] != last.get(p)]
        if changed:
            print(f"watch: {len(changed)} changed -> rebuild")
            rebuild()
            last = cur


if __name__ == "__main__":
    main()

