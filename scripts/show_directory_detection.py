#!/usr/bin/env python3
"""
Helper script to show where the repository detects the local directory.

This script demonstrates how various components in the CLI Orchestrator
detect and use the repository root directory.
"""

import subprocess
import sys
from pathlib import Path


def detect_git_root() -> Path | None:
    """Detect git repository root using git command."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=False
        )
        top = (result.stdout or '').strip()
        if result.returncode == 0 and top:
            p = Path(top)
            if p.exists():
                return p
    except Exception as e:
        print(f"Error detecting git root: {e}", file=sys.stderr)
    return None


def main():
    """Display directory detection information."""
    print("=" * 70)
    print("CLI ORCHESTRATOR - DIRECTORY DETECTION")
    print("=" * 70)
    print()
    
    # Current working directory
    cwd = Path.cwd()
    print(f"Current Working Directory (Path.cwd()):")
    print(f"  {cwd}")
    print(f"  Absolute: {cwd.resolve()}")
    print()
    
    # Git repository root
    git_root = detect_git_root()
    if git_root:
        print(f"Git Repository Root (git rev-parse --show-toplevel):")
        print(f"  {git_root}")
        print(f"  Absolute: {git_root.resolve()}")
        print()
        
        if git_root.resolve() == cwd.resolve():
            print("✓ Current directory matches git repository root")
        else:
            print("⚠ Current directory differs from git repository root")
            rel_path = cwd.relative_to(git_root) if cwd.is_relative_to(git_root) else None
            if rel_path:
                print(f"  Current directory is: {git_root} / {rel_path}")
    else:
        print("✗ Not in a git repository (or git not available)")
        print("  Components will fall back to current working directory")
    
    print()
    print("=" * 70)
    print("COMPONENT DIRECTORY USAGE:")
    print("=" * 70)
    print()
    
    # Show how different components would use the directory
    components = [
        ("WorkflowRunner", "Uses Path.cwd() for relative paths"),
        ("WorkstreamExecutor", "Detects git root, falls back to Path.cwd()"),
        ("WorkflowOrchestrator", "Uses Path.cwd() as project_root"),
        ("PipelineScaffolder", "Accepts repo_root or defaults to Path.cwd()"),
    ]
    
    for name, behavior in components:
        print(f"• {name}")
        print(f"  {behavior}")
    
    print()
    print("=" * 70)
    print()
    
    # Check key directories existence
    key_dirs = [
        "src/cli_multi_rapid",
        "workflows",
        "config",
        ".ai/workflows",
        "tests",
    ]
    
    print("Key Directories Check:")
    print()
    base = git_root if git_root else cwd
    for dir_path in key_dirs:
        full_path = base / dir_path
        exists = "✓" if full_path.exists() else "✗"
        print(f"  {exists} {dir_path}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
