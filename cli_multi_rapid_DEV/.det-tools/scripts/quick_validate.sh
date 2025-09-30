#!/usr/bin/env bash
set -euo pipefail
# Example quick validations; make these no-ops if tools are absent

if command -v npm >/dev/null 2>&1 && [ -f package.json ]; then
  npm run -s lint || true
fi

if command -v black >/dev/null 2>&1; then
  black --check . || true
fi

if command -v flake8 >/dev/null 2>&1; then
  flake8 || true
fi

echo "quick_validate completed (best-effort)."

