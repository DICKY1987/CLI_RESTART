#!/usr/bin/env python3
"""
Create Pull Request Script

Creates a pull request to merge ws-f-build-system-consolidation into main.
Uses GitHub API for PR creation.

Usage:
    # With GITHUB_TOKEN environment variable
    export GITHUB_TOKEN=your_token
    python scripts/create_pr.py
    
    # Or pass token as argument
    python scripts/create_pr.py <github_token>
    
    # In GitHub Actions, GITHUB_TOKEN should be available automatically
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from cli_multi_rapid.domain.github_client import GitHubClient


def create_pr(token=None):
    """Create a pull request to merge ws-f-build-system-consolidation into main."""
    
    # Get token from argument, environment, or prompt
    if token is None:
        token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        print("Error: GitHub token not found!")
        print()
        print("Please provide a GitHub token via:")
        print("  1. Environment variable: export GITHUB_TOKEN=your_token")
        print("  2. Command argument: python scripts/create_pr.py <token>")
        print()
        print("To create a token:")
        print("  https://github.com/settings/tokens/new")
        print("  Required scopes: repo")
        return None, None
    
    # Initialize GitHub client with token
    github = GitHubClient(token=token)
    
    # PR details
    owner = "DICKY1987"
    repo = "CLI_RESTART"
    title = "Merge ws-f-build-system-consolidation into main"
    body = "Open PR to merge ws-f-build-system-consolidation into main for review and CI validation."
    head = "ws-f-build-system-consolidation"
    base = "main"
    
    print(f"Creating PR: {title}")
    print(f"  Repository: {owner}/{repo}")
    print(f"  Head: {head}")
    print(f"  Base: {base}")
    print()
    
    try:
        # Create the PR using GitHub API
        repo_full = f"{owner}/{repo}"
        
        response = github.create_pull_request(
            repo=repo_full,
            title=title,
            head=head,
            base=base,
            body=body,
            draft=False
        )
        
        if response and "number" in response:
            pr_number = response.get("number")
            pr_url = response.get("html_url")
            print(f"✓ Pull request #{pr_number} created successfully!")
            print(f"  URL: {pr_url}")
            return pr_number, pr_url
        else:
            print("✗ Failed to create pull request")
            if "message" in response:
                print(f"  Error: {response['message']}")
            return None, None
            
    except Exception as e:
        print(f"✗ Error creating PR: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    # Get token from command line argument if provided
    token = sys.argv[1] if len(sys.argv) > 1 else None
    pr_number, pr_url = create_pr(token)
    sys.exit(0 if pr_number else 1)
