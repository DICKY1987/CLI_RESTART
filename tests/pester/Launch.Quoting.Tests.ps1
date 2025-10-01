<#
 .SYNOPSIS
   Tests for hardened quoting in tool launching.

 .DESCRIPTION
   Validates that Run-Tool.ps1 properly handles:
   - Paths with spaces
   - Non-ASCII characters
   - Special characters
#>

Describe 'Launch.Quoting' -Tag 'Quoting' {
  BeforeAll {
    $runToolScript = Join-Path $PSScriptRoot '../../.launcher/Run-Tool.ps1'

    # Create test executable in temp location with spaces
    $testDir = Join-Path $env:TEMP "Test Launch Dir"
    if (-not (Test-Path $testDir)) {
      New-Item -ItemType Directory -Path $testDir | Out-Null
    }

    # Create a simple test script
    $testScript = Join-Path $testDir 'test-tool.ps1'
    @'
param([string]$Message = "Hello")
Write-Output "Received: $Message"
exit 0
'@ | Out-File -FilePath $testScript -Encoding UTF8
  }

  AfterAll {
    # Cleanup test directory
    $testDir = Join-Path $env:TEMP "Test Launch Dir"
    if (Test-Path $testDir) {
      Remove-Item -Path $testDir -Recurse -Force
    }
  }

  It 'Handles paths with spaces without quoting errors' {
    $testDir = Join-Path $env:TEMP "Test Launch Dir"
    $testScript = Join-Path $testDir 'test-tool.ps1'

    { & $runToolScript -ToolPath $testScript -Arguments @('World') } | Should -Not -Throw
  }

  It 'Escapes arguments containing quotes' {
    $runToolScript = Join-Path $PSScriptRoot '../../.launcher/Run-Tool.ps1'

    # Test the Escape-Argument function indirectly through the script
    # by checking it doesn't crash with quoted input
    $testDir = Join-Path $env:TEMP "Test Launch Dir"
    $testScript = Join-Path $testDir 'test-tool.ps1'

    { & $runToolScript -ToolPath $testScript -Arguments @('Say "Hello"') } | Should -Not -Throw
  }

  It 'Validates tool path exists before launching' {
    $runToolScript = Join-Path $PSScriptRoot '../../.launcher/Run-Tool.ps1'
    $fakePath = 'C:\NonExistent\Tool.exe'

    { & $runToolScript -ToolPath $fakePath -ErrorAction Stop } | Should -Throw
  }

  It 'Handles working directory with spaces' {
    $runToolScript = Join-Path $PSScriptRoot '../../.launcher/Run-Tool.ps1'
    $testDir = Join-Path $env:TEMP "Test Launch Dir"
    $testScript = Join-Path $testDir 'test-tool.ps1'

    { & $runToolScript -ToolPath $testScript -WorkingDirectory $testDir } | Should -Not -Throw
  }
}
