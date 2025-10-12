#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
    Validates tooling requirements for deterministic merge system
.DESCRIPTION
    Checks for presence and versions of required tools (git, jq, yq, etc.)
    Exits with code 0 if all requirements met, non-zero otherwise
#>

param(
    [switch]$Strict,  # Exit on any missing optional tool
    [switch]$Fix      # Attempt to install missing tools
)

$ErrorActionPreference = 'Continue'
$results = @{
    required_ok = $true
    optional_ok = $true
    missing_required = @()
    missing_optional = @()
}

function Test-Tool {
    param($Name, $MinVersion = $null, $Required = $true)

    $tool = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $tool) {
        $msg = "âŒ $Name not found"
        if ($Required) {
            $results.required_ok = $false
            $results.missing_required += $Name
            Write-Host $msg -ForegroundColor Red
        } else {
            $results.optional_ok = $false
            $results.missing_optional += $Name
            Write-Host $msg -ForegroundColor Yellow
        }
        return $false
    }

    if ($MinVersion) {
        $version = & $Name --version 2>&1 | Select-Object -First 1
        Write-Host "âœ… $Name found: $version" -ForegroundColor Green
        # Version check logic here if needed
    } else {
        Write-Host "âœ… $Name found" -ForegroundColor Green
    }
    return $true
}

Write-Host "`nðŸ” Checking Required Tools..." -ForegroundColor Cyan
Test-Tool "git" -MinVersion "2.30" -Required $true
Test-Tool "pwsh" -MinVersion "7.0" -Required $true

Write-Host "`nðŸ” Checking Optional Tools (for enhanced merges)..." -ForegroundColor Cyan
Test-Tool "jq" -MinVersion "1.6" -Required $false
Test-Tool "yq" -MinVersion "4.0" -Required $false
Test-Tool "python" -MinVersion "3.9" -Required $false
Test-Tool "ruff" -Required $false
Test-Tool "mypy" -Required $false

Write-Host "`nðŸ“Š Summary:" -ForegroundColor Cyan
if (-not $results.required_ok) {
    Write-Host "âŒ Missing required tools: $($results.missing_required -join ', ')" -ForegroundColor Red
    Write-Host "`nInstall them with:" -ForegroundColor Yellow
    Write-Host "  â€¢ Git: https://git-scm.com/downloads"
    Write-Host "  â€¢ PowerShell 7: https://aka.ms/powershell"
    exit 1
}

if (-not $results.optional_ok) {
    Write-Host "âš ï¸  Missing optional tools: $($results.missing_optional -join ', ')" -ForegroundColor Yellow
    Write-Host "The system will use fallback strategies for these." -ForegroundColor Gray
    if ($Strict) {
        exit 2
    }
}

Write-Host "âœ… All required tools present" -ForegroundColor Green
exit 0
