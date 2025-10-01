Param(
  [Parameter(Mandatory=$true)][string]$BackupFile
)

if (-not $Env:DATABASE_URL) { $Env:DATABASE_URL = "sqlite:///.data/registry.db" }
$Env:BackupFile = $BackupFile

python - <<'PY'
import os
from scripts.backup_utils import restore_database
url = os.environ.get("DATABASE_URL", "sqlite:///.data/registry.db")
restore_database(url, os.environ["BackupFile"])
print("restored")
PY

