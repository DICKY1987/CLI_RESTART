Describe "Launcher Integration (-NoLaunch)" {
    BeforeAll {
        $scriptPath = Join-Path $PSScriptRoot "../../restart.ps1" | Resolve-Path
        $workspace = Join-Path $TestDrive 'int'
        New-Item -ItemType Directory -Force -Path $workspace | Out-Null
        $cfg = Join-Path $workspace 'cfg.json'
        '{"repository": {"url": "https://example.com/repo.git"}}' | Out-File -FilePath $cfg -Encoding UTF8
        $global:__sid = 'deadbeef'
        & $scriptPath -ConfigPath $cfg -NoLaunch -SessionId $__sid -NoOpenEditor | Out-Null
    }

    It "Integration: creates .sessions/{id}/manifest.json and preflight.md" {
        $repoRoot = Split-Path (Resolve-Path (Join-Path $PSScriptRoot '../../restart.ps1')) -Parent
        $sessionDir = Join-Path $repoRoot (Join-Path '.sessions' $__sid)
        (Test-Path (Join-Path $sessionDir 'manifest.json')) | Should -Be $true
        (Test-Path (Join-Path $sessionDir 'preflight.md')) | Should -Be $true
    }
}
