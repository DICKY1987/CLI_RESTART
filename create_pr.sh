#!/bin/bash
# Script to create PR from ws-f-mods-applied to main
# Usage: ./create_pr.sh

set -e

REPO="DICKY1987/CLI_RESTART"
BASE="main"
HEAD="ws-f-mods-applied"
TITLE="WS-F: Build System Consolidation & Follow-up Modifications"

echo "Creating Pull Request..."
echo "Repository: $REPO"
echo "Base: $BASE"
echo "Head: $HEAD"
echo "Title: $TITLE"
echo ""

# Check if gh CLI is installed and authenticated
if command -v gh &> /dev/null; then
    echo "Using GitHub CLI (gh)..."
    
    # Check if authenticated
    if gh auth status &> /dev/null; then
        echo "✓ GitHub CLI is authenticated"
        
        # Create PR
        gh pr create \
            --repo "$REPO" \
            --base "$BASE" \
            --head "$HEAD" \
            --title "$TITLE" \
            --body-file PR_BODY.md
        
        echo "✓ Pull request created successfully!"
        exit 0
    else
        echo "✗ GitHub CLI is not authenticated"
        echo "Please run: gh auth login"
        exit 1
    fi
else
    echo "✗ GitHub CLI (gh) is not installed"
    echo ""
    echo "Alternative options:"
    echo "1. Install gh CLI: https://cli.github.com/"
    echo "2. Use the GitHub web UI: https://github.com/$REPO/compare/$BASE...$HEAD?expand=1"
    echo "3. Use curl with GITHUB_TOKEN (see CREATE_PR_INSTRUCTIONS.md)"
    exit 1
fi
