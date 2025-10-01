# Reproducible Builds

This repository includes a reproducible build check that builds the package twice in a clean environment and compares artifact hashes.

- CI workflow: `.github/workflows/reproducible-build.yml`
- Script: `scripts/verify_reproducible_build.py`

Local usage
- Create/activate a virtualenv
- `pip install build`
- `python scripts/verify_reproducible_build.py`

The job fails if the two builds produce artifacts with different hashes.