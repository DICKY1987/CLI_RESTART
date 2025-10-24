Feature Flags Governance

Overview
- Single source of truth: `flags/registry.yaml`
- Required validation in CI: `.github/workflows/flags-governance.yml`
- Ownership: `flags/` directory owned by platform/product teams in CODEOWNERS

Rules
- Every flag must have: key, description, owners, created, expires
- Expires must be in the future; CI fails on expired flags
- Default lifecycle 90 days unless specified
- Link rollouts to change specs and runbooks

Process
1) Propose a flag: add entry to `flags/registry.yaml` with owner and expiry
2) Reference the flag in PR using the change spec template
3) After rollout complete, remove flag and cleanup dead code

Auditing
- Record deployments and removals in `.runs/changes.jsonl`
- Record any secret changes in `.runs/secrets.jsonl`

