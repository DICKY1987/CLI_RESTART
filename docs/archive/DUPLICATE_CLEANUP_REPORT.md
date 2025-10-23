# Duplicate Files Cleanup Report

**Generated:** 2025-10-13
**Analysis Source:** `files_out_OF_LOCl.txt`
**Detailed Analysis:** `duplicate_analysis.txt`

## Executive Summary

Found **22 duplicate directories/files** between:
- **Parent Directory:** `C:\Users\Richard Wilks\`
- **Project Directory:** `C:\Users\Richard Wilks\CLI_RESTART\`

### Key Findings:

✅ **21 items** - Inside (CLI_RESTART) versions are **NEWER** → Safe to delete outside versions
⚠️ **1 item** - Outside version is **NEWER** → Requires manual review

---

## Safe to Delete (Inside is Newer)

These items have newer versions in CLI_RESTART and can be safely deleted from the parent directory:

| Item | Age Difference | Recommendation |
|------|----------------|----------------|
| `.ai` | ~7.6 days newer inside | DELETE outside |
| `.gemini` | ~5 days newer inside | DELETE outside |
| `.github` | ~7.8 days newer inside | DELETE outside |
| `.git-rewrite` | ~8.6 days newer inside | DELETE outside |
| `.pytest_cache` | ~21.9 days newer inside | DELETE outside |
| `.ruff_cache` | ~8.4 days newer inside | DELETE outside |
| `.venv` | ~1.3 days newer inside | DELETE outside |
| `.vscode` | ~8.6 days newer inside | DELETE outside |
| `alembic` | ~7.7 days newer inside | DELETE outside |
| `artifacts` | ~7 days newer inside | DELETE outside |
| `CLI_PY_GUI` | ~7 days newer inside | DELETE outside |
| `config` | ~7.8 days newer inside | DELETE outside |
| `deploy` | ~19.2 days newer inside | DELETE outside |
| `logs` | ~7 days newer inside | DELETE outside |
| `nul` | Same timestamp | DELETE outside (duplicate) |
| `scripts` | ~1.3 days newer inside | DELETE outside |
| `specs` | ~20.1 days newer inside | DELETE outside |
| `src` | ~8.8 days newer inside | DELETE outside |
| `state` | ~8.1 days newer inside | DELETE outside |
| `tests` | ~8 days newer inside | DELETE outside |
| `workflows` | ~7.1 days newer inside | DELETE outside |

---

## Manual Review Required (Outside is Newer)

⚠️ **ATTENTION REQUIRED**

| Item | Issue | Action Required |
|------|-------|-----------------|
| ` ` (space directory) | Outside is 96 seconds newer (98 KB vs 49 KB) | **Manually compare contents before deciding** |

### Investigation Steps for Space Directory:

```powershell
# Compare contents
Get-ChildItem "C:\Users\Richard Wilks\ " -Recurse
Get-ChildItem "C:\Users\Richard Wilks\CLI_RESTART\ " -Recurse

# Check differences
Compare-Object `
  (Get-ChildItem "C:\Users\Richard Wilks\ " -Recurse) `
  (Get-ChildItem "C:\Users\Richard Wilks\CLI_RESTART\ " -Recurse) `
  -Property Name, Length, LastWriteTime
```

---

## Additional Cleanup Candidates

These files in the **parent directory** should be reviewed and likely deleted:

### Installation Logs (18 files)
- `installation-20251004-*.log` (multiple files from October 4)
- `installation-report-20251004-172122.md`

**Recommendation:** Archive or delete after verifying no useful info

### Temporary/Check Files
- `._chk2.py`
- `._chk_router.py`
- `._check_coord3.py`
- `._check_coord2.py`
- `._check_coord.py`
- `CON` (Windows reserved name, likely temp file)
- `nul` (Windows reserved name)

**Recommendation:** Delete

### Configuration Files
- `.aider.conf.yml` - **KEEP** (user-level aider config)
- `.gitconfig` - **KEEP** (global git config)
- `.workspace-config.ps1` - Review if still needed

### Documentation Files
- `AGENTS.md` - Move to `docs/` if needed
- `GEMINI.md` - Move to `docs/` if needed
- `OPENCODE-DEEPSEEK-SETUP.md` - Already in `docs/setup/`
- `VERIFICATION_SYSTEM_README.md` - Move to `docs/` if needed

### Script Files
- `verify-deepseek-setup.cmd` - Already in `scripts/`
- `verify-deepseek-setup.ps1` - Already in `scripts/`
- `opencode-deepseek-run.cmd` - Already in `scripts/`
- `opencode-deepseek-run.ps1` - Already in `scripts/`
- `opencode-deepseek.cmd` - Already in `scripts/`
- `opencode-deepseek.ps1` - Already in `scripts/`
- `simple_merge.sh` - Move to `scripts/` if needed
- `schema_validator.py` - Move to appropriate location if needed

### Text Files
- `672.txt` - Review contents
- `atomic-files.txt` - Review contents
- `aws-files.txt` - Review contents
- `cli_restart_tree.txt` - Likely outdated, can delete
- `pytest_output.txt` - Old test output, can delete
- `2025-10-07-httpsgithubcomdicky1987atomicgit-read-this.txt` - Review

### Backup Files
- `.claude.json.backup` - Archive if needed

---

## Recommended Actions

### Step 1: Automated Cleanup (Safe Items)

Run the provided PowerShell script:

```powershell
# Review the script first
Get-Content .\cleanup_duplicates.ps1

# Execute with backup
.\cleanup_duplicates.ps1
```

**What it does:**
- Creates timestamped backup: `CLI_RESTART_duplicates_backup_YYYYMMDD_HHMMSS`
- Deletes 21 duplicate items where inside version is newer
- Keeps backup for safety

### Step 2: Manual Review (Space Directory)

```powershell
# Compare the space directories
explorer "C:\Users\Richard Wilks\ "
explorer "C:\Users\Richard Wilks\CLI_RESTART\ "

# After comparison, either:
# A) If outside is truly needed, copy newer files to inside
# B) If inside is sufficient, delete outside
```

### Step 3: Additional Cleanup

```powershell
# Review and delete installation logs
Get-ChildItem "C:\Users\Richard Wilks\installation-*.log"

# Review temporary files
Get-ChildItem "C:\Users\Richard Wilks\._*.py"
Get-ChildItem "C:\Users\Richard Wilks\" -Include "CON","nul"

# Review text files
Get-ChildItem "C:\Users\Richard Wilks\*.txt"
```

---

## Directories That Should STAY in Parent Directory

These are **user-level** or **system-level** and should NOT be moved:

- `.cache` - User cache directory
- `.config` - User configuration
- `.continue` - Continue.dev user config
- `.local` - User-local packages
- `.ollama` - Ollama user data
- `.viminfo` - Vim user history
- `Downloads` - User downloads folder
- `Saved Games` - User games folder
- `scoop` - Windows package manager
- `pipx` - User-level pipx installations
- `.gitconfig` - Global git configuration
- `.aider.conf.yml` - User-level aider configuration

---

## Post-Cleanup Verification

After cleanup, verify:

```powershell
# 1. CLI_RESTART structure is intact
cd "C:\Users\Richard Wilks\CLI_RESTART"
git status

# 2. No broken imports or paths
pytest tests/ -v

# 3. Backup exists
ls "C:\Users\Richard Wilks\CLI_RESTART_duplicates_backup_*"
```

---

## Rollback Plan

If something goes wrong:

```powershell
# Restore all backed-up items
$backupDir = "C:\Users\Richard Wilks\CLI_RESTART_duplicates_backup_YYYYMMDD_HHMMSS"
Copy-Item -Path "$backupDir\*" -Destination "C:\Users\Richard Wilks\" -Recurse -Force
```

---

## Summary Statistics

- **Total duplicates found:** 22
- **Safe to auto-delete:** 21 items
- **Needs manual review:** 1 item (space directory)
- **Additional cleanup candidates:** ~40+ files
- **Estimated space recovered:** ~500 MB+ (including logs, caches)

---

## Notes

1. All timestamps and file sizes accurate as of analysis time
2. Backup created before any deletion
3. `.venv` deletion is safe - can be recreated with `pip install -e .`
4. Cache directories (`.ruff_cache`, `.pytest_cache`) are safe to delete - will regenerate
5. Keep user-level configs (`.gitconfig`, `.aider.conf.yml`) in parent directory

---

**Generated by:** CLI_RESTART Duplicate Analysis System
**Script:** `cleanup_duplicates.ps1`
**Analysis:** `duplicate_analysis.txt`
