Import-Module Pester -ErrorAction Stop

# Resolve repo root as plain string to avoid provider-qualified paths
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' | Join-Path -ChildPath '..')).Path
$modulePath = Join-Path $repoRoot 'scripts/TradingOps/TradingOps.psm1'

Describe 'TradingOps module' {
    BeforeAll {
        $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' | Join-Path -ChildPath '..')).Path
        $modulePath = Join-Path $repoRoot 'scripts/TradingOps/TradingOps.psm1'
        if (-not (Test-Path $modulePath)) { throw "TradingOps module not found: $modulePath" }
        Import-Module $modulePath -Force | Out-Null
    }

    It 'exports Get-Health with expected output' {
        Get-Command Get-Health | Should -Not -BeNullOrEmpty
        Get-Health | Should -Be 'Get-Health OK'
    }

    It 'exports Invoke-Action with expected output' {
        Get-Command Invoke-Action | Should -Not -BeNullOrEmpty
        Invoke-Action | Should -Be 'Invoke-Action OK'
    }

    Context 'Idempotent import' {
        It 'does not duplicate exported functions when re-imported' {
            Import-Module $modulePath -Force | Out-Null
            (Get-Command Get-Health).ModuleName | Should -Be 'TradingOps'
            (Get-Command Invoke-Action).ModuleName | Should -Be 'TradingOps'
        }
    }
}
