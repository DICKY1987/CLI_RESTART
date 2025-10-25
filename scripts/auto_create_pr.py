#!/usr/bin/env python3
"""
Automated PR Creation Hook

This script is designed to be called by CI/CD or automation systems
to create the PR for merging ws-f-build-system-consolidation into main.

It can be triggered by:
1. A GitHub Actions workflow on merge
2. A webhook
3. Manual execution with proper credentials
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))


def check_pr_exists(github, repo, head, base):
    """Check if PR already exists."""
    try:
        prs = github.list_pull_requests(repo, state="open")
        for pr in prs:
            if pr.get("head", {}).get("ref") == head and pr.get("base", {}).get("ref") == base:
                return pr
        return None
    except Exception as e:
        print(f"Error checking existing PRs: {e}")
        return None


def main():
    """Main execution function."""
    from cli_multi_rapid.domain.github_client import GitHubClient
    
    # Configuration
    repo = "DICKY1987/CLI_RESTART"
    title = "Merge ws-f-build-system-consolidation into main"
    body = "Open PR to merge ws-f-build-system-consolidation into main for review and CI validation."
    head = "ws-f-build-system-consolidation"
    base = "main"
    
    # Initialize GitHub client
    github = GitHubClient()
    
    if not github.is_authenticated():
        print("❌ ERROR: No GitHub authentication token found")
        print()
        print("This script requires a GitHub token to be set via:")
        print("  - GITHUB_TOKEN environment variable")
        print("  - GH_TOKEN environment variable")
        print()
        print("In GitHub Actions, this is automatically available as:")
        print("  ${{ github.token }} or ${{ secrets.GITHUB_TOKEN }}")
        return False
    
    print(f"📋 PR Configuration:")
    print(f"   Repository: {repo}")
    print(f"   Head: {head}")
    print(f"   Base: {base}")
    print(f"   Title: {title}")
    print()
    
    # Check if PR already exists
    print("🔍 Checking for existing PR...")
    existing_pr = check_pr_exists(github, repo, head, base)
    
    if existing_pr:
        pr_number = existing_pr.get("number")
        pr_url = existing_pr.get("html_url")
        print(f"ℹ️  PR already exists: #{pr_number}")
        print(f"   URL: {pr_url}")
        print(f"   State: {existing_pr.get('state')}")
        return True
    
    # Create the PR
    print("🚀 Creating pull request...")
    try:
        response = github.create_pull_request(
            repo=repo,
            title=title,
            head=head,
            base=base,
            body=body,
            draft=False
        )
        
        if response and "number" in response:
            pr_number = response.get("number")
            pr_url = response.get("html_url")
            print()
            print(f"✅ Pull request created successfully!")
            print(f"   PR #{pr_number}")
            print(f"   URL: {pr_url}")
            print()
            
            # Save PR info to file for other automation
            pr_info = {
                "number": pr_number,
                "url": pr_url,
                "head": head,
                "base": base,
                "created_at": response.get("created_at"),
            }
            
            output_dir = repo_root / "artifacts"
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / "pr_created.json"
            
            with open(output_file, "w") as f:
                json.dump(pr_info, f, indent=2)
            
            print(f"📄 PR info saved to: {output_file}")
            return True
        else:
            print()
            print(f"❌ Failed to create pull request")
            if "message" in response:
                print(f"   Error: {response['message']}")
            if "errors" in response:
                for error in response['errors']:
                    print(f"   - {error}")
            return False
            
    except Exception as e:
        print()
        print(f"❌ Error creating PR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
