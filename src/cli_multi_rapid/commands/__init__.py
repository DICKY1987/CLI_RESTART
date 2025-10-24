"""CLI command modules."""

# Explicitly import command modules to make them available
# Legacy commands
# Phase 3 modular commands
from . import (
    cost_commands,
    git_commands,
    pr_commands,
    replay,
    repo_init,
    scripts,
    state,
    verify_commands,
    workflow_commands,
)

__all__ = [
    # Legacy commands
    "git_commands",
    "repo_init",
    "state",
    "scripts",
    "replay",
    # Phase 3 modular commands
    "workflow_commands",
    "verify_commands",
    "pr_commands",
    "cost_commands",
]
