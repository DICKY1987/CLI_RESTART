Canonical script locations and duplication policy

- Canonical atoms tooling lives under `tools/atomic-workflow-system/tools/atoms/`.
  - Keep `md2atom.py`, `atom_validator.py`, and related converters here.
  - Tests add this folder to `PYTHONPATH` and reference these modules.
- Do not keep parallel copies of the same script at multiple paths.
  - If a variant is needed, add flags or refactor into shared utilities.
- Remove or merge any new duplicate files by content or by name.

Enforcement

- Virtual environments, caches, and tool logs are ignored via `.gitignore`.
- Use the helper `tools/scripts/check_duplicates.ps1` to scan for duplicates before committing.

