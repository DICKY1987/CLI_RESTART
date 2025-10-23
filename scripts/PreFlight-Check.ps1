#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
    Pre-flight conflict analysis before merge
.DESCRIPTION
    Analyzes potential merge conflicts and validates environment before merge-train execution
.PARAMETER Target
    Target branch to merge into (default: origin/main)
.PARAMETER Verbose
    Enable verbose output
.EXAMPLE
    .\PreFlight-Check.ps1 -Target origin/main -Verbose
#>

param(
    [string]$Target = "origin/main",
    [switch]$Verbose
)

$ErrorActionPreference = 'Continue'
$VerbosePreference = if ($Verbose) { 'Continue' } else { 'SilentlyContinue' }

# Initialize result object
$result = @{
    timestamp = (Get-Date).ToUniversalTime().ToString('o')
    conflicts_detected = $false
    conflict_files = @()
    total_conflicts = 0
    exceeds_safety_limits = $false
    recommendation = "proceed"
    checks = @{
        tooling = "unknown"
        policy = "unknown"
        fetch = "unknown"
        merge_simulation = "unknown"
    }
    errors = @()
}

Write-Host "`n🚀 PreFlight Merge Conflict Analysis" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "Target: $Target" -ForegroundColor Gray
Write-Host "Current Branch: $(git branch --show-current)" -ForegroundColor Gray
Write-Host ""

# Check 1: Validate tooling
Write-Host "📦 Checking tooling..." -ForegroundColor Cyan
try {
    $toolCheckScript = Join-Path $PSScriptRoot "Check-Tooling.ps1"
    if (Test-Path $toolCheckScript) {
        & $toolCheckScript
        if ($LASTEXITCODE -eq 0) {
            $result.checks.tooling = "pass"
            Write-Verbose "✅ Tooling check passed"
        } else {
            $result.checks.tooling = "warning"
            Write-Warning "⚠️ Some optional tools missing (non-blocking)"
        }
    } else {
        $result.checks.tooling = "skipped"
        Write-Warning "Check-Tooling.ps1 not found, skipping"
    }
} catch {
    $result.checks.tooling = "error"
    $result.errors += "Tooling check failed: $_"
    Write-Warning "⚠️ Tooling check error: $_"
}

# Check 2: Validate policy
Write-Host "`n📋 Validating merge policy..." -ForegroundColor Cyan
try {
    $policyCheckScript = Join-Path $PSScriptRoot "Validate-Policy.ps1"
    if (Test-Path $policyCheckScript) {
        & $policyCheckScript
        if ($LASTEXITCODE -eq 0) {
            $result.checks.policy = "pass"
            Write-Verbose "✅ Policy validation passed"
        } else {
            $result.checks.policy = "fail"
            $result.errors += "Policy validation failed"
            Write-Error "❌ Policy validation failed"
        }
    } else {
        $result.checks.policy = "skipped"
        Write-Warning "Validate-Policy.ps1 not found, skipping"
    }
} catch {
    $result.checks.policy = "error"
    $result.errors += "Policy validation error: $_"
    Write-Warning "⚠️ Policy validation error: $_"
}

# Check 3: Fetch latest from target
Write-Host "`n🔄 Fetching latest from $Target..." -ForegroundColor Cyan
try {
    git fetch origin --quiet
    if ($LASTEXITCODE -eq 0) {
        $result.checks.fetch = "pass"
        Write-Verbose "✅ Fetch successful"
    } else {
        $result.checks.fetch = "fail"
        $result.errors += "Git fetch failed"
        Write-Warning "⚠️ Git fetch failed"
    }
} catch {
    $result.checks.fetch = "error"
    $result.errors += "Fetch error: $_"
    Write-Warning "⚠️ Fetch error: $_"
}

# Check 4: Merge simulation
Write-Host "`n🔍 Simulating merge with $Target..." -ForegroundColor Cyan
try {
    $currentBranch = git branch --show-current

    # Use git merge-tree to simulate merge without touching working directory
    $mergeOutput = git merge-tree $(git merge-base HEAD $Target) HEAD $Target 2>&1

    # Parse merge-tree output for conflicts
    $conflictMarkers = $mergeOutput | Select-String -Pattern "^<<<<<<< " -AllMatches

    if ($conflictMarkers) {
        $result.conflicts_detected = $true
        $result.checks.merge_simulation = "conflicts_found"

        # Extract conflict files from merge-tree output
        $conflictLines = $mergeOutput | Select-String -Pattern "^(?:changed in both|deleted in|added in)" -AllMatches
        $result.conflict_files = @($conflictLines | ForEach-Object { $_.Line -replace '^.*:\s*', '' } | Select-Object -Unique)
        $result.total_conflicts = $conflictMarkers.Matches.Count

        Write-Warning "⚠️ Conflicts detected: $($result.total_conflicts) conflict markers in $($result.conflict_files.Count) files"

        # Load safety limits from policy
        if (Test-Path ".merge-policy.yaml") {
            try {
                # Try to parse YAML (using python fallback if needed)
                if (Get-Command python -ErrorAction SilentlyContinue) {
                    $yamlPyScript = 'import sys, yaml, json; json.dump(yaml.safe_load(sys.stdin), sys.stdout)'
                    $policy = Get-Content ".merge-policy.yaml" -Raw | python -c $yamlPyScript | ConvertFrom-Json

                    $maxConflicts = $policy.safety_limits.max_conflict_size_lines
                    $maxFiles = $policy.safety_limits.max_files_with_conflicts

                    if ($result.total_conflicts -gt $maxConflicts -or $result.conflict_files.Count -gt $maxFiles) {
                        $result.exceeds_safety_limits = $true
                        $result.recommendation = "quarantine"
                        Write-Warning "❌ SAFETY LIMITS EXCEEDED - Recommend quarantine"
                    } else {
                        $result.recommendation = "proceed_with_caution"
                        Write-Host "⚠️ Conflicts within safety limits - Can proceed with human review" -ForegroundColor Yellow
                    }
                }
            } catch {
                Write-Verbose "Could not load safety limits: $_"
            }
        }

        # Display conflict files
        if ($result.conflict_files.Count -gt 0 -and $result.conflict_files.Count -le 10) {
            Write-Host "`nConflicting files:" -ForegroundColor Yellow
            $result.conflict_files | ForEach-Object { Write-Host "  • $_" -ForegroundColor Gray }
        } elseif ($result.conflict_files.Count -gt 10) {
            Write-Host "`nConflicting files (first 10):" -ForegroundColor Yellow
            $result.conflict_files | Select-Object -First 10 | ForEach-Object { Write-Host "  • $_" -ForegroundColor Gray }
            Write-Host "  ... and $($result.conflict_files.Count - 10) more" -ForegroundColor Gray
        }
    } else {
        $result.checks.merge_simulation = "pass"
        $result.recommendation = "proceed"
        Write-Host "✅ No conflicts detected - safe to merge" -ForegroundColor Green
    }
} catch {
    $result.checks.merge_simulation = "error"
    $result.errors += "Merge simulation error: $_"
    Write-Warning "⚠️ Merge simulation error: $_"
}

# Output results
Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "📊 PreFlight Summary" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

# Summary
$statusSymbol = if ($result.conflicts_detected) { "⚠️" } else { "✅" }
$statusColor = if ($result.conflicts_detected) { "Yellow" } else { "Green" }
Write-Host "$statusSymbol Conflicts: $($result.conflicts_detected)" -ForegroundColor $statusColor
Write-Host "   Files affected: $($result.conflict_files.Count)" -ForegroundColor Gray
Write-Host "   Total conflicts: $($result.total_conflicts)" -ForegroundColor Gray
Write-Host "   Safety limits: $(if ($result.exceeds_safety_limits) { '❌ EXCEEDED' } else { '✅ OK' })" -ForegroundColor $(if ($result.exceeds_safety_limits) { 'Red' } else { 'Green' })
Write-Host "   Recommendation: $($result.recommendation.ToUpper())" -ForegroundColor $(if ($result.recommendation -eq 'quarantine') { 'Red' } elseif ($result.recommendation -eq 'proceed_with_caution') { 'Yellow' } else { 'Green' })

# Output JSON for CI consumption
Write-Host "`n📄 JSON Output:" -ForegroundColor Cyan
$jsonOutput = $result | ConvertTo-Json -Depth 10 -Compress
Write-Output $jsonOutput

# Always exit 0 (CI uses continue-on-error)
Write-Host "`n✅ PreFlight analysis complete" -ForegroundColor Green
exit 0
