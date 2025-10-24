#!/usr/bin/env python3
"""
Script to create a pull request for merging chore/update-submodule-aws-duplicate-workflows into main.

This script creates a PR from the chore/update-submodule-aws-duplicate-workflows branch
to the main branch for review and CI validation.

Usage:
    python scripts/create_pr_chore_aws_submodule.py [--dry-run]

Environment:
    GITHUB_TOKEN: Required GitHub personal access token with repo permissions
"""

import os
import sys
import argparse
import requests
from typing import Optional, Dict, Any


def get_github_token() -> str:
    """Get GitHub token from environment."""
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN or GH_TOKEN environment variable is required")
        print("Set it with: export GITHUB_TOKEN=<your_token>")
        sys.exit(1)
    return token


def check_branch_exists(owner: str, repo: str, branch: str, token: str) -> bool:
    """Check if a branch exists in the repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def check_existing_pr(owner: str, repo: str, head: str, base: str, token: str) -> Optional[Dict[str, Any]]:
    """Check if a PR already exists for the given head and base."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "head": f"{owner}:{head}",
        "base": base,
        "state": "open"
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        prs = response.json()
        return prs[0] if prs else None
    return None


def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str,
    token: str,
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """Create a pull request."""
    
    # Check if head branch exists
    if not check_branch_exists(owner, repo, head, token):
        print(f"❌ Error: Branch '{head}' does not exist")
        return None
    
    print(f"✓ Branch '{head}' exists")
    
    # Check if PR already exists
    existing_pr = check_existing_pr(owner, repo, head, base, token)
    if existing_pr:
        print(f"ℹ️  PR already exists: #{existing_pr['number']}")
        print(f"   URL: {existing_pr['html_url']}")
        return existing_pr
    
    if dry_run:
        print("\n🔍 DRY RUN - Would create PR with:")
        print(f"  Title: {title}")
        print(f"  Base: {base}")
        print(f"  Head: {head}")
        print(f"  Body: {body}")
        return None
    
    # Create the PR
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        pr = response.json()
        print(f"\n✓ Pull request created successfully!")
        print(f"  Number: #{pr['number']}")
        print(f"  URL: {pr['html_url']}")
        return pr
    else:
        print(f"\n❌ Failed to create PR: {response.status_code}")
        print(f"   {response.json().get('message', 'Unknown error')}")
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a PR for merging chore/update-submodule-aws-duplicate-workflows into main"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print PR details without creating it"
    )
    parser.add_argument(
        "--owner",
        default="DICKY1987",
        help="Repository owner (default: DICKY1987)"
    )
    parser.add_argument(
        "--repo",
        default="CLI_RESTART",
        help="Repository name (default: CLI_RESTART)"
    )
    
    args = parser.parse_args()
    
    # Configuration
    owner = args.owner
    repo = args.repo
    head_branch = "chore/update-submodule-aws-duplicate-workflows"
    base_branch = "main"
    title = "Merge chore/update-submodule-aws-duplicate-workflows into main"
    body = "Open PR to merge chore/update-submodule-aws-duplicate-workflows into main for review and CI validation."
    
    print(f"Creating PR for {owner}/{repo}")
    print(f"  From: {head_branch}")
    print(f"  To: {base_branch}\n")
    
    # Get GitHub token
    token = get_github_token()
    
    # Create PR
    create_pull_request(
        owner=owner,
        repo=repo,
        title=title,
        body=body,
        head=head_branch,
        base=base_branch,
        token=token,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
