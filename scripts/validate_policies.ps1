param()
$ErrorActionPreference = 'Stop'

function Has-Field {
    param([object]$obj, [string]$name)
    if ($null -eq $obj) { return $false }
    if ($obj -is [hashtable]) { return $obj.ContainsKey($name) }
    return ($obj.PSObject.Properties.Name -contains $name)
}

function Assert-Field {
    param([object]$obj, [string]$name, [string]$context)
    if (-not (Has-Field -obj $obj -name $name)) {
        throw "$context missing required field '$name'"
    }
}

function Test-SloPolicy {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { throw "SLO policy not found: $Path" }
    $yaml = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Yaml
    Assert-Field $yaml 'services' 'slo-policy'
    if ($yaml.services.Count -eq 0) { throw "slo-policy 'services' must not be empty" }
    foreach ($svc in $yaml.services) {
        Assert-Field $svc 'name' 'service'
        Assert-Field $svc 'tier' 'service'
        Assert-Field $svc 'objectives' 'service'
        $obj = $svc.objectives
        if (-not $obj) { throw "service '$($svc.name)' missing 'objectives'" }
        $keys = if ($obj -is [hashtable]) { $obj.Keys } else { $obj.PSObject.Properties.Name }
        if (-not ($keys | Where-Object { $_ -in @('availability','latency','job_success_rate') })) {
            throw "service '$($svc.name)' objectives must include availability/latency/job_success_rate"
        }
    }
}

function Test-SecretsPolicy {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { throw "Secrets policy not found: $Path" }
    $yaml = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Yaml
    Assert-Field $yaml 'rotation' 'secrets-policy'
    Assert-Field $yaml 'requirements' 'secrets-policy'
    Assert-Field $yaml 'audit' 'secrets-policy'
    $rot = $yaml.rotation
    foreach ($field in 'default_interval_days','grace_period_days') {
        if (-not (Has-Field -obj $rot -name $field)) { throw "secrets-policy.rotation missing '$field'" }
    }
    $auditPath = $yaml.audit.'append_only_ledger'
    if (-not $auditPath) { throw "secrets-policy.audit.append_only_ledger missing" }
    if (-not (Test-Path -LiteralPath $auditPath)) {
        Write-Warning "Ledger file not found at '$auditPath' (will be created on first entry)"
    }
}

function Resolve-PolicyPath {
    param([string]$NewPath, [string]$LegacyPath)
    if (Test-Path -LiteralPath $NewPath) { return $NewPath }
    return $LegacyPath
}

$sloPath = Resolve-PolicyPath -NewPath 'config/policies/slo-policy.yaml' -LegacyPath 'policies/slo-policy.yaml'
$secretsPath = Resolve-PolicyPath -NewPath 'config/policies/secrets-policy.yaml' -LegacyPath 'policies/secrets-policy.yaml'

Test-SloPolicy -Path $sloPath
Test-SecretsPolicy -Path $secretsPath
Write-Host 'Policy validation passed' -ForegroundColor Green
