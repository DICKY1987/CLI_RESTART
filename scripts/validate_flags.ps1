param(
    [string]$RegistryPath = "config/policies/flags.yaml",
    [int]$WarnDays = 14
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $RegistryPath)) {
    Write-Error "Flags registry not found at $RegistryPath"; exit 1
}

try {
    $doc = Get-Content -LiteralPath $RegistryPath -Raw | ConvertFrom-Yaml
} catch {
    Write-Error "Failed to parse YAML: $($_.Exception.Message)"; exit 1
}

$errors = @()
$warnings = @()

if (-not $doc.flags -or $doc.flags.Count -eq 0) { $errors += "No flags defined under 'flags'" }

foreach ($f in $doc.flags) {
    if (-not $f.key) { $errors += "flag missing 'key'" }
    if (-not $f.description) { $errors += "flag '$($f.key)' missing 'description'" }
    if (-not $f.owners -or $f.owners.Count -eq 0) { $errors += "flag '$($f.key)' missing 'owners'" }
    if (-not $f.created) { $errors += "flag '$($f.key)' missing 'created'" }
    if (-not $f.expires) { $errors += "flag '$($f.key)' missing 'expires'" }

    # Date checks
    $createdDt = $null; $expiresDt = $null
    if ($f.created) { [void][DateTime]::TryParse($f.created, [ref]$createdDt) }
    if ($f.expires) { [void][DateTime]::TryParse($f.expires, [ref]$expiresDt) }
    if (-not $createdDt) { $errors += "flag '$($f.key)' has invalid 'created' date" }
    if (-not $expiresDt) { $errors += "flag '$($f.key)' has invalid 'expires' date" }
    if ($expiresDt) {
        $days = [int]([Math]::Floor(($expiresDt - (Get-Date)).TotalDays))
        if ($days -lt 0) { $errors += "flag '$($f.key)' expired $(-$days) days ago ($($f.expires))" }
        elseif ($days -le $WarnDays) { $warnings += "flag '$($f.key)' expires in $days days ($($f.expires))" }
    }
}

if ($warnings.Count -gt 0) {
    Write-Host "Warnings:" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
}

if ($errors.Count -gt 0) {
    Write-Host "Errors:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    exit 1
}

Write-Host "Flags registry validation passed" -ForegroundColor Green
