#!/bin/bash
# Quick script to create PR for ws-f-remaining-mods merge
# 
# Usage:
#   ./scripts/create_pr_ws_f.sh              # dry-run
#   ./scripts/create_pr_ws_f.sh --execute    # create PR
#

set -e

REPO="DICKY1987/CLI_RESTART"
TITLE="Merge ws-f-remaining-mods into main"
BODY="Open PR to merge ws-f-remaining-mods into main for review and CI validation."
HEAD="ws-f-remaining-mods"
BASE="main"

# Check if we should execute or dry-run
if [ "$1" = "--execute" ] || [ "$1" = "-x" ]; then
    MODE="execute"
else
    MODE="dry-run"
fi

echo "=================================="
echo "PR Creation for ws-f-remaining-mods"
echo "=================================="
echo ""
echo "Repository: $REPO"
echo "Title: $TITLE"
echo "Base: $BASE → Head: $HEAD"
echo "Mode: $MODE"
echo ""

# Check if Python script exists
if [ ! -f "scripts/create_pr_ws_f_remaining_mods.py" ]; then
    echo "Error: Python script not found"
    exit 1
fi

# Check for required tools
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Check for requests module
if ! python3 -c "import requests" &> /dev/null; then
    echo "Installing requests module..."
    pip install requests
fi

# Run the Python script
if [ "$MODE" = "execute" ]; then
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "Error: GITHUB_TOKEN not set"
        echo "Please set GITHUB_TOKEN environment variable:"
        echo "  export GITHUB_TOKEN=your_token_here"
        echo "  ./scripts/create_pr_ws_f.sh --execute"
        exit 1
    fi
    echo "Creating PR..."
    python3 scripts/create_pr_ws_f_remaining_mods.py
else
    echo "Running dry-run (use --execute to create PR)..."
    python3 scripts/create_pr_ws_f_remaining_mods.py --dry-run
fi

echo ""
echo "=================================="
echo "For more options, see:"
echo "  docs/guides/CREATE_PR_WS_F_REMAINING_MODS.md"
echo "=================================="
