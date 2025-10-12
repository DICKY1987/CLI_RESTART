#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
    Registers custom merge drivers for structural file merges
.DESCRIPTION
    Configures git to use jq/yq for JSON/YAML merges with audited fallbacks
#>

param([switch]$SkipToolCheck)

$ErrorActionPreference = 'Stop'

if (-not $SkipToolCheck) {
    Write-Host "ðŸ” Checking for merge tools..." -ForegroundColor Cyan
    & "$PSScriptRoot/Check-Tooling.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Some tools missing - fallbacks will be used"
    }
}

Write-Host "`nâš™ï¸  Registering JSON merge driver..." -ForegroundColor Cyan

# JSON structural merge with audited fallback
git config merge.json-struct.name "JSON structural merge (jq)"
git config merge.json-struct.driver "powershell -NoProfile -Command `"`$ErrorActionPreference='Stop'; `$fallback=`$false; if(Get-Command jq -EA SilentlyContinue){try{jq -S -s 'reduce .[] as `$d ({}; . * `$d)' '%O' '%A' '%B' > '%A'; if(`$LASTEXITCODE -eq 0){exit 0}}catch{`$fallback=`$true}}else{`$fallback=`$true}; if(`$fallback){`$audit=@{file='%A';strategy='json-struct';fallback_used=`$true;reason='jq unavailable or failed';timestamp=(Get-Date).ToString('o')}|ConvertTo-Json -Compress; Add-Content -Path '.git/merge-fallback.log' -Value `$audit; Copy-Item '%B' '%A' -Force; exit 0}`""

Write-Host "âš™ï¸  Registering YAML merge driver..." -ForegroundColor Cyan

# YAML structural merge with audited fallback
git config merge.yaml-struct.name "YAML structural merge (yq)"
git config merge.yaml-struct.driver "powershell -NoProfile -Command `"`$ErrorActionPreference='Stop'; `$fallback=`$false; if(Get-Command yq -EA SilentlyContinue){try{yq -oy -s '.[0] * .[2]' '%O' '%A' '%B' > '%A'; if(`$LASTEXITCODE -eq 0){exit 0}}catch{`$fallback=`$true}}else{`$fallback=`$true}; if(`$fallback){`$audit=@{file='%A';strategy='yaml-struct';fallback_used=`$true;reason='yq unavailable or failed';timestamp=(Get-Date).ToString('o')}|ConvertTo-Json -Compress; Add-Content -Path '.git/merge-fallback.log' -Value `$audit; Copy-Item '%B' '%A' -Force; exit 0}`""

Write-Host "âš™ï¸  Configuring manual merge driver..." -ForegroundColor Cyan
# Manual driver exits with conflict to force human review
git config merge.manual.name "Requires manual resolution"
git config merge.manual.driver "exit 1"

Write-Host "âš™ï¸  Enabling git rerere..." -ForegroundColor Cyan
git config rerere.enabled true
git config rerere.autoupdate true

Write-Host "`nâœ… Merge drivers registered successfully" -ForegroundColor Green
Write-Host "Fallback usage will be logged to: .git/merge-fallback.log" -ForegroundColor Gray
