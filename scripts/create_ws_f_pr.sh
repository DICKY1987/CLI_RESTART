#!/bin/bash
#
# Create PR for merging ws-f-build-system-consolidation into main
#
# This script creates a pull request using the GitHub CLI (gh).
# It requires GH_TOKEN or GITHUB_TOKEN to be set in the environment.
#
# Usage:
#   ./scripts/create_ws_f_pr.sh
#
# Or with explicit token:
#   GH_TOKEN=your_token ./scripts/create_ws_f_pr.sh
#

set -e

# PR details
REPO="DICKY1987/CLI_RESTART"
TITLE="Merge ws-f-build-system-consolidation into main"
BODY="Open PR to merge ws-f-build-system-consolidation into main for review and CI validation."
HEAD="ws-f-build-system-consolidation"
BASE="main"

echo "Creating pull request..."
echo "  Repository: $REPO"
echo "  Head: $HEAD"
echo "  Base: $BASE"
echo "  Title: $TITLE"
echo ""

# Check if gh is available
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Try to create the PR
if gh pr create \
    --repo "$REPO" \
    --title "$TITLE" \
    --body "$BODY" \
    --base "$BASE" \
    --head "$HEAD"; then
    echo ""
    echo "✓ Pull request created successfully!"
else
    echo ""
    echo "✗ Failed to create pull request."
    echo ""
    echo "Make sure you have:"
    echo "  1. GitHub CLI (gh) authenticated: gh auth login"
    echo "  2. Or GH_TOKEN/GITHUB_TOKEN environment variable set"
    echo "  3. Appropriate permissions for the repository"
    exit 1
fi
