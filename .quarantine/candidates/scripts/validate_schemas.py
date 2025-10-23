#!/usr/bin/env python3
"""
Validate repository YAML/JSON fixtures against schemas.

Currently validates:
- .ai/workflows/*.yaml against .ai/schemas/workflow.schema.json (if present)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def find_files(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pat in patterns:
        files.extend(Path(".").glob(pat))
    return [f for f in files if f.is_file()]


def validate_workflows() -> int:
    try:
        import jsonschema  # type: ignore
        import yaml  # type: ignore
    except Exception:
        print("jsonschema and PyYAML are required for schema validation", file=sys.stderr)
        return 2

    schema_path = Path(".ai/schemas/workflow.schema.json")
    if not schema_path.exists():
        print("No workflow schema found; skipping.")
        return 0

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = 0

    for wf_path in find_files([".ai/workflows/*.yaml", ".ai/workflows/*.yml"]):
        try:
            data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
            jsonschema.validate(data, schema)
            print(f"OK {wf_path}")
        except Exception as e:
            errors += 1
            print(f"FAIL {wf_path}: {e}", file=sys.stderr)

    return errors


def main() -> int:
    failures = 0
    failures += validate_workflows()
    return failures


if __name__ == "__main__":
    sys.exit(main())

