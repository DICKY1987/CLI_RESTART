# Creating PR to Merge ws-f-remaining-mods into main

This document describes how to create a pull request to merge the `ws-f-remaining-mods` branch into `main` for review and CI validation.

## Overview

The `ws-f-remaining-mods` branch contains important updates including:
- Makefile consolidation and build system improvements
- Lint fixes (Ruff, mypy improvements)
- Code cleanup and documentation updates  
- CI/CD enhancements
- Script deduplication

## Methods to Create the PR

### Method 1: GitHub Actions Workflow (Recommended)

The easiest way is to use the provided GitHub Actions workflow:

1. Navigate to the repository on GitHub: https://github.com/DICKY1987/CLI_RESTART
2. Go to **Actions** tab
3. Select **"Create PR for ws-f-remaining-mods"** workflow from the left sidebar
4. Click **"Run workflow"** button
5. Choose options:
   - **Dry run**: Check this to preview without creating (recommended first run)
   - Leave unchecked to actually create the PR
6. Click **"Run workflow"**

### Method 2: Python Script (Manual)

If you prefer to run the script manually with a GitHub token:

```bash
# Dry run (preview without creating)
python scripts/create_pr_ws_f_remaining_mods.py --dry-run

# Create the PR (requires GITHUB_TOKEN)
GITHUB_TOKEN=your_token_here python scripts/create_pr_ws_f_remaining_mods.py
```

#### Script Options

```bash
# Full usage
python scripts/create_pr_ws_f_remaining_mods.py \
  --repo DICKY1987/CLI_RESTART \
  --title "Merge ws-f-remaining-mods into main" \
  --body "Open PR to merge ws-f-remaining-mods into main for review and CI validation." \
  --head ws-f-remaining-mods \
  --base main \
  --token YOUR_GITHUB_TOKEN
```

### Method 3: GitHub CLI

If you have the GitHub CLI installed and authenticated:

```bash
gh pr create \
  --repo DICKY1987/CLI_RESTART \
  --base main \
  --head ws-f-remaining-mods \
  --title "Merge ws-f-remaining-mods into main" \
  --body "Open PR to merge ws-f-remaining-mods into main for review and CI validation."
```

### Method 4: GitHub Web UI

1. Navigate to: https://github.com/DICKY1987/CLI_RESTART
2. Click on **"Pull requests"** tab
3. Click **"New pull request"** button
4. Set:
   - **base**: `main`
   - **compare**: `ws-f-remaining-mods`
5. Click **"Create pull request"**
6. Enter:
   - **Title**: `Merge ws-f-remaining-mods into main`
   - **Description**: `Open PR to merge ws-f-remaining-mods into main for review and CI validation.`
7. Click **"Create pull request"**

## PR Details

- **Title**: Merge ws-f-remaining-mods into main
- **Body**: Open PR to merge ws-f-remaining-mods into main for review and CI validation.
- **Base Branch**: main
- **Head Branch**: ws-f-remaining-mods

## What Happens After PR Creation

Once the PR is created:

1. **CI Validation**: Automated CI workflows will run:
   - Tests (Python, PowerShell)
   - Linting (Ruff, mypy)
   - Security scans (CodeQL, Bandit)
   - Coverage checks
   - Schema validation

2. **Code Review**: Team members can review the changes

3. **Merge**: Once approved and CI passes, the PR can be merged

## Changes Included

The ws-f-remaining-mods branch includes approximately 20 commits with:

- **Build System**: Consolidated to Makefile, simplified Nox
- **Linting**: Fixed bare except statements, modernized typing
- **CI**: Adjusted rule configurations, made some checks non-blocking
- **Cleanup**: Removed obsolete files, quarantined deprecated content
- **Documentation**: Updated docs to reflect new structure
- **Scripts**: Deduplicated and organized scripts

## Verification

To verify the script works without creating a PR:

```bash
# This will show what would be created without actually creating it
python scripts/create_pr_ws_f_remaining_mods.py --dry-run
```

Expected output:
```
DRY RUN - Would create PR with:
  Repository: DICKY1987/CLI_RESTART
  Title: Merge ws-f-remaining-mods into main
  Base: main
  Head: ws-f-remaining-mods
  Body: Open PR to merge ws-f-remaining-mods into main for review and CI validation.
```

## Troubleshooting

### PR Already Exists

If a PR already exists for these branches, the script will detect it:

```
✓ PR already exists: #XXX (open)
  URL: https://github.com/DICKY1987/CLI_RESTART/pull/XXX
```

### Authentication Error

If you see a 401/403 error, ensure your GitHub token has the required permissions:
- `repo` scope for repository access
- `pull_request` scope for PR creation

### Branch Not Found

Ensure both branches exist on the remote:

```bash
git ls-remote --heads origin | grep -E '(main|ws-f-remaining-mods)'
```

## References

- Script: `scripts/create_pr_ws_f_remaining_mods.py`
- Workflow: `.github/workflows/create-pr-ws-f-remaining-mods.yml`
- Repository: https://github.com/DICKY1987/CLI_RESTART
