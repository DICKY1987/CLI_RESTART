# Create Pull Request: ws-f-mods-applied → main

## Summary

This document provides instructions to create a pull request merging the `ws-f-mods-applied` branch into `main` for review and CI validation.

## Branch Analysis

**Source Branch:** `ws-f-mods-applied` (SHA: 8a42a10)
**Target Branch:** `main` (SHA: cd40731)
**Commits to Merge:** 11 commits

### Commits in ws-f-mods-applied (not in main)

1. **8a42a10** - fix(lint): eliminate bare excepts; modernize typing and test var names; restore proper indentation
2. **4a7b089** - ci: keep UP006/UP035 ignored for now; will tackle modernization in a follow-up
3. **cdca84e** - chore(lint): partially re-enable Ruff rules (E722, UP006, UP035, E741) after code fixes
4. **0006bb6** - fix(lint): replace bare excepts; modernize typing in factory; resolve ambiguous test vars
5. **feb53a4** - style: replace bare except with 'except Exception' in DeepSeek adapter
6. **7362df2** - WS-C: Scripts de-duplication completed (wrappers + index); no changes required vs HEAD
7. **93e76bc** - ci: fix validators and adjust supply-chain severity; make PS tests non-blocking
8. **5e52933** - ci: relax Ruff rules; skip Pester in consolidated test; make mypy non-blocking
9. **ff600a9** - style: apply Ruff --fix and isort/black formatting (safe autofixes)
10. **63be588** - Fix Makefile tabs for test targets
11. **f2767cc** - WS-F: consolidate build systems to Makefile; simplify Nox to tests-only; remove Taskfile; update CI to run make ci; update docs

## Changes Overview

This PR contains WS-F follow-up modifications applied after the build-system consolidation effort:

### Build System Consolidation (WS-F)
- Consolidate build systems to Makefile
- Simplify Nox to tests-only  
- Remove Taskfile
- Update CI to run `make ci`
- Update documentation

### Code Quality & Linting
- Apply Ruff --fix and isort/black formatting (safe autofixes)
- Fix Makefile tabs for test targets
- Eliminate bare excepts; modernize typing
- Replace bare except with 'except Exception' in DeepSeek adapter
- Partially re-enable Ruff rules (E722, UP006, UP035, E741) after code fixes
- Modernize typing in factory; resolve ambiguous test vars

### Scripts & CI Improvements
- Scripts de-duplication completed (wrappers + index)
- Fix validators and adjust supply-chain severity
- Make PowerShell tests non-blocking
- Relax Ruff rules; skip Pester in consolidated test
- Make mypy non-blocking

## Creating the Pull Request

### Option 1: Using GitHub CLI (gh)

```bash
# Ensure you're authenticated
gh auth login

# Create the PR
gh pr create \
  --repo DICKY1987/CLI_RESTART \
  --base main \
  --head ws-f-mods-applied \
  --title "WS-F: Build System Consolidation & Follow-up Modifications" \
  --body-file PR_BODY.md
```

### Option 2: Using GitHub Web UI

1. Navigate to: https://github.com/DICKY1987/CLI_RESTART
2. Click "Pull requests" tab
3. Click "New pull request"
4. Set base: `main`
5. Set compare: `ws-f-mods-applied`
6. Use the title: **WS-F: Build System Consolidation & Follow-up Modifications**
7. Copy the PR description from `PR_BODY.md` (see below)

### Option 3: Using curl (GitHub API)

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Create PR via API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/DICKY1987/CLI_RESTART/pulls \
  -d @PR_PAYLOAD.json
```

## PR Body Content

Save this content to `PR_BODY.md`:

```markdown
# WS-F: Build System Consolidation & Follow-up Modifications

This PR opens the existing work in `ws-f-mods-applied` for review and CI validation. The branch contains WS-F follow-up modifications applied after the build-system consolidation effort.

## Changes Overview

This branch includes 11 commits with the following improvements:

### Build System Consolidation (WS-F)
- Consolidate build systems to Makefile
- Simplify Nox to tests-only  
- Remove Taskfile
- Update CI to run `make ci`
- Update documentation

### Code Quality & Linting
- Apply Ruff --fix and isort/black formatting (safe autofixes)
- Fix Makefile tabs for test targets
- Eliminate bare excepts; modernize typing
- Replace bare except with 'except Exception' in DeepSeek adapter
- Partially re-enable Ruff rules (E722, UP006, UP035, E741) after code fixes
- Modernize typing in factory; resolve ambiguous test vars

### Scripts & CI Improvements
- Scripts de-duplication completed (wrappers + index)
- Fix validators and adjust supply-chain severity
- Make PowerShell tests non-blocking
- Relax Ruff rules; skip Pester in consolidated test
- Make mypy non-blocking

## Testing & Validation

This PR is opened for:
- ✅ Code review
- ✅ CI validation
- ✅ Merge approval

## Commit History

- **8a42a10** - fix(lint): eliminate bare excepts; modernize typing and test var names
- **4a7b089** - ci: keep UP006/UP035 ignored for now
- **cdca84e** - chore(lint): partially re-enable Ruff rules
- **0006bb6** - fix(lint): replace bare excepts; modernize typing in factory
- **feb53a4** - style: replace bare except with 'except Exception' in DeepSeek adapter
- **7362df2** - WS-C: Scripts de-duplication completed
- **93e76bc** - ci: fix validators and adjust supply-chain severity
- **5e52933** - ci: relax Ruff rules; skip Pester in consolidated test
- **ff600a9** - style: apply Ruff --fix and isort/black formatting
- **63be588** - Fix Makefile tabs for test targets
- **f2767cc** - WS-F: consolidate build systems to Makefile

## Related Work

- Base commit: cd40731 (Merge train: PRs #115–#119)
- Branch: `ws-f-mods-applied` (SHA: 8a42a10)

No additional code changes are requested at this time.
```

## PR Payload for API (PR_PAYLOAD.json)

```json
{
  "title": "WS-F: Build System Consolidation & Follow-up Modifications",
  "body": "This PR opens the existing work in `ws-f-mods-applied` for review and CI validation. The branch contains WS-F follow-up modifications applied after the build-system consolidation effort.\n\n## Changes Overview\n\nThis branch includes 11 commits with the following improvements:\n\n### Build System Consolidation (WS-F)\n- Consolidate build systems to Makefile\n- Simplify Nox to tests-only  \n- Remove Taskfile\n- Update CI to run `make ci`\n- Update documentation\n\n### Code Quality & Linting\n- Apply Ruff --fix and isort/black formatting (safe autofixes)\n- Fix Makefile tabs for test targets\n- Eliminate bare excepts; modernize typing\n- Replace bare except with 'except Exception' in DeepSeek adapter\n- Partially re-enable Ruff rules (E722, UP006, UP035, E741) after code fixes\n- Modernize typing in factory; resolve ambiguous test vars\n\n### Scripts & CI Improvements\n- Scripts de-duplication completed (wrappers + index)\n- Fix validators and adjust supply-chain severity\n- Make PowerShell tests non-blocking\n- Relax Ruff rules; skip Pester in consolidated test\n- Make mypy non-blocking\n\n## Testing & Validation\n\nThis PR is opened for:\n- ✅ Code review\n- ✅ CI validation\n- ✅ Merge approval\n\nNo additional code changes are requested at this time.",
  "head": "ws-f-mods-applied",
  "base": "main"
}
```

## Verification

After creating the PR, verify:

1. ✅ PR appears in GitHub UI
2. ✅ CI checks begin running
3. ✅ All 11 commits are included
4. ✅ Diff shows expected changes (build system, linting, CI config)
5. ✅ No merge conflicts

## Direct PR Creation Link

You can also use this direct link to create the PR with pre-filled fields:

```
https://github.com/DICKY1987/CLI_RESTART/compare/main...ws-f-mods-applied?expand=1
```

## Notes

- This PR requires review but **no additional code changes**
- The purpose is to enable review and CI validation of the WS-F work
- All commits are already present in the `ws-f-mods-applied` branch
