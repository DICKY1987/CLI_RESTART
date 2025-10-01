#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL=${DATABASE_URL:-"sqlite:///.data/registry.db"}
BACKUP_FILE=${1:?"Usage: $0 <backup_file>"}

python - <<PY
import os
from scripts.backup_utils import restore_database
url = os.environ.get("DATABASE_URL", "sqlite:///.data/registry.db")
restore_database(url, "${BACKUP_FILE}")
print("restored")
PY

