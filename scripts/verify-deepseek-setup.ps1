# Verify DeepSeek + AI Tools Setup
# This script checks that Aider, Continue, OpenCode, and Ollama are properly configured

Write-Host "`n=== DeepSeek AI Tools Setup Verification ===" -ForegroundColor Cyan
Write-Host ""

# Check Ollama
Write-Host "[1/5] Checking Ollama service..." -ForegroundColor Yellow
try {
    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
    $deepseekModel = $ollamaResponse.models | Where-Object { $_.name -like "*deepseek*" }

    if ($deepseekModel) {
        Write-Host "  ✅ Ollama is running" -ForegroundColor Green
        Write-Host "  ✅ DeepSeek model found: $($deepseekModel.name)" -ForegroundColor Green
        Write-Host "     Size: $([math]::Round($deepseekModel.size / 1GB, 2)) GB" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  Ollama is running but DeepSeek model not found" -ForegroundColor Yellow
        Write-Host "     Run: ollama pull deepseek-coder-v2:lite" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ❌ Ollama is not running or not accessible" -ForegroundColor Red
    Write-Host "     Make sure Ollama is started" -ForegroundColor Gray
}

# Check Aider config
Write-Host "`n[2/5] Checking Aider configuration..." -ForegroundColor Yellow
$aiderConfig = "$env:USERPROFILE\.aider.conf.yml"
if (Test-Path $aiderConfig) {
    $aiderContent = Get-Content $aiderConfig -Raw
    if ($aiderContent -match "deepseek") {
        Write-Host "  ✅ Aider config found and configured for DeepSeek" -ForegroundColor Green
        Write-Host "     Config: $aiderConfig" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  Aider config found but not using DeepSeek" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ Aider config not found" -ForegroundColor Red
    Write-Host "     Expected: $aiderConfig" -ForegroundColor Gray
}

# Check Continue config
Write-Host "`n[3/5] Checking Continue configuration..." -ForegroundColor Yellow
$continueConfig = "$env:USERPROFILE\.continue\config.json"
if (Test-Path $continueConfig) {
    $continueContent = Get-Content $continueConfig -Raw | ConvertFrom-Json
    $hasDeepSeek = $continueContent.models | Where-Object { $_.model -like "*deepseek*" }

    if ($hasDeepSeek) {
        Write-Host "  ✅ Continue config found and configured for DeepSeek" -ForegroundColor Green
        Write-Host "     Config: $continueConfig" -ForegroundColor Gray
        Write-Host "     Model: $($hasDeepSeek.model)" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  Continue config found but not using DeepSeek" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ Continue config not found" -ForegroundColor Red
    Write-Host "     Expected: $continueConfig" -ForegroundColor Gray
}

# Check OpenCode installation
Write-Host "`n[4/5] Checking OpenCode installation..." -ForegroundColor Yellow
try {
    $opencodeVersion = & opencode --version 2>&1
    Write-Host "  ✅ OpenCode installed: v$opencodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ OpenCode not found in PATH" -ForegroundColor Red
}

# Check OpenCode wrapper scripts
Write-Host "`n[5/5] Checking OpenCode wrapper scripts..." -ForegroundColor Yellow
$wrapperScripts = @(
    "$env:USERPROFILE\opencode-deepseek.cmd",
    "$env:USERPROFILE\opencode-deepseek.ps1",
    "$env:USERPROFILE\opencode-deepseek-run.cmd",
    "$env:USERPROFILE\opencode-deepseek-run.ps1"
)

$foundWrappers = 0
foreach ($script in $wrapperScripts) {
    if (Test-Path $script) {
        $foundWrappers++
    }
}

if ($foundWrappers -eq 4) {
    Write-Host "  ✅ All wrapper scripts found ($foundWrappers/4)" -ForegroundColor Green
    Write-Host "     Location: $env:USERPROFILE" -ForegroundColor Gray
} elseif ($foundWrappers -gt 0) {
    Write-Host "  ⚠️  Some wrapper scripts found ($foundWrappers/4)" -ForegroundColor Yellow
} else {
    Write-Host "  ❌ No wrapper scripts found" -ForegroundColor Red
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration files:" -ForegroundColor White
Write-Host "  - Aider:    $aiderConfig"
Write-Host "  - Continue: $continueConfig"
Write-Host "  - OpenCode: $env:USERPROFILE\opencode-deepseek.*"
Write-Host ""
Write-Host "Usage:" -ForegroundColor White
Write-Host "  - Aider:    aider"
Write-Host "  - Continue: Use VS Code extension (Ctrl+L)"
Write-Host "  - OpenCode: opencode-deepseek or .\opencode-deepseek.cmd"
Write-Host ""
Write-Host "Documentation:" -ForegroundColor White
Write-Host "  - Setup guide: $env:USERPROFILE\OPENCODE-DEEPSEEK-SETUP.md"
Write-Host "  - Quick ref:   $env:USERPROFILE\CLI_RESTART\AI-TOOLS-DEEPSEEK-REFERENCE.md"
Write-Host ""
