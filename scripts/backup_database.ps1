Param(
  [string]$DestDir = ".backups"
)

if (-not $Env:DATABASE_URL) { $Env:DATABASE_URL = "sqlite:///.data/registry.db" }
$Env:DestDir = $DestDir

python - <<'PY'
import os
from scripts.backup_utils import backup_database
url = os.environ.get("DATABASE_URL", "sqlite:///.data/registry.db")
path = backup_database(url, os.environ.get("DestDir", ".backups"))
print(path)
PY

