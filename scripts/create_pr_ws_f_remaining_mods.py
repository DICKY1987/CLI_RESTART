#!/usr/bin/env python3
"""
Create a Pull Request to merge ws-f-remaining-mods into main.

Usage:
  - With token from environment:
      GITHUB_TOKEN=... python scripts/create_pr_ws_f_remaining_mods.py
  - With explicit token:
      python scripts/create_pr_ws_f_remaining_mods.py --token YOUR_TOKEN
  - Dry-run (default):
      python scripts/create_pr_ws_f_remaining_mods.py --dry-run

This script creates a PR with:
  - Title: "Merge ws-f-remaining-mods into main"
  - Body: "Open PR to merge ws-f-remaining-mods into main for review and CI validation."
  - Base: main
  - Head: ws-f-remaining-mods
"""

import argparse
import json
import os
import sys

import requests


def get_token() -> str | None:
    """Get GitHub token from environment or command line."""
    return os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")


def gh_api_url(repo: str, endpoint: str) -> str:
    """Construct GitHub API URL."""
    return f"https://api.github.com/repos/{repo}{endpoint}"


def gh_headers(token: str | None) -> dict[str, str]:
    """Create headers for GitHub API requests."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def check_pr_exists(repo: str, token: str | None, head: str, base: str) -> dict | None:
    """Check if a PR already exists for the given head and base branches."""
    url = gh_api_url(repo, f"/pulls?state=all&head={head}&base={base}")
    try:
        r = requests.get(url, headers=gh_headers(token), timeout=30)
        r.raise_for_status()
        prs = r.json()
        if prs:
            return prs[0]  # Return the first (most recent) matching PR
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error checking existing PRs: {e}")
        return None


def create_pull_request(
    repo: str,
    token: str | None,
    title: str,
    body: str,
    head: str,
    base: str,
    dry_run: bool = True,
) -> dict | None:
    """Create a pull request on GitHub."""
    # Check if PR already exists
    existing_pr = check_pr_exists(repo, token, head, base)
    if existing_pr:
        pr_number = existing_pr["number"]
        pr_state = existing_pr["state"]
        pr_url = existing_pr["html_url"]
        print(f"✓ PR already exists: #{pr_number} ({pr_state})")
        print(f"  URL: {pr_url}")
        return existing_pr

    if dry_run:
        print("DRY RUN - Would create PR with:")
        print(f"  Repository: {repo}")
        print(f"  Title: {title}")
        print(f"  Base: {base}")
        print(f"  Head: {head}")
        print(f"  Body: {body}")
        return None

    url = gh_api_url(repo, "/pulls")
    payload = {
        "title": title,
        "body": body,
        "head": head,
        "base": base,
    }

    try:
        r = requests.post(
            url,
            headers=gh_headers(token),
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        pr_data = r.json()
        print(f"✓ Created PR #{pr_data['number']}")
        print(f"  URL: {pr_data['html_url']}")
        return pr_data
    except requests.exceptions.RequestException as e:
        print(f"✗ Error creating PR: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"  Response: {e.response.text}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Create a PR to merge ws-f-remaining-mods into main"
    )
    parser.add_argument(
        "--repo",
        default="DICKY1987/CLI_RESTART",
        help="GitHub repository (default: DICKY1987/CLI_RESTART)",
    )
    parser.add_argument(
        "--token",
        help="GitHub token (or use GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview without creating (default: False)",
    )
    parser.add_argument(
        "--title",
        default="Merge ws-f-remaining-mods into main",
        help="PR title",
    )
    parser.add_argument(
        "--body",
        default="Open PR to merge ws-f-remaining-mods into main for review and CI validation.",
        help="PR body/description",
    )
    parser.add_argument(
        "--head",
        default="ws-f-remaining-mods",
        help="Head branch (source)",
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch (target)",
    )

    args = parser.parse_args()

    # Get token from args or environment
    token = args.token or get_token()

    if not token and not args.dry_run:
        print("Error: GitHub token required. Set GITHUB_TOKEN env var or use --token")
        print("Use --dry-run to preview without authentication")
        sys.exit(1)

    # Create the PR
    result = create_pull_request(
        repo=args.repo,
        token=token,
        title=args.title,
        body=args.body,
        head=args.head,
        base=args.base,
        dry_run=args.dry_run,
    )

    if result is None and not args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
