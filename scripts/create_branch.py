#!/usr/bin/env python
"""Automated branch naming and creation script."""

from __future__ import annotations

import re
import subprocess
import sys


def normalize_name(text: str) -> str:
    """Normalize text for branch name."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    # Remove leading/trailing hyphens
    return text.strip('-')


def create_branch(ticket_id: str, description: str, branch_type: str = "feature") -> str:
    """Create and checkout a conventionally named branch.

    Args:
        ticket_id: Ticket/issue ID (e.g., JIRA-123)
        description: Short description
        branch_type: Type of branch (feature, bugfix, hotfix)

    Returns:
        Branch name created
    """
    # Validate ticket ID format
    if not re.match(r'^[A-Z]+-\d+$', ticket_id, re.IGNORECASE):
        print(f"Warning: Ticket ID '{ticket_id}' doesn't match standard format (e.g., PROJ-123)")

    # Normalize description
    normalized_desc = normalize_name(description)[:50]  # Limit length

    # Construct branch name
    branch_name = f"{branch_type}/{ticket_id.upper()}-{normalized_desc}"

    try:
        # Create and checkout branch
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(f"✓ Created and checked out branch: {branch_name}")
        return branch_name
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create branch: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Create a conventionally named git branch")
    parser.add_argument("ticket_id", help="Ticket ID (e.g., PROJ-123)")
    parser.add_argument("description", help="Short branch description")
    parser.add_argument(
        "--type",
        choices=["feature", "bugfix", "hotfix", "chore"],
        default="feature",
        help="Branch type (default: feature)",
    )

    args = parser.parse_args()
    create_branch(args.ticket_id, args.description, args.type)


if __name__ == "__main__":
    main()
