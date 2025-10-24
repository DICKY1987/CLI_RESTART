#!/usr/bin/env pwsh
# Legacy wrapper: use Launch-Workflow-VSCode.ps1
# Forwards all arguments to the canonical implementation.

$ErrorActionPreference = 'Stop'
$target = Join-Path $PSScriptRoot 'Launch-Workflow-VSCode.ps1'
Write-Host "[WS-C] Forwarding to canonical: $target" -ForegroundColor Yellow
& $target @args
exit $LASTEXITCODE

