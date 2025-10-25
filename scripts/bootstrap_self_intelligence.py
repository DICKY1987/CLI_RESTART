from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def repo_root(start: Path) -> Path:
    p = start.resolve()
    for _ in range(10):
        if (p / ".git").exists() or (p / "pyproject.toml").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return start.resolve()


def main() -> None:
    here = Path(__file__).resolve()
    root = repo_root(here)
    tmpl = root / "templates" / "code-intel-template"
    dst = root / ".code-intel"

    if dst.exists():
        print(".code-intel already exists; refreshing config/scripts")
        # Refresh non-generated files
        for name in [
            "config.json",
            "ignore_globs.txt",
            "chunk_rules.yaml",
            "build_index.py",
            "retrieve.py",
            "ask_deepseek.py",
            "watch_and_incremental.py",
            "build_index.ps1",
            "retrieve.ps1",
            "ask_deepseek.ps1",
            "watch_and_incremental.ps1",
        ]:
            shutil.copy2(tmpl / name, dst / name)
    else:
        print("Creating .code-intel from template")
        shutil.copytree(tmpl, dst)
        (dst / "db").mkdir(parents=True, exist_ok=True)
        (dst / "cache").mkdir(parents=True, exist_ok=True)

    # Ensure .gitignore entries
    gi = root / ".gitignore"
    lines = []
    if gi.exists():
        lines = gi.read_text(encoding="utf-8").splitlines()
    for a in [".code-intel/db/", ".code-intel/cache/"]:
        if a not in lines:
            lines.append(a)
    gi.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Build index
    print("Building index for orchestrator repo...")
    subprocess.run([sys.executable, str(dst / "build_index.py")], cwd=root, check=False)
    print("Done.")


if __name__ == "__main__":
    main()

