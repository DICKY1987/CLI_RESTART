#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
    Automated merge-train workflow for workstream branches
.DESCRIPTION
    Performs policy-driven automated merges with verification gates and quarantine routing
.PARAMETER SkipVerification
    Skip verification gates (hooks, tests, security scans)
.PARAMETER Verbose
    Enable verbose output
.EXAMPLE
    .\AutoMerge-Workstream.ps1 -Verbose
.EXAMPLE
    .\AutoMerge-Workstream.ps1 -SkipVerification -Verbose
#>

param(
    [switch]$SkipVerification,
    [switch]$Verbose
)

$ErrorActionPreference = 'Stop'
$VerbosePreference = if ($Verbose) { 'Continue' } else { 'SilentlyContinue' }

# Initialize audit record
$audit = @{
    timestamp = (Get-Date).ToUniversalTime().ToString('o')
    run_id = $env:GITHUB_RUN_ID ?? "local-$(Get-Date -Format 'yyyyMMddHHmmss')"
    branch_source = ""
    branch_target = "main"
    policy_version = ""
    strategies_applied = @()
    fallbacks_used = @()
    conflicts_found = 0
    verification_gates = @{}
    outcome = "unknown"
    quarantine_reason = $null
    artifacts = @()
    errors = @()
}

function Write-AuditLog {
    param($Record, $Path)
    $jsonLine = $Record | ConvertTo-Json -Depth 10 -Compress
    Add-Content -Path $Path -Value $jsonLine -Encoding UTF8
}

function Move-ToQuarantine {
    param([string]$Reason, [string]$SourceBranch)

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $quarantineBranch = "needs-human/$SourceBranch-$timestamp"

    Write-Host "`n🔒 QUARANTINE TRIGGERED" -ForegroundColor Red
    Write-Host "Reason: $Reason" -ForegroundColor Red
    Write-Host "Creating quarantine branch: $quarantineBranch" -ForegroundColor Yellow

    try {
        # Create quarantine branch from current HEAD
        git branch $quarantineBranch HEAD

        # Push quarantine branch
        git push origin $quarantineBranch

        Write-Host "✅ Quarantine branch created: $quarantineBranch" -ForegroundColor Yellow

        $audit.outcome = "quarantined"
        $audit.quarantine_reason = $Reason

        return $true
    } catch {
        Write-Error "❌ Failed to create quarantine branch: $_"
        $audit.errors += "Quarantine creation failed: $_"
        return $false
    }
}

Write-Host "`n🚂 Merge Train - Automated Workstream Merge" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Gray

# Step 1: Validate we're on a workstream branch
Write-Host "`n📍 Step 1: Validate branch..." -ForegroundColor Cyan
$currentBranch = git branch --show-current
$audit.branch_source = $currentBranch

if (-not $currentBranch.StartsWith("workstream/")) {
    Write-Error "❌ Not on a workstream/* branch. Current: $currentBranch"
    $audit.outcome = "failed"
    $audit.errors += "Not on workstream branch"
    Write-AuditLog $audit ".git/merge-audit.jsonl"
    exit 1
}

Write-Host "✅ On workstream branch: $currentBranch" -ForegroundColor Green

# Step 2: Load and validate policy
Write-Host "`n📋 Step 2: Load merge policy..." -ForegroundColor Cyan
if (-not (Test-Path ".merge-policy.yaml")) {
    Write-Error "❌ .merge-policy.yaml not found"
    $audit.outcome = "failed"
    $audit.errors += "Policy file missing"
    Write-AuditLog $audit ".git/merge-audit.jsonl"
    exit 1
}

try {
    # Parse policy (python fallback)
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $yamlPyScript = 'import sys, yaml, json; json.dump(yaml.safe_load(sys.stdin), sys.stdout)'
        $policy = Get-Content ".merge-policy.yaml" -Raw | python -c $yamlPyScript | ConvertFrom-Json
        $audit.policy_version = $policy.policy_version
        Write-Host "✅ Policy loaded: v$($policy.policy_version)" -ForegroundColor Green
    } else {
        Write-Warning "Python not available - using basic policy handling"
        $policy = $null
    }
} catch {
    Write-Error "❌ Failed to parse policy: $_"
    $audit.outcome = "failed"
    $audit.errors += "Policy parse error: $_"
    Write-AuditLog $audit ".git/merge-audit.jsonl"
    exit 1
}

# Step 3: Fetch latest main
Write-Host "`n🔄 Step 3: Fetch latest main..." -ForegroundColor Cyan
try {
    git fetch origin main --quiet
    Write-Host "✅ Fetched latest main" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to fetch main: $_"
    $audit.outcome = "failed"
    $audit.errors += "Fetch failed: $_"
    Write-AuditLog $audit ".git/merge-audit.jsonl"
    exit 1
}

# Step 4: Check branch priority
Write-Host "`n🎯 Step 4: Check branch priority..." -ForegroundColor Cyan
$sourcePriority = 60 # Default for workstream/*
$targetPriority = 100 # main branch

if ($policy -and $policy.branch_priority) {
    $sourcePriority = $policy.branch_priority."workstream/*" ?? 60
    $targetPriority = $policy.branch_priority.main ?? 100
}

Write-Host "   Source priority: $sourcePriority" -ForegroundColor Gray
Write-Host "   Target priority: $targetPriority" -ForegroundColor Gray

if ($sourcePriority -ge $targetPriority) {
    Write-Warning "⚠️ Source priority >= target (unusual, but allowed)"
}

# Step 5: Setup merge drivers
Write-Host "`n⚙️ Step 5: Setup merge drivers..." -ForegroundColor Cyan
$setupScript = Join-Path $PSScriptRoot "setup-merge-drivers.ps1"
if (Test-Path $setupScript) {
    try {
        & $setupScript -SkipToolCheck
        Write-Host "✅ Merge drivers configured" -ForegroundColor Green
        $audit.strategies_applied += "merge-drivers"
    } catch {
        Write-Warning "⚠️ Merge driver setup warning: $_"
        $audit.fallbacks_used += "merge-driver-setup-failed"
    }
} else {
    Write-Warning "⚠️ setup-merge-drivers.ps1 not found - using Git defaults"
    $audit.fallbacks_used += "no-custom-drivers"
}

# Step 6: Attempt merge
Write-Host "`n🔀 Step 6: Attempting merge to main..." -ForegroundColor Cyan
$mergeSuccess = $false

try {
    # Switch to main
    git checkout main

    # Attempt merge with rerere
    $mergeResult = git merge $currentBranch --no-ff -m "feat: Merge $currentBranch via merge-train" 2>&1

    if ($LASTEXITCODE -eq 0) {
        $mergeSuccess = $true
        Write-Host "✅ Merge successful (no conflicts)" -ForegroundColor Green
    } else {
        # Conflicts detected
        $conflictFiles = git diff --name-only --diff-filter=U
        $audit.conflicts_found = ($conflictFiles | Measure-Object).Count

        Write-Host "⚠️ Conflicts detected in $($audit.conflicts_found) files" -ForegroundColor Yellow

        # Check safety limits
        if ($policy -and $policy.safety_limits) {
            $maxFiles = $policy.safety_limits.max_files_with_conflicts ?? 20
            $action = $policy.safety_limits.action_on_exceed ?? "quarantine"

            if ($audit.conflicts_found -gt $maxFiles) {
                Write-Host "❌ Conflict count exceeds safety limit ($maxFiles)" -ForegroundColor Red

                # Abort merge
                git merge --abort

                # Move to quarantine
                git checkout $currentBranch
                Move-ToQuarantine "Conflict count ($($audit.conflicts_found)) exceeds safety limit ($maxFiles)" $currentBranch
                Write-AuditLog $audit ".git/merge-audit.jsonl"
                exit 1
            }
        }

        # Conflicts within limits - try rerere
        Write-Host "🔄 Applying rerere resolutions..." -ForegroundColor Cyan
        git rerere

        # Check if rerere resolved everything
        $remainingConflicts = git diff --name-only --diff-filter=U
        if (-not $remainingConflicts) {
            Write-Host "✅ Rerere resolved all conflicts!" -ForegroundColor Green
            git add -A
            git commit --no-edit
            $mergeSuccess = $true
            $audit.strategies_applied += "rerere"
        } else {
            Write-Host "❌ Rerere could not resolve all conflicts" -ForegroundColor Red
            git merge --abort
            git checkout $currentBranch
            Move-ToQuarantine "Manual conflict resolution required" $currentBranch
            Write-AuditLog $audit ".git/merge-audit.jsonl"
            exit 1
        }
    }
} catch {
    Write-Error "❌ Merge failed: $_"
    $audit.outcome = "failed"
    $audit.errors += "Merge error: $_"

    # Ensure we're back on source branch
    try { git merge --abort } catch {}
    try { git checkout $currentBranch } catch {}

    Write-AuditLog $audit ".git/merge-audit.jsonl"
    exit 1
}

# Step 7: Verification gates
if ($mergeSuccess -and -not $SkipVerification) {
    Write-Host "`n🔍 Step 7: Running verification gates..." -ForegroundColor Cyan

    # Gate 1: Pre-commit hooks
    Write-Host "   📝 Running pre-commit hooks..." -ForegroundColor Cyan
    try {
        if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
            pre-commit run --all-files --show-diff-on-failure
            if ($LASTEXITCODE -eq 0) {
                $audit.verification_gates.pre_commit = "pass"
                Write-Host "   ✅ Pre-commit hooks passed" -ForegroundColor Green
            } else {
                $audit.verification_gates.pre_commit = "fail"
                Write-Host "   ❌ Pre-commit hooks failed" -ForegroundColor Red

                # Rollback merge
                git reset --hard HEAD~1
                git checkout $currentBranch
                Move-ToQuarantine "Pre-commit hooks failed" $currentBranch
                Write-AuditLog $audit ".git/merge-audit.jsonl"
                exit 1
            }
        } else {
            $audit.verification_gates.pre_commit = "skipped"
            Write-Host "   ⚠️ pre-commit not installed, skipping" -ForegroundColor Yellow
        }
    } catch {
        $audit.verification_gates.pre_commit = "error"
        $audit.errors += "Pre-commit error: $_"
        Write-Warning "   ⚠️ Pre-commit error: $_"
    }

    # Gate 2: Integration tests (if defined in policy)
    if ($policy -and $policy.verification.integration_tests) {
        Write-Host "   🧪 Running integration tests..." -ForegroundColor Cyan
        foreach ($test in $policy.verification.integration_tests) {
            try {
                $testCmd = $test.command
                Invoke-Expression $testCmd
                if ($LASTEXITCODE -eq 0) {
                    $audit.verification_gates.integration_tests = "pass"
                    Write-Host "   ✅ Integration tests passed" -ForegroundColor Green
                } else {
                    $audit.verification_gates.integration_tests = "fail"
                    Write-Host "   ❌ Integration tests failed" -ForegroundColor Red

                    if ($test.required) {
                        # Rollback merge
                        git reset --hard HEAD~1
                        git checkout $currentBranch
                        Move-ToQuarantine "Integration tests failed" $currentBranch
                        Write-AuditLog $audit ".git/merge-audit.jsonl"
                        exit 1
                    }
                }
            } catch {
                $audit.verification_gates.integration_tests = "error"
                $audit.errors += "Integration test error: $_"
                Write-Warning "   ⚠️ Test error: $_"
            }
        }
    }

    # Gate 3: Security checks (if defined in policy)
    if ($policy -and $policy.verification.security_checks) {
        Write-Host "   🔒 Running security checks..." -ForegroundColor Cyan
        foreach ($check in $policy.verification.security_checks) {
            try {
                $checkCmd = $check.command
                Invoke-Expression $checkCmd
                if ($LASTEXITCODE -eq 0) {
                    $audit.verification_gates.security_checks = "pass"
                    Write-Host "   ✅ Security checks passed" -ForegroundColor Green
                } else {
                    $audit.verification_gates.security_checks = "fail"
                    Write-Host "   ❌ Security checks failed" -ForegroundColor Red

                    if ($check.required) {
                        # Rollback merge
                        git reset --hard HEAD~1
                        git checkout $currentBranch
                        Move-ToQuarantine "Security checks failed" $currentBranch
                        Write-AuditLog $audit ".git/merge-audit.jsonl"
                        exit 1
                    }
                }
            } catch {
                $audit.verification_gates.security_checks = "error"
                $audit.errors += "Security check error: $_"
                Write-Warning "   ⚠️ Security check error: $_"
            }
        }
    }
} elseif ($SkipVerification) {
    Write-Host "`n⚠️ Step 7: Verification SKIPPED (as requested)" -ForegroundColor Yellow
    $audit.verification_gates.skipped = $true
}

# Step 8: Push to main
if ($mergeSuccess) {
    Write-Host "`n🚀 Step 8: Pushing to main..." -ForegroundColor Cyan
    try {
        git push origin main
        Write-Host "✅ Pushed to main successfully!" -ForegroundColor Green

        $audit.outcome = "merged"
        $audit.artifacts += ".git/merge-fallback.log"

        # Collect fallback logs if they exist
        if (Test-Path ".git/merge-fallback.log") {
            $fallbackLog = Get-Content ".git/merge-fallback.log" | ConvertFrom-Json
            $audit.fallbacks_used += $fallbackLog | ForEach-Object { $_.strategy }
        }

    } catch {
        Write-Error "❌ Failed to push to main: $_"
        $audit.outcome = "failed"
        $audit.errors += "Push failed: $_"
        Write-AuditLog $audit ".git/merge-audit.jsonl"
        exit 1
    }
}

# Step 9: Write audit logs
Write-Host "`n📝 Step 9: Writing audit logs..." -ForegroundColor Cyan

# Ensure audit directory exists
$auditDir = ".runs/audit"
if (-not (Test-Path $auditDir)) {
    New-Item -ItemType Directory -Path $auditDir -Force | Out-Null
}

# Write to both locations
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$auditFile = "$auditDir/merge-$timestamp.jsonl"

Write-AuditLog $audit ".git/merge-audit.jsonl"
Write-AuditLog $audit $auditFile

Write-Host "✅ Audit logs written:" -ForegroundColor Green
Write-Host "   • .git/merge-audit.jsonl" -ForegroundColor Gray
Write-Host "   • $auditFile" -ForegroundColor Gray

# Final summary
Write-Host "`n" + ("=" * 70) -ForegroundColor Gray
Write-Host "📊 Merge Train Summary" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Gray
Write-Host "Branch: $($audit.branch_source) → $($audit.branch_target)" -ForegroundColor Gray
Write-Host "Policy: v$($audit.policy_version)" -ForegroundColor Gray
Write-Host "Strategies: $($audit.strategies_applied -join ', ')" -ForegroundColor Gray
Write-Host "Conflicts: $($audit.conflicts_found)" -ForegroundColor Gray
Write-Host "Outcome: $($audit.outcome.ToUpper())" -ForegroundColor $(if ($audit.outcome -eq 'merged') { 'Green' } elseif ($audit.outcome -eq 'quarantined') { 'Yellow' } else { 'Red' })

if ($audit.outcome -eq 'merged') {
    Write-Host "`n✅ MERGE TRAIN COMPLETE - Changes merged to main" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️ MERGE TRAIN INCOMPLETE - Check logs for details" -ForegroundColor Yellow
    exit 1
}
