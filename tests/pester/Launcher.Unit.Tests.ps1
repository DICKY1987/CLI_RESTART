Describe "Launcher Unit (restart.ps1)" {
    BeforeAll {
        $scriptPath = Join-Path $PSScriptRoot "../../restart.ps1" | Resolve-Path
    }

    It "Unit: New-SessionId (8-char hex)" {
        $ws = Join-Path $TestDrive 'ws1'
        New-Item -ItemType Directory -Path $ws | Out-Null
        $cfg = Join-Path $ws 'cfg.json'
        '{"repository": {"url": "https://example.com/repo.git"}}' | Out-File -FilePath $cfg -Encoding UTF8
        & $scriptPath -ConfigPath $cfg -NoLaunch -NoOpenEditor | Out-Null
        $sessionsDir = Join-Path $PSScriptRoot '../../.sessions' | Resolve-Path -ErrorAction SilentlyContinue
        $sessionsDir = if ($sessionsDir) { $sessionsDir.Path } else { Join-Path (Split-Path $scriptPath -Parent) '.sessions' }
        $dirs = Get-ChildItem -Path $sessionsDir -Directory
        ($dirs.Count -gt 0) | Should Be $true
        $latest = $dirs | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $sid = $latest.Name
        $sid.Length | Should Be 8
        ($sid -match '^[0-9a-f]{8}$') | Should Be $true
    }

    It "Unit: Read-Config failure paths" {
        $ws = Join-Path $TestDrive 'ws2'
        New-Item -ItemType Directory -Path $ws | Out-Null
        $missing = Join-Path $ws 'missing.json'
        $sid = 'badc0de1'
        # Invoke; script will write error.txt and exit 1
        & $scriptPath -ConfigPath $missing -SessionId $sid -NoOpenEditor *>$null
        $errFile = Join-Path (Join-Path (Split-Path $scriptPath -Parent) ".sessions/$sid") 'error.txt'
        (Test-Path $errFile) | Should Be $true
        ((Get-Content -Raw -LiteralPath $errFile) -match 'Config file not found') | Should Be $true
    }

    It "Unit: Preflight check formatting" {
        $ws = Join-Path $TestDrive 'ws3'
        New-Item -ItemType Directory -Path $ws | Out-Null
        $cfg = Join-Path $ws 'cfg.json'
        '{"repository": {"url": "https://example.com/repo.git"}}' | Out-File -FilePath $cfg -Encoding UTF8
        $sid = 'cafebabe'
        & $scriptPath -ConfigPath $cfg -NoLaunch -SessionId $sid -NoOpenEditor | Out-Null
        $sessionDir = Join-Path (Split-Path $scriptPath -Parent) ".sessions/$sid"
        $preflight = Get-Content -Raw -LiteralPath (Join-Path $sessionDir 'preflight.md')
        ($preflight -match "# Preflight Check") | Should Be $true
        ($preflight -match "Workspace:") | Should Be $true
        ($preflight -match "Timestamp:") | Should Be $true
    }
}
