#!/usr/bin/env pwsh
# Quick cleanup script - executes immediately

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Archive & Obsolete Files Cleanup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Change to project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Track stats
$removed = 0
$totalSize = 0

function Remove-AndLog {
    param(
        [string]$Path,
        [string]$Description
    )

    if (Test-Path $Path) {
        $size = if (Test-Path $Path -PathType Container) {
            (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        } else {
            (Get-Item $Path).Length
        }

        if ($null -eq $size) { $size = 0 }

        $sizeKB = [math]::Round($size / 1KB, 2)
        Write-Host "Removing: $Description" -ForegroundColor Yellow
        Write-Host "  Path: $Path" -ForegroundColor Gray
        Write-Host "  Size: $sizeKB KB" -ForegroundColor Gray

        try {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
            Write-Host "  SUCCESS" -ForegroundColor Green
            $script:removed++
            $script:totalSize += $size
        } catch {
            Write-Host "  FAILED: $_" -ForegroundColor Red
        }
        Write-Host ""
    } else {
        Write-Host "SKIP: $Description (not found)" -ForegroundColor DarkGray
        Write-Host ""
    }
}

# Phase 1: Remove archived scripts
Write-Host "PHASE 1: Archived Scripts" -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan
Remove-AndLog "scripts\archive" "Archived cleanup scripts directory"

# Phase 2: Remove old reports
Write-Host "PHASE 2: Old Reports" -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan
Remove-AndLog "docs\reports\2025-09-20" "September 2025 reports"

# Phase 3: Remove old manifest
Write-Host "PHASE 3: Old Cleanup Manifest" -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan
Remove-AndLog "cleanup-manifest-2025-10-18.txt" "Previous cleanup manifest"

# Phase 4: Remove coverage files
Write-Host "PHASE 4: Coverage Files" -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan
Remove-AndLog ".coverage" "Root coverage file"
Remove-AndLog "tools\atomic-workflow-system\.coverage" "Atomic workflow coverage file"

# Summary
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  CLEANUP COMPLETE" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Items removed: $removed" -ForegroundColor Green
Write-Host "Total size freed: $([math]::Round($totalSize / 1KB, 2)) KB ($([math]::Round($totalSize / 1MB, 3)) MB)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
