Import-Module Pester -ErrorAction Stop

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..' )
$modulePath = Join-Path $repoRoot 'scripts/TradingOps/TradingOps.psm1'

Describe 'TradingOps module' {
    BeforeAll {
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
