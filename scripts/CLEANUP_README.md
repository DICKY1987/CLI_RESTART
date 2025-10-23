# Cleanup Script Usage Guide

This directory contains scripts to safely remove archived, backup, legacy, and outdated files from the repository.

## Quick Start

### 1. Preview Mode (Safe - Recommended First Step)

**Windows PowerShell:**
```powershell
.\scripts\cleanup_archive_and_obsolete.ps1
```

**Windows Command Prompt / Double-click:**
```cmd
scripts\cleanup_archive_and_obsolete.cmd
```

**What it does:** Shows what WOULD be deleted without actually deleting anything.

### 2. Execute Cleanup (Actually Delete Files)

**PowerShell:**
```powershell
.\scripts\cleanup_archive_and_obsolete.ps1 -DryRun:$false
```

**Command Prompt:**
```cmd
scripts\cleanup_archive_and_obsolete.cmd --execute
```

**What it does:** Actually removes the files (with confirmation prompt).

### 3. Force Mode (No Confirmation)

**PowerShell:**
```powershell
.\scripts\cleanup_archive_and_obsolete.ps1 -DryRun:$false -Force
```

**Command Prompt:**
```cmd
scripts\cleanup_archive_and_obsolete.cmd --force
```

**What it does:** Removes files without asking for confirmation (use with caution).

## What Gets Removed

### Phase 1: Archived Cleanup Scripts (~24 KB)
- `scripts/archive/` - Old cleanup scripts from October 13

### Phase 2: Outdated Reports (~28 KB)
- `docs/reports/2025-09-20/` - Reports from September (1 month old)
  - cli_updates_version_1.txt
  - cli_updates_version_2.md
  - stakeholder_reports.md
  - executive_dashboard.md

### Phase 3: Old Cleanup Manifest
- `cleanup-manifest-2025-10-18.txt` - Previous cleanup planning document

### Phase 4: Coverage Files (Regenerated Artifacts)
- `.coverage` - Root coverage file
- `tools/atomic-workflow-system/.coverage` - Submodule coverage file

### Phase 5: Activity Logs
- `logs/activity.log` - Archived if >10 MB, otherwise kept

### Phase 6: Empty Directories
- Any empty directories found (excluding .git, .venv, node_modules)

## Output Files

After running the script, you'll find:

1. **Manifest:** `logs/cleanup-manifest-YYYY-MM-DD-HHmmss.txt`
   - Detailed list of what was (or would be) removed
   - File sizes
   - Success/failure status

2. **Log:** `logs/cleanup-log-YYYY-MM-DD-HHmmss.log`
   - Timestamped execution log
   - All actions taken
   - Any errors encountered

## Safety Features

1. **Dry-run by default:** Won't delete anything unless you explicitly use `-DryRun:$false`
2. **Confirmation prompt:** Asks for confirmation before deleting (unless `-Force` is used)
3. **Detailed logging:** Every action is logged
4. **Manifest generation:** Creates a record of all deletions
5. **Size reporting:** Shows how much space will be/was freed
6. **Error handling:** Continues even if individual operations fail

## Troubleshooting

### "Execution Policy" Error

If you get an error about execution policy, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or use the batch file (`.cmd`) which bypasses this.

### "Access Denied" Errors

- Close any programs that might have files open
- Run PowerShell/Command Prompt as Administrator
- Check file permissions

### Want to Keep Some Files?

Edit the script and comment out the specific `Remove-ItemSafely` calls for files you want to keep.

## Recommended Workflow

1. **First run:** Preview with dry-run mode
   ```powershell
   .\scripts\cleanup_archive_and_obsolete.ps1
   ```

2. **Review:** Check the manifest file to see what will be deleted

3. **Execute:** If everything looks good, run with execute mode
   ```powershell
   .\scripts\cleanup_archive_and_obsolete.ps1 -DryRun:$false
   ```

4. **Verify:** Check the log file for any errors

5. **Commit:** If satisfied, commit the cleanup
   ```bash
   git add -A
   git commit -m "chore: remove archived and obsolete files"
   ```

## Statistics from Previous Cleanup

According to git history:
- **2025-10-23** (commit `54e88bd`): Removed 32+ MB of clutter
- **2025-10-18**: Major cleanup of extensions, caches, duplicates (~415 MB)

This script targets the remaining small (~57 KB) obsolete files.

## Need Help?

- Review the generated manifest: `logs/cleanup-manifest-*.txt`
- Check the log file: `logs/cleanup-log-*.log`
- Look at git history: `git log --oneline --grep="cleanup"`
