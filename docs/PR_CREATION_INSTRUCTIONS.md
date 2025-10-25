# Creating Pull Request: ws-f-build-system-consolidation → main

This document provides multiple methods to create a pull request merging the `ws-f-build-system-consolidation` branch into `main`.

## Branch Information

- **Source Branch**: `ws-f-build-system-consolidation`
- **Target Branch**: `main`
- **Repository**: `DICKY1987/CLI_RESTART`
- **PR Title**: "Merge ws-f-build-system-consolidation into main"
- **PR Body**: "Open PR to merge ws-f-build-system-consolidation into main for review and CI validation."

## Methods to Create the PR

### Method 1: GitHub Actions Workflow (Recommended)

A GitHub Actions workflow has been created that can be manually triggered:

1. Go to: https://github.com/DICKY1987/CLI_RESTART/actions/workflows/create-pr-ws-f-build.yml
2. Click "Run workflow"
3. Select the branch (default values are already set)
4. Click "Run workflow"

The workflow file is located at: `.github/workflows/create-pr-ws-f-build.yml`

### Method 2: Shell Script

Run the provided shell script:

```bash
# From repository root
./scripts/create_ws_f_pr.sh
```

**Requirements:**
- GitHub CLI (`gh`) must be installed
- Must be authenticated: `gh auth login` or have `GH_TOKEN` set

### Method 3: Python Script

Run the Python script:

```bash
# With GITHUB_TOKEN environment variable
export GITHUB_TOKEN=your_personal_access_token
python scripts/create_pr.py

# Or pass token as argument
python scripts/create_pr.py your_personal_access_token
```

**Requirements:**
- Python 3.9+
- Repository dependencies installed: `pip install -e .`
- GitHub personal access token with `repo` scope

### Method 4: GitHub CLI Direct Command

Use the GitHub CLI directly:

```bash
gh pr create \
  --repo DICKY1987/CLI_RESTART \
  --title "Merge ws-f-build-system-consolidation into main" \
  --body "Open PR to merge ws-f-build-system-consolidation into main for review and CI validation." \
  --base main \
  --head ws-f-build-system-consolidation
```

**Requirements:**
- GitHub CLI installed and authenticated

### Method 5: GitHub Web UI

1. Go to: https://github.com/DICKY1987/CLI_RESTART
2. Click on "Pull requests" tab
3. Click "New pull request"
4. Set base: `main`
5. Set compare: `ws-f-build-system-consolidation`
6. Click "Create pull request"
7. Enter title: "Merge ws-f-build-system-consolidation into main"
8. Enter description: "Open PR to merge ws-f-build-system-consolidation into main for review and CI validation."
9. Click "Create pull request"

## Verification

After creating the PR, verify it was created successfully:

```bash
# List open PRs
gh pr list --repo DICKY1987/CLI_RESTART

# Or check the web UI
# https://github.com/DICKY1987/CLI_RESTART/pulls
```

## Troubleshooting

### "No token found" or authentication errors

- Ensure you have a valid GitHub personal access token
- Token must have `repo` scope for private repositories
- Set the token in environment: `export GITHUB_TOKEN=your_token`

### "Branch not found" errors

- Verify the branch exists: `git branch -r | grep ws-f-build-system-consolidation`
- Ensure you've fetched the latest: `git fetch origin`

### "Validation Failed" errors

- Check if a PR already exists for these branches
- Verify you have write access to the repository

## Files Created

This PR creation setup includes:

1. `.github/workflows/create-pr-ws-f-build.yml` - GitHub Actions workflow
2. `scripts/create_pr.py` - Python script for PR creation
3. `scripts/create_ws_f_pr.sh` - Shell script for PR creation
4. `docs/PR_CREATION_INSTRUCTIONS.md` - This documentation file

## Next Steps

Once the PR is created:

1. Review the changes in the PR
2. Ensure CI/CD checks pass
3. Request reviews from team members
4. Merge when approved and all checks pass
