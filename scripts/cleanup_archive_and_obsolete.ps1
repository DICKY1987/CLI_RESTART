#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Safely remove archived, backup, legacy, and outdated files from the repository.

.DESCRIPTION
    This script removes identified obsolete files including:
    - Archived cleanup scripts (scripts/archive/)
    - Old reports from September (docs/reports/2025-09-20/)
    - Cleanup manifest from previous run
    - Coverage files (regenerated on test runs)
    - Activity logs (if large)

.PARAMETER DryRun
    If specified, shows what would be deleted without actually deleting.

.PARAMETER Force
    Skip confirmation prompts (use with caution).

.PARAMETER Verbose
    Show detailed progress information.

.EXAMPLE
    .\cleanup_archive_and_obsolete.ps1
    Run in dry-run mode (safe, preview only)

.EXAMPLE
    .\cleanup_archive_and_obsolete.ps1 -DryRun:$false
    Actually perform the cleanup (with confirmation)

.EXAMPLE
    .\cleanup_archive_and_obsolete.ps1 -DryRun:$false -Force
    Perform cleanup without confirmation prompts
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [bool]$DryRun = $true,

    [Parameter(Mandatory=$false)]
    [bool]$Force = $false,

    [Parameter(Mandatory=$false)]
    [bool]$VerboseOutput = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"

# Get script location and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Change to project root
Push-Location $ProjectRoot

try {
    # Create cleanup log directory
    $LogDir = Join-Path $ProjectRoot "logs"
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }

    # Create cleanup manifest
    $Timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
    $ManifestPath = Join-Path $LogDir "cleanup-manifest-$Timestamp.txt"
    $LogPath = Join-Path $LogDir "cleanup-log-$Timestamp.log"

    function Write-Log {
        param(
            [string]$Message,
            [string]$Level = "INFO"
        )
        $LogMessage = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
        Add-Content -Path $LogPath -Value $LogMessage

        switch ($Level) {
            "INFO"    { Write-Host $Message -ForegroundColor $ColorInfo }
            "SUCCESS" { Write-Host $Message -ForegroundColor $ColorSuccess }
            "WARNING" { Write-Host $Message -ForegroundColor $ColorWarning }
            "ERROR"   { Write-Host $Message -ForegroundColor $ColorError }
        }
    }

    function Get-FolderSize {
        param([string]$Path)
        if (Test-Path $Path) {
            $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue |
                     Measure-Object -Property Length -Sum).Sum
            return [math]::Round($size / 1KB, 2)
        }
        return 0
    }

    function Remove-ItemSafely {
        param(
            [string]$Path,
            [string]$Description,
            [ref]$Stats
        )

        if (-not (Test-Path $Path)) {
            Write-Log "SKIP: $Description (not found)" "WARNING"
            return
        }

        $isDirectory = Test-Path $Path -PathType Container
        $size = if ($isDirectory) { Get-FolderSize $Path } else {
            [math]::Round((Get-Item $Path).Length / 1KB, 2)
        }

        if ($DryRun) {
            Write-Log "[DRY-RUN] Would remove: $Description" "INFO"
            Write-Log "           Path: $Path" "INFO"
            Write-Log "           Size: $size KB" "INFO"
            Add-Content -Path $ManifestPath -Value "WOULD REMOVE: $Path ($size KB) - $Description"
            $Stats.Value.WouldRemoveCount++
            $Stats.Value.WouldRemoveSize += $size
        } else {
            Write-Log "Removing: $Description" "INFO"
            Write-Log "         Path: $Path" "INFO"
            Write-Log "         Size: $size KB" "INFO"

            try {
                if ($isDirectory) {
                    Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
                } else {
                    Remove-Item -Path $Path -Force -ErrorAction Stop
                }
                Write-Log "SUCCESS: Removed $Description" "SUCCESS"
                Add-Content -Path $ManifestPath -Value "REMOVED: $Path ($size KB) - $Description"
                $Stats.Value.RemovedCount++
                $Stats.Value.RemovedSize += $size
            } catch {
                Write-Log "ERROR: Failed to remove $Description - $_" "ERROR"
                Add-Content -Path $ManifestPath -Value "FAILED: $Path - $_"
                $Stats.Value.FailedCount++
            }
        }
    }

    # Initialize statistics
    $Stats = @{
        WouldRemoveCount = 0
        WouldRemoveSize = 0
        RemovedCount = 0
        RemovedSize = 0
        FailedCount = 0
    }

    # Header
    Write-Log "================================================" "INFO"
    Write-Log "  Archive & Obsolete Files Cleanup Script" "INFO"
    Write-Log "  Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"
    Write-Log "  Mode: $(if ($DryRun) { 'DRY-RUN (safe preview)' } else { 'EXECUTE' })" "INFO"
    Write-Log "================================================" "INFO"
    Write-Host ""

    # Confirmation for actual deletion
    if (-not $DryRun -and -not $Force) {
        Write-Log "WARNING: This will permanently delete files!" "WARNING"
        $confirmation = Read-Host "Are you sure you want to proceed? (yes/no)"
        if ($confirmation -ne "yes") {
            Write-Log "Cleanup cancelled by user." "WARNING"
            Pop-Location
            return
        }
        Write-Host ""
    }

    # Start cleanup manifest
    Add-Content -Path $ManifestPath -Value "CLEANUP MANIFEST"
    Add-Content -Path $ManifestPath -Value "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Add-Content -Path $ManifestPath -Value "Mode: $(if ($DryRun) { 'DRY-RUN' } else { 'EXECUTE' })"
    Add-Content -Path $ManifestPath -Value "Project: $ProjectRoot"
    Add-Content -Path $ManifestPath -Value "================================================"
    Add-Content -Path $ManifestPath -Value ""

    # Phase 1: Remove archived cleanup scripts
    Write-Log "PHASE 1: Archived Cleanup Scripts" "INFO"
    Write-Log "------------------------------------" "INFO"

    $archiveDir = Join-Path $ProjectRoot "scripts\archive"
    Remove-ItemSafely -Path $archiveDir -Description "Archived cleanup scripts directory" -Stats ([ref]$Stats)
    Write-Host ""

    # Phase 2: Remove old reports from September
    Write-Log "PHASE 2: Outdated Reports (September 2025)" "INFO"
    Write-Log "------------------------------------" "INFO"

    $reportsDir = Join-Path $ProjectRoot "docs\reports\2025-09-20"
    Remove-ItemSafely -Path $reportsDir -Description "Old reports from 2025-09-20" -Stats ([ref]$Stats)
    Write-Host ""

    # Phase 3: Remove cleanup manifest from previous run
    Write-Log "PHASE 3: Old Cleanup Manifest" "INFO"
    Write-Log "------------------------------------" "INFO"

    $oldManifest = Join-Path $ProjectRoot "cleanup-manifest-2025-10-18.txt"
    Remove-ItemSafely -Path $oldManifest -Description "Previous cleanup manifest" -Stats ([ref]$Stats)
    Write-Host ""

    # Phase 4: Remove coverage files (regenerated on test runs)
    Write-Log "PHASE 4: Coverage Files (Regenerated Artifacts)" "INFO"
    Write-Log "------------------------------------" "INFO"

    $coverageRoot = Join-Path $ProjectRoot ".coverage"
    Remove-ItemSafely -Path $coverageRoot -Description "Root coverage file" -Stats ([ref]$Stats)

    $coverageAtomic = Join-Path $ProjectRoot "tools\atomic-workflow-system\.coverage"
    Remove-ItemSafely -Path $coverageAtomic -Description "Atomic workflow system coverage file" -Stats ([ref]$Stats)
    Write-Host ""

    # Phase 5: Check and optionally truncate large log files
    Write-Log "PHASE 5: Activity Logs" "INFO"
    Write-Log "------------------------------------" "INFO"

    $activityLog = Join-Path $ProjectRoot "logs\activity.log"
    if (Test-Path $activityLog) {
        $logSize = [math]::Round((Get-Item $activityLog).Length / 1MB, 2)
        Write-Log "Activity log size: $logSize MB" "INFO"

        if ($logSize -gt 10) {
            Write-Log "Activity log is large (>10 MB)" "WARNING"
            if ($DryRun) {
                Write-Log "[DRY-RUN] Would truncate or archive activity.log" "INFO"
                Add-Content -Path $ManifestPath -Value "WOULD TRUNCATE: $activityLog ($logSize MB)"
            } else {
                # Archive the old log
                $archiveLogPath = Join-Path $LogDir "activity-archive-$Timestamp.log"
                Copy-Item -Path $activityLog -Destination $archiveLogPath
                Clear-Content -Path $activityLog
                Write-Log "SUCCESS: Archived and truncated activity.log" "SUCCESS"
                Add-Content -Path $ManifestPath -Value "ARCHIVED: $activityLog -> $archiveLogPath"
            }
        } else {
            Write-Log "Activity log size is acceptable (<10 MB)" "SUCCESS"
        }
    } else {
        Write-Log "No activity log found" "INFO"
    }
    Write-Host ""

    # Phase 6: Clean up empty directories
    Write-Log "PHASE 6: Empty Directories" "INFO"
    Write-Log "------------------------------------" "INFO"

    $emptyDirs = Get-ChildItem -Path $ProjectRoot -Recurse -Directory -ErrorAction SilentlyContinue |
                 Where-Object {
                     $_.FullName -notmatch '\\\.git\\' -and
                     $_.FullName -notmatch '\\\.venv\\' -and
                     $_.FullName -notmatch '\\node_modules\\' -and
                     (@(Get-ChildItem -Path $_.FullName -Force -ErrorAction SilentlyContinue)).Count -eq 0
                 } |
                 Sort-Object -Property FullName -Descending

    if ($emptyDirs) {
        Write-Log "Found $($emptyDirs.Count) empty directories" "INFO"
        foreach ($dir in $emptyDirs) {
            Remove-ItemSafely -Path $dir.FullName -Description "Empty directory: $($dir.Name)" -Stats ([ref]$Stats)
        }
    } else {
        Write-Log "No empty directories found" "SUCCESS"
    }
    Write-Host ""

    # Summary
    Write-Log "================================================" "INFO"
    Write-Log "  CLEANUP SUMMARY" "INFO"
    Write-Log "================================================" "INFO"

    if ($DryRun) {
        Write-Log "Mode: DRY-RUN (no files were actually deleted)" "WARNING"
        Write-Log "Items that would be removed: $($Stats.WouldRemoveCount)" "INFO"
        Write-Log "Total size to be freed: $([math]::Round($Stats.WouldRemoveSize / 1024, 2)) MB" "INFO"
        Write-Log "" "INFO"
        Write-Log "To actually perform cleanup, run:" "INFO"
        Write-Log "  .\scripts\cleanup_archive_and_obsolete.ps1 -DryRun:`$false" "INFO"
    } else {
        Write-Log "Items successfully removed: $($Stats.RemovedCount)" "SUCCESS"
        Write-Log "Total size freed: $([math]::Round($Stats.RemovedSize / 1024, 2)) MB" "SUCCESS"
        Write-Log "Failed operations: $($Stats.FailedCount)" $(if ($Stats.FailedCount -gt 0) { "ERROR" } else { "INFO" })
    }

    Write-Log "" "INFO"
    Write-Log "Manifest saved to: $ManifestPath" "INFO"
    Write-Log "Log saved to: $LogPath" "INFO"
    Write-Log "================================================" "INFO"

    # Save summary to manifest
    Add-Content -Path $ManifestPath -Value ""
    Add-Content -Path $ManifestPath -Value "SUMMARY"
    Add-Content -Path $ManifestPath -Value "================================================"
    if ($DryRun) {
        Add-Content -Path $ManifestPath -Value "Mode: DRY-RUN"
        Add-Content -Path $ManifestPath -Value "Items that would be removed: $($Stats.WouldRemoveCount)"
        Add-Content -Path $ManifestPath -Value "Total size to be freed: $([math]::Round($Stats.WouldRemoveSize / 1024, 2)) MB"
    } else {
        Add-Content -Path $ManifestPath -Value "Mode: EXECUTE"
        Add-Content -Path $ManifestPath -Value "Items removed: $($Stats.RemovedCount)"
        Add-Content -Path $ManifestPath -Value "Total size freed: $([math]::Round($Stats.RemovedSize / 1024, 2)) MB"
        Add-Content -Path $ManifestPath -Value "Failed operations: $($Stats.FailedCount)"
    }

} catch {
    Write-Log "CRITICAL ERROR: $_" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    throw
} finally {
    Pop-Location
}
