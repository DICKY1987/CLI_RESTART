#!/usr/bin/env bash
set -euo pipefail
cmd="${1:-}"; msg="${2:-update}"

import_gitconfig() {
  root="$(git rev-parse --show-toplevel)"
  if [ -f "$root/.gitconfig.local" ]; then
    git config --local include.path ".gitconfig.local"
  fi
}

ensure_branch() {
  tool="${REPO_FLOW_TOOL:-generic}"
  date="$(date +%F)"
  topic="$(git rev-parse --short HEAD)"
  branch="ws/$date-$tool-$topic"
  if git rev-parse --verify "$branch" >/dev/null 2>&1; then
    git checkout "$branch" >/dev/null
  else
    git checkout -b "$branch" >/dev/null
  fi
  echo "$branch"
}

begin() {
  import_gitconfig
  b="$(ensure_branch)"
  echo "On $b"
}

save() {
  import_gitconfig
  cur="$(git rev-parse --abbrev-ref HEAD)"
  [ "$cur" = "main" ] && { echo "Refusing to commit on main"; exit 1; }
  git add -A
  git commit -m "$msg" --allow-empty
  git push -u origin "$cur"
  if gh pr view >/dev/null 2>&1; then
    gh pr edit --title "$cur" --body "Automated PR by repo_flow" || true
  else
    gh pr create --fill --title "$cur" --body "Automated PR by repo_flow" --base main --head "$cur"
  fi
  gh pr edit --add-label "auto-merge" >/dev/null 2>&1 || true
  echo "Pushed and PR ready for $cur"
}

consolidate() {
  git fetch --prune
  git remote prune origin || true
  gh api repos/{owner}/{repo}/dispatches -f event_type="consolidate-branches" >/dev/null 2>&1 || true
}

cleanup() {
  git fetch --prune
  # delete local branches merged into origin/main
  for b in $(git branch --merged origin/main | sed 's/^..//'); do
    [ "$b" = "main" ] && continue
    git branch -d "$b" || true
  done
}

case "$cmd" in
  begin)       begin ;;
  save)        save ;;
  consolidate) consolidate ;;
  cleanup)     cleanup ;;
  *) echo "usage: repo_flow <begin|save|consolidate|cleanup> [message]"; exit 2 ;;
esac

