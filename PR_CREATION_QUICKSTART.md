# Quick Start: Create PR for AWS Submodule Update

This is a quick reference for creating the PR to merge `chore/update-submodule-aws-duplicate-workflows` into `main`.

## Fastest Method: Let GitHub Actions Do It

The workflow `.github/workflows/create-pr-chore-aws-submodule.yml` will automatically run when changes are pushed to the `copilot/merge-chore-update-submodule-aws` branch.

**Status**: Workflow should be running now! Check: https://github.com/DICKY1987/CLI_RESTART/actions

## Manual Method: Python Script

If you prefer manual control:

```bash
export GITHUB_TOKEN=your_token_here
python scripts/create_pr_chore_aws_submodule.py
```

## Complete Documentation

See [docs/PR_CREATION_GUIDE.md](docs/PR_CREATION_GUIDE.md) for all available methods.

## What This PR Will Do

When created, the PR will:
- Merge branch: `chore/update-submodule-aws-duplicate-workflows` → `main`
- Title: "Merge chore/update-submodule-aws-duplicate-workflows into main"
- Trigger all CI/CD validation checks
- Be ready for code review

## Branch Details

- **10+ commits** in the source branch
- Includes: AWS submodule updates, lint fixes, and workflow improvements
- All changes are related to AWS duplicate workflow cleanup
