#!/usr/bin/env python3
"""
Validate that .env example contains environment variables referenced in code.

Checks:
- Greps for os.getenv usage across src/
- Reports variables missing from the provided env file
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Set

CODE_DIR = Path(__file__).resolve().parents[1] / "src"


GETENV_RE = re.compile(r"os\.getenv\(\s*['\"]([A-Z0-9_]+)['\"])"
)


def find_env_vars_in_code(root: Path) -> Set[str]:
    found: Set[str] = set()
    for path in root.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in GETENV_RE.finditer(text):
            found.add(m.group(1))
    # Common env keys used by Settings models / runtime
    found.update({
        "CLI_ENV", "CLI_ORCHESTRATOR_ENV", "ENVIRONMENT",
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
        "REDIS_URL",
    })
    return found


def parse_env_file(path: Path) -> Set[str]:
    keys: Set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k = line.split("=", 1)[0].strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k):
                keys.add(k)
    return keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", type=Path, default=Path(".env.example"))
    args = ap.parse_args()

    code_vars = find_env_vars_in_code(CODE_DIR)
    env_vars = parse_env_file(args.check)

    missing = sorted(v for v in code_vars if v not in env_vars)
    if missing:
        print("Missing variables in env file:")
        for v in missing:
            print(f"  - {v}")
        return 1
    print("OK: env example contains all referenced variables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

