#!/bin/bash
# Wrapper script to create PR for merging chore/update-submodule-aws-duplicate-workflows into main
# Usage: ./scripts/create-pr.sh [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ] && [ -z "$GH_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN or GH_TOKEN environment variable is required"
    echo ""
    echo "Set it with:"
    echo "  export GITHUB_TOKEN=<your_token>"
    echo ""
    echo "Or use GitHub CLI (if authenticated):"
    echo "  gh pr create --repo DICKY1987/CLI_RESTART \\"
    echo "    --base main \\"
    echo "    --head chore/update-submodule-aws-duplicate-workflows \\"
    echo "    --title 'Merge chore/update-submodule-aws-duplicate-workflows into main' \\"
    echo "    --body 'Open PR to merge chore/update-submodule-aws-duplicate-workflows into main for review and CI validation.'"
    exit 1
fi

# Run the Python script
cd "$REPO_ROOT"
python3 scripts/create_pr_chore_aws_submodule.py "$@"
