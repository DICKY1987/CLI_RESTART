#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL=${DATABASE_URL:-"sqlite:///.data/registry.db"}
DEST_DIR=${1:-".backups"}

python - <<PY
import os
from scripts.backup_utils import backup_database
url = os.environ.get("DATABASE_URL", "sqlite:///.data/registry.db")
path = backup_database(url, "${DEST_DIR}")
print(path)
PY

