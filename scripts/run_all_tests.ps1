[CmdletBinding()]
param(
    [switch]$SkipPython,
    [switch]$SkipPowerShell,
    [switch]$SkipNode
)

$ErrorActionPreference = 'Stop'
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDirectory '..')
$originalLocation = Get-Location
Push-Location $repoRoot

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

$reportsRoot = Join-Path $repoRoot '.reports'
Ensure-Directory -Path $reportsRoot
Ensure-Directory -Path (Join-Path $reportsRoot 'python/junit')
Ensure-Directory -Path (Join-Path $reportsRoot 'python/coverage')
Ensure-Directory -Path (Join-Path $reportsRoot 'powershell/junit')
Ensure-Directory -Path (Join-Path $reportsRoot 'powershell/coverage')
Ensure-Directory -Path (Join-Path $reportsRoot 'js/junit')
Ensure-Directory -Path (Join-Path $reportsRoot 'js/coverage')

$summary = @()
$overallSuccess = $true

function Add-SummaryLine {
    param([string]$Message)
    $script:summary += $Message
}

if (-not $SkipPython) {
    Write-Host '=== Python suite ===' -ForegroundColor Cyan
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
    }

    if (-not $pythonCmd) {
        Write-Warning 'Python executable not found. Skipping Python tests.'
        Add-SummaryLine '- Python: skipped (python executable not available)'
    }
    else {
        try {
            & $pythonCmd.Path -m pip install --upgrade pip | Write-Host
            if (Test-Path 'requirements-dev.txt') {
                & $pythonCmd.Path -m pip install -r 'requirements-dev.txt' | Write-Host
            }
            else {
                & $pythonCmd.Path -m pip install -e '.[test]' | Write-Host
            }

            $junitPath = Join-Path $reportsRoot 'python/junit/pytest-results.xml'
            $coverageXmlPath = Join-Path $reportsRoot 'python/coverage/coverage.xml'
            $coverageTxtPath = Join-Path $reportsRoot 'python/coverage/coverage.txt'

            & $pythonCmd.Path 'scripts/_python_security_tests.py' `
                --repo-root $repoRoot `
                --junit $junitPath `
                --coverage-xml $coverageXmlPath `
                --coverage-text $coverageTxtPath
            $pythonExit = $LASTEXITCODE
            if ($pythonExit -ne 0) {
                $overallSuccess = $false
                Add-SummaryLine '- Python: failed (see .reports/python for details)'
            }
            else {
                Add-SummaryLine '- Python: passed (coverage ≥ 85%)'
            }
        }
        catch {
            $overallSuccess = $false
            Add-SummaryLine "- Python: exception $($_.Exception.Message)"
        }
    }
}
else {
    Add-SummaryLine '- Python: skipped by flag'
}

if (-not $SkipPowerShell) {
    Write-Host '=== PowerShell suite ===' -ForegroundColor Cyan
    # Detect Pester tests; skip if none found
    $psTestFiles = Get-ChildItem -Path $repoRoot -Recurse -Include *.Tests.ps1, *.tests.ps1 -ErrorAction SilentlyContinue
    if (-not $psTestFiles) {
        Add-SummaryLine '- PowerShell: skipped (no tests found)'
    }
    else {
    try {
        $pesterModule = Get-Module -ListAvailable -Name Pester | Sort-Object Version -Descending | Select-Object -First 1
        if (-not $pesterModule -or $pesterModule.Version.Major -lt 5) {
            Write-Host 'Installing Pester module (v5)...'
            Install-Module Pester -Scope CurrentUser -Force -MinimumVersion 5.4.0 -ErrorAction Stop
        }
        Import-Module Pester -MinimumVersion 5.4.0 -ErrorAction Stop

        $configPath = Join-Path $repoRoot 'pester.config.psd1'
        $configData = Import-PowerShellDataFile -Path $configPath
        $configuration = New-PesterConfiguration -Hashtable $configData
        $configuration.TestResult.OutputPath = Join-Path $reportsRoot 'powershell/junit/pester-results.xml'
        $configuration.CodeCoverage.OutputPath = Join-Path $reportsRoot 'powershell/coverage/pester-coverage.xml'
        $configuration.CodeCoverage.OutputFormat = 'JaCoCo'

        $pesterResult = Invoke-Pester -Configuration $configuration
        $pesterExit = $LASTEXITCODE
        $coveragePercent = 0.0
        if ($null -ne $pesterResult.CodeCoverage -and $null -ne $pesterResult.CodeCoverage.CoveragePercent) {
            [void][double]::TryParse($pesterResult.CodeCoverage.CoveragePercent.ToString(), [ref]$coveragePercent)
        }
        if ($pesterExit -ne 0 -or $coveragePercent -lt 85) {
            if ($coveragePercent -lt 85) {
                Write-Error ('Pester coverage {0}% is below required threshold.' -f [math]::Round($coveragePercent, 2))
            }
            $overallSuccess = $false
            Add-SummaryLine '- PowerShell: failed (see .reports/powershell)'
        }
        else {
            Add-SummaryLine '- PowerShell: passed (coverage ≥ 85%)'
        }
    }
    catch {
        $overallSuccess = $false
        Add-SummaryLine "- PowerShell: exception $($_.Exception.Message)"
    }
    }
}
else {
    Add-SummaryLine '- PowerShell: skipped by flag'
}

if (-not $SkipNode) {
    Write-Host '=== Node suite ===' -ForegroundColor Cyan
    $packagePath = Join-Path $repoRoot 'package.json'
    if (-not (Test-Path $packagePath)) {
        Add-SummaryLine '- Node: skipped (package.json not found)'
    }
    else {
        $package = Get-Content $packagePath | ConvertFrom-Json
        $hasTestScript = $false
        if ($package.PSObject.Properties.Name -contains 'scripts') {
            $hasTestScript = $package.scripts.PSObject.Properties.Name -contains 'test'
        }

        if (-not $hasTestScript) {
            Add-SummaryLine '- Node: skipped (no test script defined)'
        }
        else {
            try {
                npm install --ignore-scripts | Write-Host
                $reportsDir = Join-Path $reportsRoot 'js'
                $env:JEST_JUNIT_OUTPUT = Join-Path $reportsDir 'junit/jest-results.xml'
                $env:CI = 'true'
                npm test -- --reporters=default --reporters=jest-junit --coverage --coverageDirectory "$(Join-Path $reportsDir 'coverage')"
                if ($LASTEXITCODE -ne 0) {
                    $overallSuccess = $false
                    Add-SummaryLine '- Node: failed (see .reports/js)'
                }
                else {
                    Add-SummaryLine '- Node: passed'
                }
            }
            catch {
                $overallSuccess = $false
                Add-SummaryLine "- Node: exception $($_.Exception.Message)"
            }
        }
    }
}
else {
    Add-SummaryLine '- Node: skipped by flag'
}

$summaryPath = Join-Path $reportsRoot 'summary.md'
"# Test Run Summary" | Out-File -FilePath $summaryPath -Encoding UTF8
$summary | ForEach-Object { $_ | Out-File -FilePath $summaryPath -Append -Encoding UTF8 }

Pop-Location

if (-not $overallSuccess) {
    Write-Error 'One or more test suites failed.'
    exit 1
}

Write-Host 'All requested test suites passed.' -ForegroundColor Green
exit 0
