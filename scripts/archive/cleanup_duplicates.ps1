# Cleanup Duplicate Files Script
# This script removes old duplicate directories/files from parent directory
# Based on analysis showing INSIDE versions are newer

$ErrorActionPreference = "Stop"

$parentDir = "C:\Users\Richard Wilks"
$backupDir = "$parentDir\CLI_RESTART_duplicates_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Duplicate Cleanup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# List of items to delete (INSIDE is newer based on analysis)
$itemsToDelete = @(
    "scripts",
    ".venv",
    "nul",
    ".gemini",
    "workflows",
    "tests",
    "state",
    "logs",
    "config",
    "alembic",
    "artifacts",
    ".vscode",
    "CLI_PY_GUI",
    ".github",
    ".git-rewrite",
    "src",
    ".ruff_cache",
    ".ai",
    "deploy",
    "specs",
    ".pytest_cache"
)

# Special case: " " (space directory) - OUTSIDE is NEWER, need to check manually
$manualReviewItems = @(" ")

Write-Host "Creating backup directory: $backupDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$deleted = 0
$failed = 0
$backed_up = 0

# Delete items where INSIDE is newer
foreach ($item in $itemsToDelete) {
    $itemPath = Join-Path $parentDir $item

    if (Test-Path $itemPath) {
        $backupPath = Join-Path $backupDir $item

        try {
            Write-Host "Processing: $item" -ForegroundColor White

            # Create backup first
            Write-Host "  - Creating backup..." -ForegroundColor Gray
            if (Test-Path $itemPath -PathType Container) {
                Copy-Item -Path $itemPath -Destination $backupPath -Recurse -Force
            } else {
                Copy-Item -Path $itemPath -Destination $backupPath -Force
            }
            $backed_up++

            # Remove original
            Write-Host "  - Removing old version..." -ForegroundColor Gray
            Remove-Item -Path $itemPath -Recurse -Force

            Write-Host "  [SUCCESS] Deleted (backup created)" -ForegroundColor Green
            $deleted++

        } catch {
            Write-Host "  [FAILED] $_" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "Skipping (not found): $item" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Manual Review Required" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Items that need manual review
foreach ($item in $manualReviewItems) {
    $itemPath = Join-Path $parentDir $item
    if (Test-Path $itemPath) {
        Write-Host "[$item]" -ForegroundColor Yellow
        Write-Host "  Path: $itemPath" -ForegroundColor White
        Write-Host "  Note: OUTSIDE is NEWER - needs manual inspection" -ForegroundColor Yellow
        Write-Host ""
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deleted: $deleted items" -ForegroundColor Green
Write-Host "Backed up: $backed_up items" -ForegroundColor Yellow
Write-Host "Failed: $failed items" -ForegroundColor Red
Write-Host "Manual review: $($manualReviewItems.Count) items" -ForegroundColor Yellow
Write-Host ""
Write-Host "Backup location: $backupDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "To restore if needed:" -ForegroundColor White
Write-Host "  Copy-Item -Path '$backupDir\*' -Destination '$parentDir' -Recurse -Force" -ForegroundColor Gray
Write-Host ""

# Additional files that might need cleanup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Additional Cleanup Candidates" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "These files in parent directory should be manually reviewed:" -ForegroundColor White
Write-Host ""

$additionalCleanup = @(
    "*.log",
    "*.backup",
    "._chk*.py",
    "CON",
    "*.txt" # Review case by case
)

foreach ($pattern in $additionalCleanup) {
    $items = Get-ChildItem -Path $parentDir -Filter $pattern -ErrorAction SilentlyContinue
    if ($items) {
        Write-Host "  Pattern: $pattern" -ForegroundColor Yellow
        foreach ($file in $items) {
            Write-Host "    - $($file.Name)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "Review these files manually and delete as appropriate." -ForegroundColor White
Write-Host ""
