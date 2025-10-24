# WS-B Consolidation Report

Summary
- Inventory: 160+ Markdown files detected across repo.
- Taxonomy: Created docs/concepts, docs/how-to, docs/reference, docs/adr.
- Index/Redirects: Added docs/INDEX.md and docs/REDIRECTS.md.

Actions Completed
- Moved duplicate/confusing guides to taxonomy:
  - docs/contracts/INTERFACE_GUIDE.md -> docs/reference/cli-vscode-interface-contract.md
  - docs/guides/INTERFACE_GUIDE.md -> docs/how-to/interface-selection.md
- Curated moves from docs/ root into taxonomy (38 files):
  - How-To: getting-started, setup, workflows, simplified-workflows, vscode-cockpit, ai-tools, gui-functionality-evaluation
  - Concepts: framework-overview, cli-system-overview, execution-model, routing-logic, idempotency, ipt-wt-pattern, workflow-enhancements, workflow-integration-strategy, repo-structure
  - Reference: configuration, event-bus-topics, tool-registry, verification-framework, contracts, audit-schema, security-tokens, sql-standards, policies/*
  - Operations: operations overview and runbooks (backup-strategy, disaster-recovery, failover-strategy, maintenance-schedule)
  - Development: releasing, testing, test-gap-report
  - Updates: release-notes
- Updated internal links in 9 files to point to new locations.

Redirects
- All moves recorded in docs/REDIRECTS.md for traceability.

Next Suggestions (Non-destructive)
- Consolidate under docs/specs/ into docs/reference/specs/ with a stable index.
- Review tools/atomic-workflow-system docs; either:
  - Keep in-place but link from docs/reference/atomic-workflow-system.md, or
  - Extract to separate package docs and link out (coordinate with WS-J decision).
- Reduce top-level docs in docs/ by moving remaining topic pages into taxonomy.
- Add link-check CI to validate internal references.
- Normalize front-matter across migrated docs (owners, last-verified).

Acceptance Criteria Check
- Index present: docs/INDEX.md
- Redirects map present: docs/REDIRECTS.md
- Docs moved into taxonomy: initial batch complete
- Broken links: initial pass updated; recommend CI link check

