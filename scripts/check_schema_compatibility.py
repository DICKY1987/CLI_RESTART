from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _load_json(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _git_show(path: str, ref: str) -> Dict[str, Any] | None:
    try:
        out = subprocess.check_output(["git", "show", f"{ref}:{path}"])  # nosec B603
    except subprocess.CalledProcessError:
        return None
    return json.loads(out.decode("utf-8"))


def compare_schemas(base: Dict[str, Any], curr: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    base_required = set(base.get("required", []))
    curr_required = set(curr.get("required", []))
    removed_required = base_required - curr_required
    if removed_required:
        reasons.append(f"Removed required: {sorted(removed_required)}")

    base_props = base.get("properties", {}) or {}
    curr_props = curr.get("properties", {}) or {}
    for name, bprop in base_props.items():
        if name in curr_props:
            btype = bprop.get("type")
            ctype = curr_props[name].get("type")
            if btype and ctype and btype != ctype:
                reasons.append(f"Changed type of '{name}' from {btype} to {ctype}")

    return (len(reasons) == 0, reasons)


def ensure_schema_headers(schema: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    if "$schema" not in schema:
        errs.append("missing $schema")
    if "version" not in schema:
        errs.append("missing version")
    return errs


def main(argv: List[str]) -> int:
    base_ref = "origin/main"
    root = Path(__file__).resolve().parents[1]
    schemas_dir = root / ".ai" / "schemas"
    changed = []
    try:
        diff = subprocess.check_output(["git", "diff", "--name-only", f"{base_ref}...HEAD"])  # nosec B603
        changed = [l.strip() for l in diff.decode("utf-8").splitlines() if l.strip().endswith(".json")]
    except Exception:
        pass

    failures: List[str] = []
    for path in schemas_dir.glob("*.json"):
        schema = _load_json(path)
        header_errs = ensure_schema_headers(schema)
        if header_errs:
            failures.append(f"{path}: {'; '.join(header_errs)}")
            continue

        rel = str(path).replace(str(root) + "\\", "").replace(str(root) + "/", "")
        if not changed or rel in changed:
            base = _git_show(rel, base_ref)
            if base is None:
                continue
            compatible, reasons = compare_schemas(base, schema)
            if not compatible and schema.get("version") == base.get("version"):
                failures.append(f"{path}: breaking change without version bump: {', '.join(reasons)}")

    if failures:
        for f in failures:
            print(f)
        return 1
    print("Schema compatibility checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

