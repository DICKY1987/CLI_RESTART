@{
    Run = @{
        Path = @('tests/pester')
        Exit = $true
    }
    Output = @{
        Verbosity = 'Detailed'
    }
    TestResult = @{
        Enabled = $true
        OutputFormat = 'NUnitXml'
    }
    CodeCoverage = @{
        Enabled = $true
        Path = @('scripts/TradingOps/TradingOps.psm1')
        CoveragePercentTarget = 85
    }
}
