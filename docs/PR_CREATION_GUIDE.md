# Creating Pull Request: chore/update-submodule-aws-duplicate-workflows → main

This document describes multiple methods to create a pull request for merging the `chore/update-submodule-aws-duplicate-workflows` branch into `main`.

## Branch Information

- **Source Branch**: `chore/update-submodule-aws-duplicate-workflows`
- **Target Branch**: `main`
- **PR Title**: "Merge chore/update-submodule-aws-duplicate-workflows into main"
- **PR Description**: "Open PR to merge chore/update-submodule-aws-duplicate-workflows into main for review and CI validation."

## Method 1: GitHub Actions Workflow (Recommended)

A GitHub Actions workflow has been created that will automatically create the PR.

### Automatic Trigger
The workflow will run automatically when changes are pushed to the `copilot/merge-chore-update-submodule-aws` branch.

### Manual Trigger
You can also manually trigger the workflow:

1. Go to the Actions tab in GitHub
2. Select "Create PR - chore/update-submodule-aws-duplicate-workflows" workflow
3. Click "Run workflow"
4. Optionally enable "Dry run" to preview without creating

### Workflow File
Location: `.github/workflows/create-pr-chore-aws-submodule.yml`

## Method 2: Python Script

A Python script is available for manual PR creation with more control.

### Prerequisites
- Python 3.6+
- `requests` library (`pip install requests`)
- GitHub Personal Access Token with `repo` permissions

### Usage

#### Set up GitHub token
```bash
export GITHUB_TOKEN=<your_github_token>
```

#### Run the script
```bash
# Dry run (preview only)
python scripts/create_pr_chore_aws_submodule.py --dry-run

# Create the PR
python scripts/create_pr_chore_aws_submodule.py
```

### Script Features
- ✅ Checks if the source branch exists
- ✅ Checks if a PR already exists (avoids duplicates)
- ✅ Dry-run mode for safe testing
- ✅ Clear success/error messages
- ✅ Returns PR URL upon creation

## Method 3: GitHub CLI (gh)

If you have the GitHub CLI installed and authenticated:

```bash
# Authenticate (if not already)
gh auth login

# Create the PR
gh pr create \
  --repo DICKY1987/CLI_RESTART \
  --base main \
  --head chore/update-submodule-aws-duplicate-workflows \
  --title "Merge chore/update-submodule-aws-duplicate-workflows into main" \
  --body "Open PR to merge chore/update-submodule-aws-duplicate-workflows into main for review and CI validation."
```

## Method 4: GitHub Web UI

1. Navigate to https://github.com/DICKY1987/CLI_RESTART
2. Click on "Pull requests" tab
3. Click "New pull request"
4. Select:
   - Base: `main`
   - Compare: `chore/update-submodule-aws-duplicate-workflows`
5. Enter title: "Merge chore/update-submodule-aws-duplicate-workflows into main"
6. Enter description: "Open PR to merge chore/update-submodule-aws-duplicate-workflows into main for review and CI validation."
7. Click "Create pull request"

## Verification

After creating the PR, it will:
- Trigger CI/CD pipelines for validation
- Be available for code review
- Run all configured checks and tests

### Expected CI Checks
Based on the repository's workflow configuration, the PR will trigger:
- Code quality checks (linting, formatting)
- Security scans (CodeQL, dependency scanning)
- Test suites
- Schema validation
- Policy compliance checks

## Troubleshooting

### Branch doesn't exist
If the `chore/update-submodule-aws-duplicate-workflows` branch doesn't exist:
```bash
git fetch origin
git branch -r | grep chore/update-submodule-aws-duplicate-workflows
```

### PR already exists
Check for existing PRs:
```bash
gh pr list --repo DICKY1987/CLI_RESTART --head chore/update-submodule-aws-duplicate-workflows
```

Or visit: https://github.com/DICKY1987/CLI_RESTART/pulls

### Authentication issues
- For Python script: Ensure `GITHUB_TOKEN` environment variable is set with valid token
- For GitHub CLI: Run `gh auth status` to check authentication
- For GitHub Actions: Workflow uses `GITHUB_TOKEN` automatically in Actions context

## Files Created

1. `.github/workflows/create-pr-chore-aws-submodule.yml` - GitHub Actions workflow
2. `scripts/create_pr_chore_aws_submodule.py` - Python script for PR creation
3. `docs/PR_CREATION_GUIDE.md` - This documentation file

## Additional Resources

- [GitHub REST API - Pull Requests](https://docs.github.com/en/rest/pulls/pulls)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub Actions - github-script](https://github.com/actions/github-script)
