# Rollback Branch Root Cause Analysis

## Executive Summary

**CRITICAL ISSUE IDENTIFIED**: Your repository has a git pre-push hook (`C:/tools/.det-tools/bin/create-rollback.ps1`) that creates a new rollback branch **EVERY TIME** you push to main, and then immediately pushes it to GitHub. This created 1,892 rollback branches (948 local + 944 remote).

## Root Cause

### Primary Issue: Pre-Push Hook
**Location**: `.git/hooks/pre-push` (line 16)

```bash
if [ "$BRANCH" = "main" ]; then
    # Create rollback point
    if command -v pwsh &> /dev/null; then
        pwsh -File "C:/tools/.det-tools/bin/create-rollback.ps1" "main" 2>/dev/null || true
    fi
```

**What it does**:
1. Runs **before every push** to main
2. Creates a new branch: `rollback/main/YYYYMMDD_HHmmss`
3. Pushes the rollback branch to GitHub: `git push origin "${rollbackBranch}:refs/heads/$rollbackBranch"`
4. Attempts to clean up branches older than 7 days (but this rarely works)

### Why It Created 1,892 Branches

Looking at your branch timestamps, you had branches created every 2-3 seconds:
- `rollback/main/20251012_100144`
- `rollback/main/20251012_100146`
- `rollback/main/20251012_100147`
- `rollback/main/20251012_100149`
- ...continuing for hours

**This pattern indicates**:
1. A rapid series of pushes to main (likely automated)
2. Each push triggered the pre-push hook
3. Each hook execution created and pushed a new rollback branch
4. The cleanup logic failed to delete old branches

## Secondary Issues

### 1. Ineffective Cleanup Logic
**Location**: `C:/tools/.det-tools/bin/create-rollback.ps1` (lines 41-52)

```powershell
# Cleanup old rollback branches (older than 7 days)
$cutoffDate = (Get-Date).AddDays(-7)
git for-each-ref --format='%(refname:short) %(creatordate:iso8601)' refs/heads/rollback/ 2>$null | ForEach-Object {
    $parts = $_ -split ' ', 2
    $branchName = $parts[0]
    $dateStr = $parts[1]

    try {
        $branchDate = [DateTime]::Parse($dateStr)
        if ($branchDate -lt $cutoffDate) {
            git branch -D $branchName 2>$null | Out-Null
            git push origin --delete $branchName 2>$null | Out-Null
        }
    } catch {}
}
```

**Problems**:
- Only runs AFTER creating a new branch (too late)
- Silently fails with `2>$null | Out-Null` - errors never reported
- Uses `creatordate` which may not match the timestamp in branch name
- Runs synchronously during push (slows down workflow)
- No verification that deletions succeeded

### 2. Post-Merge Hook Also Tries Cleanup
**Location**: `.git/hooks/post-merge` (lines 8-19)

```bash
# Cleanup old rollback branches (older than 7 days)
CUTOFF_DATE=$(date -d '7 days ago' +%Y%m%d 2>/dev/null || date -v-7d +%Y%m%d 2>/dev/null || echo "")

if [ -n "$CUTOFF_DATE" ]; then
    git for-each-ref --format='%(refname:short)' refs/heads/rollback/ 2>/dev/null | while read branch; do
        BRANCH_DATE=$(echo "$branch" | grep -oE '[0-9]{8}' | head -1)
        if [ -n "$BRANCH_DATE" ] && [ "$BRANCH_DATE" -lt "$CUTOFF_DATE" ]; then
            git branch -D "$branch" 2>/dev/null || true
            git push origin --delete "$branch" 2>/dev/null || true
        fi
    done
fi
```

**Problems**:
- Parses date from branch name (fragile)
- Uses shell date parsing which may fail on Windows
- Also silently fails with `2>/dev/null || true`
- Duplicates logic from create-rollback.ps1

### 3. Multiple Rollback Systems
Found multiple conflicting rollback systems:

1. **Git hook system** (`C:/tools/.det-tools/bin/create-rollback.ps1`) - Creates branches
2. **CLI orchestrator** (`src/cli_multi_rapid/commands/rollback.py`) - Snapshot-based rollback
3. **Atomic workflow system** (`tools/atomic-workflow-system/scripts/cleanup-rollback-branches.ps1`) - Cleanup script

These systems don't coordinate, leading to:
- Duplicate rollback mechanisms
- Conflicting cleanup logic
- No single source of truth

## Impact Analysis

### Performance Impact
- **Push time increased**: Creating and pushing rollback branches adds 2-5 seconds per push
- **Repository bloat**: 1,892 branches = significant git overhead
- **GitHub API rate limits**: Excessive branch operations may trigger rate limiting
- **Local .git folder bloat**: 1,892 branch refs consume disk space and slow git operations

### Operational Impact
- **Branch list pollution**: `git branch -r` output becomes unusable
- **CI/CD confusion**: Some CI systems scan all branches
- **Developer confusion**: Hard to find actual feature branches
- **Merge conflicts**: More branches = more potential merge scenarios

### Security Impact
- **Audit log noise**: Thousands of rollback branches make audit trails hard to review
- **Secret exposure risk**: If commits contained secrets, they're now in 1,892 places
- **Branch protection bypass**: Rollback branches may not have protection rules applied

## Recommended Solutions

### Option 1: Disable Hook-Based Rollback System (RECOMMENDED)

**Pros**: Simplest, fastest fix
**Cons**: Lose automatic rollback capability (but you have snapshot system)

```bash
# Disable the pre-push hook
cd "C:\Users\Richard Wilks\CLI_RESTART"
chmod -x .git/hooks/pre-push
# Or comment out the create-rollback.ps1 line

# Use the CLI orchestrator snapshot system instead
cli-orchestrator rollback list
cli-orchestrator rollback restore <snapshot-id>
```

### Option 2: Rate-Limit Rollback Branch Creation

**Pros**: Keeps rollback capability, reduces branch spam
**Cons**: More complex, still creates branches

Modify `C:/tools/.det-tools/bin/create-rollback.ps1`:

```powershell
# Only create rollback if last one is >1 hour old
$lastRollback = git for-each-ref --sort=-creatordate --format='%(creatordate:iso8601)' refs/heads/rollback/ 2>$null | Select-Object -First 1
if ($lastRollback) {
    $lastDate = [DateTime]::Parse($lastRollback)
    $hoursSince = ((Get-Date) - $lastDate).TotalHours
    if ($hoursSince -lt 1) {
        Write-Verbose "Skipping rollback creation: last rollback was $hoursSince hours ago"
        exit 0
    }
}

# Rest of script...
```

### Option 3: Move to Snapshot-Only System

**Pros**: More scalable, no branch pollution, better for large repos
**Cons**: Requires migration from branch-based rollback

1. Disable git hook rollback system
2. Enhance CLI orchestrator snapshot system
3. Add automatic snapshot creation on major operations
4. Implement retention policy in snapshot system

### Option 4: Background Cleanup Service

**Pros**: Keeps current system, adds better cleanup
**Cons**: Complex, requires separate service

Create a scheduled task/cron job:
```powershell
# Run daily at 2 AM
# Delete rollback branches older than 7 days
pwsh -File "C:\Users\Richard Wilks\CLI_RESTART\Remove-RollbackBranches.ps1" `
  -RepositoryPath "C:\Users\Richard Wilks\CLI_RESTART" `
  -Force `
  -Verify
```

## Immediate Action Plan

### Step 1: Disable Automatic Rollback Creation (URGENT)

```bash
cd "C:\Users\Richard Wilks\CLI_RESTART"

# Backup hooks
cp .git/hooks/pre-push .git/hooks/pre-push.backup

# Edit pre-push hook to comment out rollback creation
# Or simply disable it:
chmod -x .git/hooks/pre-push
```

### Step 2: Verify No New Branches Created

```bash
# Count current branches
git branch -r | grep rollback | wc -l

# Make a test push
echo "test" >> README.md
git add README.md
git commit -m "test: verify no rollback branches created"
git push origin main

# Count again - should be same number
git fetch --all
git branch -r | grep rollback | wc -l
```

### Step 3: Set Up Proper Retention Policy

```powershell
# Add to cron/Task Scheduler - run weekly
pwsh -File "C:\Users\Richard Wilks\CLI_RESTART\Remove-RollbackBranches.ps1" `
  -RepositoryPath "C:\Users\Richard Wilks\CLI_RESTART" `
  -Force `
  -NoVerify
```

### Step 4: Migrate to Snapshot System

```bash
# Use CLI orchestrator for rollbacks instead
cli-orchestrator rollback list
cli-orchestrator rollback restore <snapshot-id>

# Configure automatic snapshots
# Add to .ai/workflows/pre-merge.yaml
```

## Long-Term Architecture Recommendations

### 1. Unified Rollback Strategy
- **Choose ONE rollback mechanism**: Either git branches OR snapshots, not both
- **Recommendation**: Use snapshot system (scales better, no git pollution)

### 2. Proper Retention Policy
- Keep last 7 days of rollbacks
- Keep weekly rollbacks for 1 month
- Keep monthly rollbacks for 1 year
- Archive to cold storage after 1 year

### 3. Monitoring and Alerting
- Alert if rollback branch count exceeds threshold (e.g., 50)
- Alert if rollback creation rate exceeds 1 per hour
- Dashboard showing rollback usage and cleanup status

### 4. Documentation
- Document rollback procedures for team
- Clarify when to use rollback vs revert vs reset
- Add runbook for rollback recovery scenarios

## Files to Review/Modify

### Critical Files
1. `.git/hooks/pre-push` - Disable or rate-limit rollback creation
2. `C:/tools/.det-tools/bin/create-rollback.ps1` - Fix cleanup logic
3. `.git/hooks/post-merge` - Remove duplicate cleanup logic

### Supporting Files
4. `src/cli_multi_rapid/commands/rollback.py` - CLI snapshot system (preferred)
5. `tools/atomic-workflow-system/scripts/cleanup-rollback-branches.ps1` - Cleanup utility
6. `.gitignore` - Consider ignoring rollback audit logs

## Testing Recommendations

### Test 1: Verify Hook Disabled
```bash
git push origin main
git branch -r | grep rollback | wc -l  # Should not increase
```

### Test 2: Test Manual Rollback
```bash
cli-orchestrator rollback list
cli-orchestrator rollback restore <id> --dry-run
```

### Test 3: Test Cleanup Script
```bash
pwsh Remove-RollbackBranches.ps1 -RepositoryPath . -WhatIf -Verbose
```

## Conclusion

**Root Cause**: Pre-push git hook creating rollback branches on every push to main.

**Immediate Fix**: Disable `.git/hooks/pre-push` or comment out rollback creation logic.

**Long-Term Fix**: Migrate to snapshot-based rollback system (`cli-orchestrator rollback`) and establish proper retention policies.

**Prevention**:
- Monitor branch count
- Set up weekly cleanup automation
- Use snapshot system instead of git branches for rollbacks
- Document rollback procedures for team

---

**Next Steps**:
1. Disable pre-push hook immediately
2. Test that no new rollback branches are created
3. Set up weekly cleanup automation
4. Migrate team to snapshot-based rollback system
