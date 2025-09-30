# One-time Repository Settings (Manual)

These settings keep the automation effective and prevent branch sprawl.

## Branch Protection

- Protect `main`: require status checks to pass before merging.
- Enable Auto-merge or Merge queue.
- Require PRs (disallow direct pushes to main).
- Enable Automatically delete head branches on merge.

## Required Checks (examples)

- Lint/Test CI workflow(s).
- Optionally a security scan workflow.

## Secrets

- `GITHUB_TOKEN` is provided automatically for this repo.
- If you need elevated scopes, create a fine-grained PAT named `GH_TOKEN` and add to repo secrets.

## Notes

The automation creates branches named `ws/YYYY-MM-DD-<tool>-<topic>`,
opens/refreshes PRs, rebases them periodically, and deletes merged branches.
Local hooks and `repo_flow` CLI prevent unsafe local actions.

