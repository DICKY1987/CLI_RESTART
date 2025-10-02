Param(
  [switch]$DryRun = $true,
  [int]$BranchDays = 7,
  [int]$LockHours = 1
)

python - <<'PY'
import os, sys
from scripts.cleanup_orphans import list_stale_branches, list_abandoned_locks

dry = os.environ.get('DRYRUN','1') == '1'
days = int(os.environ.get('BRANCHDAYS','7'))
hours = int(os.environ.get('LOCKHOURS','1'))

for b in list_stale_branches(days):
    print(f"Stale branch: {b}")

for lf in list_abandoned_locks(hours):
    print(f"Abandoned lock: {lf}")
PY

