Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-ChildAndGetExit([string]$cfgPath, [string]$sessionId) {
  $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' | Join-Path -ChildPath '..')).Path
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = 'powershell'
  $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $repoRoot 'restart.ps1')`" -ConfigPath `"$cfgPath`" -SessionId $sessionId -NoOpenEditor"
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $p = [System.Diagnostics.Process]::Start($psi)
  $p.WaitForExit()
  return $p.ExitCode
}

Describe 'Config Validation' {
  BeforeAll {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' | Join-Path -ChildPath '..')).Path
    $scriptPath = Join-Path $repoRoot 'restart.ps1'

    It 'restart.ps1 exists' {
      (Test-Path $scriptPath) | Should -Be $true
    }

    $tmpDir = Join-Path $repoRoot '.tmp-tests'
    if (-not (Test-Path $tmpDir)) { New-Item -ItemType Directory -Path $tmpDir | Out-Null }
  }

  AfterAll {
    if (Test-Path (Join-Path $repoRoot '.tmp-tests')) {
      Remove-Item -Recurse -Force (Join-Path $repoRoot '.tmp-tests')
    }
  }

  It 'Missing repository.url -> non-zero exit and error.txt exists' {
    $cfg = @{ repository = @{}; toggles = @{ launchPanes = $true } } | ConvertTo-Json
    $cfgPath = Join-Path $repoRoot '.tmp-tests/missing-repo-url.json'
    Set-Content -LiteralPath $cfgPath -Value $cfg -Encoding UTF8

    $sessionId = [Guid]::NewGuid().ToString('N')
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'powershell'
    $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $repoRoot 'restart.ps1')`" -ConfigPath `"$cfgPath`" -SessionId $sessionId -NoOpenEditor"
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $p = [System.Diagnostics.Process]::Start($psi)
    $p.WaitForExit()
    $exit = $p.ExitCode

    $exit | Should -Not -Be 0
    $errorFile = Join-Path $repoRoot ".sessions/$sessionId/error.txt"
    Start-Sleep -Milliseconds 200
    Write-Host "Expecting error file at: $errorFile"
    (Test-Path $errorFile) | Should -Be $true
    (Get-Content -LiteralPath $errorFile -Raw) | Should -Match 'repository\\.url is required'
  }

  It 'Invalid types in toggles -> error surfaced' {
    $cfg = @{ repository = @{ url = 'https://example.com/repo.git' }; toggles = @{ launchPanes = 'yes'; dryRun = 1 } } | ConvertTo-Json
    $cfgPath = Join-Path $repoRoot '.tmp-tests/invalid-toggles.json'
    Set-Content -LiteralPath $cfgPath -Value $cfg -Encoding UTF8

    $sessionId = [Guid]::NewGuid().ToString('N')
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'powershell'
    $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $repoRoot 'restart.ps1')`" -ConfigPath `"$cfgPath`" -SessionId $sessionId -NoOpenEditor"
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $p = [System.Diagnostics.Process]::Start($psi)
    $p.WaitForExit()
    $exit = $p.ExitCode

    $exit | Should -Not -Be 0
    $errorFile = Join-Path $repoRoot ".sessions/$sessionId/error.txt"
    Start-Sleep -Milliseconds 200
    Write-Host "Expecting error file at: $errorFile"
    (Test-Path $errorFile) | Should -Be $true
    $content = Get-Content -LiteralPath $errorFile -Raw
    $content | Should -Match 'toggles\\.launchPanes must be boolean'
    $content | Should -Match 'toggles\\.dryRun must be boolean'
  }
}
