#!/usr/bin/env python3
"""
Setup Tool Environment (session-oriented)

Reads config/tool_adapters.yaml and prints a JSON summary of:
- env: environment variables to set (from tool_config.*.env)
- resolved_tools: tool name -> {path, version}

Intended to be called by a thin PowerShell wrapper that applies the env and
prints a status table.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    print(json.dumps({"error": "PyYAML not available"}))
    raise SystemExit(1)


def _run_version(cmd: str) -> str:
    try:
        parts = shlex.split(cmd, posix=os.name != "nt")
        # Try common flags
        for flag in ("--version", "version", "-v"):
            p = subprocess.run(parts + [flag], capture_output=True, text=True, timeout=5)
            out = (p.stdout or p.stderr or "").strip()
            if p.returncode == 0 and out:
                return out.splitlines()[0][:200]
        return ""
    except Exception:
        return ""


def main() -> None:
    cfg_path = Path("config") / "tool_adapters.yaml"
    data: Dict[str, Any] = {}
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    env_to_set: Dict[str, str] = {}
    tool_envs = (data.get("tool_config") or {})
    for _tool, td in tool_envs.items():
        env = (td or {}).get("env") or {}
        for k, v in env.items():
            if isinstance(k, str) and isinstance(v, str):
                env_to_set[k] = v

    # Resolve tool commands from paths mapping (names -> command)
    resolved: Dict[str, Dict[str, str]] = {}
    for name, exe in (data.get("paths") or {}).items():
        if not isinstance(exe, str):
            continue
        # Use where/which to resolve path
        try:
            if os.name == "nt":
                p = subprocess.run(["where", exe], capture_output=True, text=True, timeout=5)
            else:
                p = subprocess.run(["which", exe], capture_output=True, text=True, timeout=5)
            path = p.stdout.splitlines()[0].strip() if p.returncode == 0 and p.stdout else ""
        except Exception:
            path = ""
        version = _run_version(exe)
        resolved[name] = {"path": path, "version": version}

    print(json.dumps({"env": env_to_set, "resolved_tools": resolved}, indent=2))


if __name__ == "__main__":
    main()

