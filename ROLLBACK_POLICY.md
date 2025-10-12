# Rollback Branch Policy

This repository forbids creation and pushing of `rollback/*` branches.

Why
- Previous automation created hundreds of rollback branches locally and on GitHub.
- This caused noise, risk, and repository bloat with little operational value.

Guards in place
- Local pre-commit: blocks commits on `rollback/*` branches.
- Local pre-push: blocks any push that includes `refs/heads/rollback/*` refs.
- CI workflow: auto-deletes any pushed `rollback/**` branches and fails the job.
- Environment: `ENABLE_AUTO_ROLLBACK=false` to disable external rollback automation.

Allowed recovery methods
- Use standard Git techniques (e.g., `git revert`) for safe rollbacks.
- Create topic branches that are not under `rollback/*` and follow review via PR.

If you see rollback branches appear
- Do not push them. The push will be rejected or deleted by CI.
- Remove them locally: `git branch -D <branch>`.

Questions: open an issue with details of the tool or workflow attempting rollback creation.

