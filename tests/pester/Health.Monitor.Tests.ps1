<#
 .SYNOPSIS
   Tests for health monitor functionality.

 .DESCRIPTION
   Validates that health-monitor.ps1:
   - Writes health.json at regular intervals
   - Tracks system health metrics
   - Honors interval and max checks settings
#>

Describe 'Health.Monitor' -Tag 'Health' {
  BeforeAll {
    $healthMonitorScript = Join-Path $PSScriptRoot '../../.launcher/health-monitor.ps1'
    $testOutputDir = Join-Path $env:TEMP "HealthMonitorTests"

    if (-not (Test-Path $testOutputDir)) {
      New-Item -ItemType Directory -Path $testOutputDir | Out-Null
    }
  }

  AfterAll {
    if (Test-Path $testOutputDir) {
      Remove-Item -Path $testOutputDir -Recurse -Force
    }
  }

  BeforeEach {
    # Clean test output directory
    Get-ChildItem -Path $testOutputDir -File | Remove-Item -Force
  }

  It 'Exists and is a valid PowerShell script' {
    $healthMonitorScript | Should -Exist
    { Get-Command -Name $healthMonitorScript -ErrorAction Stop } | Should -Not -Throw
  }

  It 'Creates health.json file when run with MaxChecks=1' {
    $healthOutput = Join-Path $testOutputDir 'health.json'

    # Run health monitor for single check
    & $healthMonitorScript -OutputPath $healthOutput -IntervalSeconds 1 -MaxChecks 1

    # Verify output file was created
    Test-Path $healthOutput | Should -Be $true
  }

  It 'Health.json contains valid JSON with required fields' {
    $healthOutput = Join-Path $testOutputDir 'health-valid.json'

    # Run health monitor
    & $healthMonitorScript -OutputPath $healthOutput -IntervalSeconds 1 -MaxChecks 1

    # Read and parse JSON
    $content = Get-Content -LiteralPath $healthOutput -Raw
    $health = $null
    { $health = $content | ConvertFrom-Json } | Should -Not -Throw

    # Verify required fields
    $health.timestamp | Should -Not -BeNullOrEmpty
    $health.PSObject.Properties['healthy'] | Should -Not -BeNullOrEmpty
    $health.checks | Should -Not -BeNullOrEmpty
  }

  It 'Updates health.json multiple times with short interval' {
    $healthOutput = Join-Path $testOutputDir 'health-multi.json'

    # Run health monitor for 2 checks with 1 second interval
    & $healthMonitorScript -OutputPath $healthOutput -IntervalSeconds 1 -MaxChecks 2

    # Verify file exists
    Test-Path $healthOutput | Should -Be $true

    # Parse and verify it's valid
    $content = Get-Content -LiteralPath $healthOutput -Raw
    $health = $content | ConvertFrom-Json

    $health.timestamp | Should -Not -BeNullOrEmpty
  }

  It 'Includes disk space check in health status' {
    $healthOutput = Join-Path $testOutputDir 'health-disk.json'

    & $healthMonitorScript -OutputPath $healthOutput -IntervalSeconds 1 -MaxChecks 1

    $content = Get-Content -LiteralPath $healthOutput -Raw
    $health = $content | ConvertFrom-Json

    $health.checks.disk | Should -Not -BeNullOrEmpty
    $health.checks.disk.status | Should -BeIn @('ok', 'warning', 'error')
  }

  It 'Includes memory check in health status' {
    $healthOutput = Join-Path $testOutputDir 'health-memory.json'

    & $healthMonitorScript -OutputPath $healthOutput -IntervalSeconds 1 -MaxChecks 1

    $content = Get-Content -LiteralPath $healthOutput -Raw
    $health = $content | ConvertFrom-Json

    $health.checks.memory | Should -Not -BeNullOrEmpty
    # Status could be ok, warning, error, or skipped (on non-Windows)
    $health.checks.memory.status | Should -BeIn @('ok', 'warning', 'error', 'skipped')
  }

  It 'Includes process count check in health status' {
    $healthOutput = Join-Path $testOutputDir 'health-processes.json'

    & $healthMonitorScript -OutputPath $healthOutput -IntervalSeconds 1 -MaxChecks 1

    $content = Get-Content -LiteralPath $healthOutput -Raw
    $health = $content | ConvertFrom-Json

    $health.checks.processes | Should -Not -BeNullOrEmpty
    $health.checks.processes.status | Should -BeIn @('ok', 'error')
  }
}
