# Script to create PR from ws-f-mods-applied to main
# Usage: .\create_pr.ps1

$ErrorActionPreference = "Stop"

$REPO = "DICKY1987/CLI_RESTART"
$BASE = "main"
$HEAD = "ws-f-mods-applied"
$TITLE = "WS-F: Build System Consolidation & Follow-up Modifications"

Write-Host "Creating Pull Request..." -ForegroundColor Green
Write-Host "Repository: $REPO"
Write-Host "Base: $BASE"
Write-Host "Head: $HEAD"
Write-Host "Title: $TITLE"
Write-Host ""

# Check if gh CLI is installed
$ghExists = Get-Command gh -ErrorAction SilentlyContinue

if ($ghExists) {
    Write-Host "Using GitHub CLI (gh)..." -ForegroundColor Cyan
    
    # Check if authenticated
    try {
        gh auth status 2>&1 | Out-Null
        Write-Host "✓ GitHub CLI is authenticated" -ForegroundColor Green
        
        # Create PR
        gh pr create `
            --repo $REPO `
            --base $BASE `
            --head $HEAD `
            --title $TITLE `
            --body-file PR_BODY.md
        
        Write-Host "✓ Pull request created successfully!" -ForegroundColor Green
        exit 0
    }
    catch {
        Write-Host "✗ GitHub CLI is not authenticated" -ForegroundColor Red
        Write-Host "Please run: gh auth login" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "✗ GitHub CLI (gh) is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative options:" -ForegroundColor Yellow
    Write-Host "1. Install gh CLI: https://cli.github.com/"
    Write-Host "2. Use the GitHub web UI: https://github.com/$REPO/compare/$BASE...$HEAD?expand=1"
    Write-Host "3. Use Invoke-RestMethod with GITHUB_TOKEN (see CREATE_PR_INSTRUCTIONS.md)"
    exit 1
}
