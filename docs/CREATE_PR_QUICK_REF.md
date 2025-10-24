# Quick Reference: Create PR for ws-f-remaining-mods

## Quickest Methods

### GitHub Actions (Recommended)
1. Go to: https://github.com/DICKY1987/CLI_RESTART/actions/workflows/create-pr-ws-f-remaining-mods.yml
2. Click "Run workflow" → Execute

### Makefile (Local)
```bash
make pr-create-ws-f-dry-run  # Preview first
GITHUB_TOKEN=your_token make pr-create-ws-f  # Create PR
```

### Shell Script
```bash
./scripts/create_pr_ws_f.sh --execute  # Requires GITHUB_TOKEN
```

## PR Details
- **Title**: Merge ws-f-remaining-mods into main
- **Base**: main
- **Head**: ws-f-remaining-mods
- **Body**: Open PR to merge ws-f-remaining-mods into main for review and CI validation.

## Full Documentation
See: `docs/guides/CREATE_PR_WS_F_REMAINING_MODS.md`

## Tools Available
- Python: `scripts/create_pr_ws_f_remaining_mods.py`
- Shell: `scripts/create_pr_ws_f.sh`
- Workflow: `.github/workflows/create-pr-ws-f-remaining-mods.yml`
- Make: `make pr-create-ws-f` / `make pr-create-ws-f-dry-run`
