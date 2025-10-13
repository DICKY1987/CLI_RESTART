# Fast Cleanup Duplicate Files Script
# Skips .venv and other regenerable directories for speed

$ErrorActionPreference = "Stop"

$parentDir = "C:\Users\Richard Wilks"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fast Duplicate Cleanup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Items to delete without backup (safe, regenerable)
$skipBackupItems = @(
    ".venv",           # Regenerable with pip install
    ".ruff_cache",     # Regenerable cache
    ".pytest_cache",   # Regenerable cache
    "nul",             # Empty temp file
    "__pycache__"      # Python cache
)

# Items to delete with simple verification
$safeToDelete = @(
    "scripts",
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
    ".ai",
    "deploy",
    "specs"
)

$deleted = 0
$failed = 0

Write-Host "Phase 1: Removing regenerable items (no backup needed)" -ForegroundColor Yellow
Write-Host ""

foreach ($item in $skipBackupItems) {
    $itemPath = Join-Path $parentDir $item

    if (Test-Path $itemPath) {
        try {
            Write-Host "Removing: $item" -ForegroundColor White
            Remove-Item -Path $itemPath -Recurse -Force -ErrorAction Stop
            Write-Host "  [SUCCESS]" -ForegroundColor Green
            $deleted++
        } catch {
            Write-Host "  [FAILED] $_" -ForegroundColor Red
            $failed++
        }
    }
}

Write-Host ""
Write-Host "Phase 2: Removing duplicate project directories" -ForegroundColor Yellow
Write-Host ""

foreach ($item in $safeToDelete) {
    $itemPath = Join-Path $parentDir $item
    $insidePath = Join-Path "C:\Users\Richard Wilks\CLI_RESTART" $item

    if (Test-Path $itemPath) {
        # Quick verification that inside version exists
        if (Test-Path $insidePath) {
            try {
                Write-Host "Removing: $item (verified inside exists)" -ForegroundColor White
                Remove-Item -Path $itemPath -Recurse -Force -ErrorAction Stop
                Write-Host "  [SUCCESS]" -ForegroundColor Green
                $deleted++
            } catch {
                Write-Host "  [FAILED] $_" -ForegroundColor Red
                $failed++
            }
        } else {
            Write-Host "SKIPPING: $item (inside version not found!)" -ForegroundColor Red
            $failed++
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Additional Cleanup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cleanup temporary files
$tempFiles = @(
    "._chk2.py",
    "._chk_router.py",
    "._check_coord3.py",
    "._check_coord2.py",
    "._check_coord.py",
    "CON"
)

Write-Host "Removing temporary check files..." -ForegroundColor Yellow
foreach ($file in $tempFiles) {
    $filePath = Join-Path $parentDir $file
    if (Test-Path $filePath) {
        try {
            Remove-Item -Path $filePath -Force
            Write-Host "  Removed: $file" -ForegroundColor Green
            $deleted++
        } catch {
            Write-Host "  Failed: $file - $_" -ForegroundColor Red
            $failed++
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deleted: $deleted items" -ForegroundColor Green
Write-Host "Failed: $failed items" -ForegroundColor Red
Write-Host ""

Write-Host "Note: Manual review still needed for:" -ForegroundColor Yellow
Write-Host "  - ' ' (space directory) - outside is newer" -ForegroundColor White
Write-Host "  - Installation logs (*.log files)" -ForegroundColor White
Write-Host "  - Script files (if not in CLI_RESTART/scripts/)" -ForegroundColor White
Write-Host ""

# Check for old installation logs
$logFiles = Get-ChildItem -Path $parentDir -Filter "installation-*.log" -ErrorAction SilentlyContinue
if ($logFiles) {
    Write-Host "Found $($logFiles.Count) installation log files:" -ForegroundColor Yellow
    Write-Host "  To remove: Get-ChildItem '$parentDir\installation-*.log' | Remove-Item" -ForegroundColor Gray
    Write-Host ""
}

# Check for duplicate scripts
$scriptFiles = @(
    "verify-deepseek-setup.cmd",
    "verify-deepseek-setup.ps1",
    "opencode-deepseek-run.cmd",
    "opencode-deepseek-run.ps1",
    "opencode-deepseek.cmd",
    "opencode-deepseek.ps1"
)

Write-Host "Checking for duplicate script files..." -ForegroundColor Yellow
foreach ($script in $scriptFiles) {
    $outsidePath = Join-Path $parentDir $script
    $insidePath = Join-Path "C:\Users\Richard Wilks\CLI_RESTART\scripts" $script

    if ((Test-Path $outsidePath) -and (Test-Path $insidePath)) {
        Write-Host "  Duplicate found: $script" -ForegroundColor White
        Write-Host "    To remove: Remove-Item '$outsidePath'" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host ""
