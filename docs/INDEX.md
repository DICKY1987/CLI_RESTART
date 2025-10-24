# Documentation Index

Purpose: Provide a curated entry point to the repository documentation and a consistent structure for contributors.

Sections
- Concepts: High-level overviews, architecture, domain concepts.
- How-To: Task-oriented guides and step-by-step instructions.
- Reference: APIs, CLI, configuration, schemas, and command catalogs.
- ADR: Architecture Decision Records documenting important decisions.

Getting Started
- Concepts: docs/concepts/
- How-To: docs/how-to/
- Reference: docs/reference/
- ADR: docs/adr/

Consolidation Status
- This index and taxonomy are part of WS-B (Documentation Consolidation).
- Redirects for moved/removed files are tracked in docs/REDIRECTS.md.
- Inventory and summaries are under docs/_meta/ (generated as part of WS-B).

Curation Checklist
- Title, summary, owners, and last-verified present in front-matter.
- Links verified with a link checker before merge.
- Avoid duplicate or overlapping pages; prefer updating existing content.
- Place documents under the appropriate folder: concepts/, how-to/, reference/, or adr/.

Front-Matter Template
Use the template in docs/_templates/front_matter.md at the top of each document.

