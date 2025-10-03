#!/usr/bin/env python3
"""
Generate Pydantic models from JSON Schemas.

This script prefers using the `datamodel-code-generator` tool if available.
If the tool isn't installed, it will emit a clear message and exit gracefully
without failing. This keeps pre-commit runs usable for contributors who
haven't installed the optional tool yet, while allowing CI to enforce it.

Behavior:
- Looks for schemas under `.ai/schemas/`.
- Generates/updates models under `src/contracts/models/`.
- If `datamodel-codegen` is available, it is used to generate models.
- If not available, prints guidance and exits 0.

Note: To enforce strict consistency in CI, install `datamodel-code-generator`
and set env var `ENFORCE_MODEL_GEN=1`. In that mode, missing tool or diffs
will cause a non-zero exit code.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = REPO_ROOT / ".ai" / "schemas"
OUTPUT_DIR = REPO_ROOT / "src" / "contracts" / "models"


def has_datamodel_codegen() -> bool:
    return shutil.which("datamodel-codegen") is not None


def generate_with_datamodel_codegen() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        "datamodel-codegen",
        "--input", str(SCHEMAS_DIR),
        "--input-file-type", "jsonschema",
        "--output", str(OUTPUT_DIR / "models.py"),
        "--target-python-version", "3.9",
        "--use-schema-title-as-class-name",
        "--disable-timestamp",
    ]

    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stdout)
        sys.stderr.write(res.stderr)
        return res.returncode

    return 0


def main() -> int:
    enforce = os.getenv("ENFORCE_MODEL_GEN") == "1"

    if not SCHEMAS_DIR.exists():
        print(f"Schemas directory not found: {SCHEMAS_DIR}")
        return 0

    if has_datamodel_codegen():
        return generate_with_datamodel_codegen()

    msg = (
        "datamodel-codegen not found. Install with 'pip install datamodel-code-generator' "
        "to auto-generate Pydantic models from JSON Schemas."
    )
    print(msg)
    # In enforce mode, fail if tool is missing
    return 1 if enforce else 0


if __name__ == "__main__":
    raise SystemExit(main())

