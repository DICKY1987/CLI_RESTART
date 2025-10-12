#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
    Validates .merge-policy.yaml configuration
.DESCRIPTION
    Checks for syntax errors, conflicting rules, and security issues
#>

$ErrorActionPreference = 'Stop'
$issues = @()

function Add-Issue($severity, $message) {
    $script:issues += [PSCustomObject]@{
        Severity = $severity
        Message = $message
    }
}

# Check file exists
if (-not (Test-Path ".merge-policy.yaml")) {
    Write-Error ".merge-policy.yaml not found"
    exit 1
}

# Parse YAML (requires PowerShell-Yaml or python)
try {
    # Check for pwsh module first
    if (-not (Get-Module -ListAvailable -Name PowerShell-Yaml)) {
        Write-Warning "PowerShell-Yaml module not found. Install with: Install-Module PowerShell-Yaml"
        Write-Warning "Attempting to use python as a fallback to parse YAML..."
        if (Get-Command python -ErrorAction SilentlyContinue) {
             $yamlPyScript = 'import sys, yaml, json; json.dump(yaml.safe_load(sys.stdin), sys.stdout)'
             $policy = Get-Content ".merge-policy.yaml" -Raw | python -c $yamlPyScript | ConvertFrom-Json
        } else {
            throw "Neither PowerShell-Yaml nor Python is available to parse the policy file."
        }
    } else {
         $policy = Get-Content ".merge-policy.yaml" -Raw | ConvertFrom-Yaml
    }
} catch {
    Write-Error "Failed to parse .merge-policy.yaml: $_"
    exit 1
}

# Validate version
if (-not $policy.policy_version) {
    Add-Issue "ERROR" "Missing policy_version field"
}

# Check for conflicting path strategies
$patterns = @{}
foreach ($rule in $policy.path_strategies) {
    if ($patterns.ContainsKey($rule.pattern)) {
        Add-Issue "WARNING" "Duplicate pattern: $($rule.pattern)"
    }
    $patterns[$rule.pattern] = $rule.strategy
}

# Validate security-sensitive files have quarantine enabled
$securityPatterns = @("Dockerfile", "requirements.txt", "*.mod", "*.toml")
foreach ($pattern in $securityPatterns) {
    $rule = $policy.path_strategies | Where-Object { $_.pattern -eq $pattern }
    if ($rule -and -not $rule.quarantine_on_conflict) {
        Add-Issue "WARNING" "Security-sensitive pattern '$pattern' should have quarantine_on_conflict: true"
    }
}

# Validate branch priorities are ordered correctly
if ($policy.branch_priority) {
    $mainPriority = $policy.branch_priority.main
    $featurePriority = $policy.branch_priority."feature/*"
    if ($featurePriority -ge $mainPriority) {
        Add-Issue "ERROR" "Feature branches should have lower priority than main"
    }
}

# Validate safety limits
if (-not $policy.safety_limits) {
    Add-Issue "WARNING" "No safety_limits defined - large conflicts may auto-resolve incorrectly"
}

# Report results
if ($issues.Count -eq 0) {
    Write-Host "âœ… Policy validation passed" -ForegroundColor Green
    exit 0
}

$errors = $issues | Where-Object { $_.Severity -eq "ERROR" }
$warnings = $issues | Where-Object { $_.Severity -eq "WARNING" }

if ($warnings.Count -gt 0) {
    Write-Host "`nâš ï¸  Warnings:" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host "  â€¢ $($_.Message)" -ForegroundColor Yellow }
}

if ($errors.Count -gt 0) {
    Write-Host "`nâŒ Errors:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  â€¢ $($_.Message)" -ForegroundColor Red }
    exit 1
}

exit 0
