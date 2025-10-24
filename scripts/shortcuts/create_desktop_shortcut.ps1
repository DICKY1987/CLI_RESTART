#!/usr/bin/env pwsh
# Legacy wrapper: this helper moved to scripts/create_desktop_shortcut.ps1
# Forward all arguments to the canonical implementation.

$ErrorActionPreference = 'Stop'
$target = Join-Path (Split-Path $PSScriptRoot -Parent) 'create_desktop_shortcut.ps1'
Write-Host "[WS-C] Forwarding to canonical: $target" -ForegroundColor Yellow
& $target @args
exit $LASTEXITCODE
