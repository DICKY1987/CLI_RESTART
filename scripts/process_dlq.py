from __future__ import annotations

import argparse

from src.cli_multi_rapid.resilience.dlq import FileDLQ


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    dlq = FileDLQ()
    if args.list:
        for item in dlq.list():
            print(f"{item.timestamp} {item.workflow}: {item.reason} (retries={item.retries})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

