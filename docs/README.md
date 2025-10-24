# Documentation Taxonomy and Conventions

Structure
- `docs/concepts/` — architecture, core ideas, domain concepts.
- `docs/how-to/` — step-by-step guides and task-oriented recipes.
- `docs/reference/` — API/CLI references, configuration, schemas.
- `docs/adr/` — Architecture Decision Records (ADR-0001, ADR-0002, ...).

Conventions
- Each document starts with front-matter (title, summary, owners, last-verified). See `docs/_templates/front_matter.md`.
- Keep file names lowercase-with-dashes. Prefer stable anchors for deep links.
- Update `docs/INDEX.md` when adding or retiring pages.
- When moving or removing a document, add an entry to `docs/REDIRECTS.md`.

Validation
- Run a link checker locally or in CI to ensure internal links resolve.
- Prefer updating existing documents over duplicating content.

