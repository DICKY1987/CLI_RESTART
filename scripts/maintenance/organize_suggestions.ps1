# Suggested organization actions (review before running)
# Notes:
# - Many items are referenced by tasks or code; search and update references before moving.
# - Prefer archiving over deletion. Test after each move.

param(
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $root  # -> scripts/
$root = Split-Path -Parent $root  # -> repo root

function Invoke-MoveSafe {
    param(
        [Parameter(Mandatory)] [string]$From,
        [Parameter(Mandatory)] [string]$To
    )
    if (-not (Test-Path $From)) { Write-Host "Skip (missing): $From"; return }
    $destDir = Split-Path -Parent $To
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Force -Path $destDir | Out-Null }
    Write-Host "Plan: $From -> $To"
    if ($Execute) { Move-Item -LiteralPath $From -Destination $To -Force }
}

# 1) Move VS Code extension tooling under tools/
Invoke-MoveSafe -From (Join-Path $root 'vscode-extension') -To (Join-Path $root 'tools\vscode-extension')

# 2) Move tmp project into tools/ (if not actively used as temp)
Invoke-MoveSafe -From (Join-Path $root 'tmp\atomic-workflow-system') -To (Join-Path $root 'tools\atomic-workflow-system')

# 3) Optionally relocate CODEX_IMPLEMENTATION docs under docs/ (requires updating .vscode tasks and scripts)
# Invoke-MoveSafe -From (Join-Path $root 'CODEX_IMPLEMENTATION') -To (Join-Path $root 'docs\codex_implementation')

# 4) Archive stale artifacts by date
$archive = Join-Path $root ('archive\' + (Get-Date).ToString('yyyy-MM-dd'))
New-Item -ItemType Directory -Force -Path $archive | Out-Null
# Example: Archive a backup dir
Invoke-MoveSafe -From (Join-Path $root 'removal-backup-20251011-160634') -To (Join-Path $archive 'removal-backup-20251011-160634')

Write-Host ''
if ($Execute) { Write-Host 'Moves executed.' } else { Write-Host 'Dry plan printed. Run with -Execute to apply.' }
