Title: <concise, imperative>

Summary
- What change is being made and why?
- Link to issue(s) and design/docs.

Risk & Impact
- Risk level: low/medium/high and rationale
- Backward compatibility: yes/no; details
- User-facing changes: screenshots or CLI examples (if applicable)

Rollout & Feature Flags
- Flags introduced/modified (keys):
- Default state and environments:
- Cleanup date (expiry) and owner:

SLOs
- Expected impact on service SLOs (availability/latency or job success rate)
- Runbook/dashboard links

Security & Secrets
- New secrets or scope changes
- Storage location (vault), rotation plan, and references added to `.runs/secrets.jsonl`

Testing
- Unit/integration tests added or rationale if not applicable
- Manual verification steps

Backout Plan
- How to revert safely; data migration rollback steps if any

Checklist
- [ ] CI green (PowerShell CI, Supply Chain Security, Policy Validate, Flags Governance)
- [ ] Updated docs/runbooks as needed
- [ ] Added/updated entries in `flags/registry.yaml` (if flags involved)
- [ ] Appended ledger entries to `.runs/changes.jsonl` (deploys) and `.runs/secrets.jsonl` (rotations)

