# repo_flow usage

Always let tools call `repo_flow` instead of raw git commands.

## Commands

- `repo_flow begin` — create/switch to a namespaced branch `ws/YYYY-MM-DD-<tool>-<topic>`
- `repo_flow save "message"` — stage, commit, push, ensure PR exists and is labeled for auto-merge
- `repo_flow consolidate` — server-side consolidation via repository_dispatch and scheduled workflow
- `repo_flow cleanup` — prune local merged branches

## Install hooks

```
bash ./.det-tools/scripts/install_hooks.sh
```

This sets `core.hooksPath` to `.githooks` so local guards run automatically.

