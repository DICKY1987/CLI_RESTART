#!/usr/bin/env pwsh
# Legacy wrapper: this path is deprecated in favor of the
# canonical script under tools/atomic-workflow-system.
# Forwards all arguments to the canonical implementation.

$ErrorActionPreference = 'Stop'
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$target = Join-Path $repoRoot 'tools/atomic-workflow-system/GIT/deterministic_merge_system/scripts/PreFlight-Check.ps1'

Write-Host "[WS-C] Forwarding to canonical: $target" -ForegroundColor Yellow
& $target @args
exit $LASTEXITCODE

