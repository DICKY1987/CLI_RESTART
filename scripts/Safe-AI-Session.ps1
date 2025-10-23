#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
    Scoped AI tool session wrapper with automatic hook execution
.DESCRIPTION
    Creates timestamped workstream branches for AI tool sessions with automatic
    pre-commit hook execution and optional push on exit
.PARAMETER Tool
    AI tool to launch (aider, claude, opencode, continue, ollama)
.PARAMETER Scope
    Path scope to limit changes (default: entire repo)
.PARAMETER PushOnExit
    Automatically push to remote on exit
.PARAMETER NoCheckpoint
    Skip initial checkpoint commit
.EXAMPLE
    .\Safe-AI-Session.ps1 -Tool aider -Scope src -PushOnExit
.EXAMPLE
    .\Safe-AI-Session.ps1 -Tool claude -NoCheckpoint
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("aider", "claude", "opencode", "continue", "ollama", "cursor")]
    [string]$Tool,

    [string]$Scope = ".",

    [switch]$PushOnExit,

    [switch]$NoCheckpoint
)

$ErrorActionPreference = 'Stop'
# Note: -Verbose is a built-in common parameter, no need to declare it

Write-Host "`n🤖 Safe AI Session - Scoped Branch Wrapper" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

# Step 1: Generate unique session ID
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ulid = $timestamp
$branchName = "workstream/$Tool/$ulid"

Write-Host "`n📍 Session Details:" -ForegroundColor Cyan
Write-Host "   Tool: $Tool" -ForegroundColor Gray
Write-Host "   Scope: $Scope" -ForegroundColor Gray
Write-Host "   Branch: $branchName" -ForegroundColor Gray
Write-Host "   Push on exit: $(if ($PushOnExit) { 'Yes' } else { 'No' })" -ForegroundColor Gray

# Step 2: Ensure clean working directory
Write-Host "`n🔍 Checking working directory..." -ForegroundColor Cyan
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️ You have uncommitted changes:" -ForegroundColor Yellow
    Write-Host $status -ForegroundColor Gray

    $response = Read-Host "`nContinue anyway? Changes will be included in session (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "❌ Aborting - please commit or stash changes first" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Create workstream branch
Write-Host "`n🌿 Creating workstream branch..." -ForegroundColor Cyan
try {
    git switch -c $branchName
    Write-Host "✅ Created and switched to: $branchName" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to create branch: $_"
    exit 1
}

# Step 4: Optional checkpoint commit
if (-not $NoCheckpoint) {
    Write-Host "`n📌 Creating checkpoint commit..." -ForegroundColor Cyan
    try {
        $checkpointMsg = @"
feat(session): Start $Tool session [$ulid]

Scope: $Scope
Tool: $Tool
Timestamp: $timestamp
Type: AI-assisted development session

This is an automated checkpoint commit marking the start of a scoped
AI tool session. All subsequent changes will be made within this branch.
"@

        # Stage scope if specified
        if ($Scope -ne ".") {
            if (Test-Path $Scope) {
                git add $Scope
            } else {
                Write-Warning "⚠️ Scope path '$Scope' not found - using entire repo"
                $Scope = "."
            }
        }

        git commit --allow-empty -m $checkpointMsg
        Write-Host "✅ Checkpoint commit created" -ForegroundColor Green
    } catch {
        Write-Warning "⚠️ Checkpoint commit failed (non-critical): $_"
    }
}

# Step 5: Display tool launch instructions
Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "🚀 Ready to launch $Tool" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Gray
Write-Host ""
Write-Host "Session is ready! You can now:" -ForegroundColor Cyan
Write-Host "  1. Launch your AI tool manually" -ForegroundColor Gray
Write-Host "  2. Make changes within scope: $Scope" -ForegroundColor Gray
Write-Host "  3. Commit changes as you work" -ForegroundColor Gray
Write-Host ""

# Tool-specific launch hints
switch ($Tool) {
    "aider" {
        $cmd = if ($Scope -ne ".") { "aider $Scope" } else { "aider" }
        Write-Host "💡 To launch Aider:" -ForegroundColor Yellow
        Write-Host "   $cmd" -ForegroundColor White
    }
    "claude" {
        Write-Host "💡 To launch Claude Code:" -ForegroundColor Yellow
        Write-Host "   claude" -ForegroundColor White
    }
    "opencode" {
        $cmd = if ($Scope -ne ".") { "opencode $Scope" } else { "opencode" }
        Write-Host "💡 To launch OpenCode:" -ForegroundColor Yellow
        Write-Host "   $cmd" -ForegroundColor White
    }
    "continue" {
        Write-Host "💡 To launch Continue (VS Code):" -ForegroundColor Yellow
        Write-Host "   code ." -ForegroundColor White
        Write-Host "   Then use Cmd+Shift+P > Continue: Start" -ForegroundColor Gray
    }
    "ollama" {
        Write-Host "💡 To use Ollama with Aider:" -ForegroundColor Yellow
        Write-Host "   aider --model ollama/deepseek-coder-v2:lite" -ForegroundColor White
    }
    "cursor" {
        Write-Host "💡 To launch Cursor:" -ForegroundColor Yellow
        Write-Host "   cursor ." -ForegroundColor White
    }
}

Write-Host ""
Write-Host "When done, press Enter to run hooks and finalize..." -ForegroundColor Cyan

# Step 6: Wait for user to complete session
try {
    Read-Host "Press Enter when session is complete"
} catch {
    # Handle Ctrl+C gracefully
    Write-Host "`n⚠️ Session interrupted" -ForegroundColor Yellow
}

# Step 7: Run pre-commit hooks
Write-Host "`n🔍 Running pre-commit hooks..." -ForegroundColor Cyan
$hooksOk = $true

try {
    if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
        pre-commit run --all-files --show-diff-on-failure

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "⚠️ Pre-commit hooks found issues"
            $hooksOk = $false

            $response = Read-Host "`nContinue with push anyway? (y/N)"
            if ($response -ne 'y' -and $response -ne 'Y') {
                Write-Host "`n⚠️ Session complete but not pushed (fix hooks first)" -ForegroundColor Yellow
                Write-Host "   Branch: $branchName" -ForegroundColor Gray
                Write-Host "   Push manually when ready: git push -u origin $branchName" -ForegroundColor Gray
                exit 0
            }
        } else {
            Write-Host "✅ All hooks passed" -ForegroundColor Green
        }
    } else {
        Write-Warning "⚠️ pre-commit not installed - skipping hook validation"
        Write-Host "   Install with: pip install pre-commit && pre-commit install" -ForegroundColor Gray
    }
} catch {
    Write-Warning "⚠️ Hook execution error: $_"
    $hooksOk = $false
}

# Step 8: Optional push to remote
if ($PushOnExit) {
    Write-Host "`n🚀 Pushing to remote..." -ForegroundColor Cyan
    try {
        git push -u origin $branchName

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Pushed to origin: $branchName" -ForegroundColor Green

            # Display PR creation hint
            Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
            Write-Host "   • Merge train will automatically process this branch" -ForegroundColor Gray
            Write-Host "   • Or create a PR manually:" -ForegroundColor Gray
            Write-Host "     gh pr create --base main --head $branchName --fill" -ForegroundColor White
        } else {
            Write-Warning "⚠️ Push failed (exit code: $LASTEXITCODE)"
            Write-Host "   Push manually when ready: git push -u origin $branchName" -ForegroundColor Gray
        }
    } catch {
        Write-Warning "⚠️ Push error: $_"
        Write-Host "   Push manually when ready: git push -u origin $branchName" -ForegroundColor Gray
    }
} else {
    Write-Host "`n📦 Session complete (not pushed)" -ForegroundColor Yellow
    Write-Host "   Branch: $branchName" -ForegroundColor Gray
    Write-Host "   Push when ready:" -ForegroundColor Gray
    Write-Host "     git push -u origin $branchName" -ForegroundColor White
}

# Step 9: Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "✅ Safe AI Session Complete" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Gray
Write-Host "Tool: $Tool" -ForegroundColor Gray
Write-Host "Branch: $branchName" -ForegroundColor Gray
Write-Host "Hooks: $(if ($hooksOk) { '✅ Passed' } else { '⚠️ Issues found' })" -ForegroundColor Gray
Write-Host "Pushed: $(if ($PushOnExit) { '✅ Yes' } else { '❌ No' })" -ForegroundColor Gray
Write-Host ""

exit 0
