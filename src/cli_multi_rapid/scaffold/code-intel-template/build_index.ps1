Param(
  [string]$RepoRoot = (Resolve-Path "$PSScriptRoot\..\").Path,
  [switch]$NoEmbed
)
$ErrorActionPreference = 'Stop'
try {
  & python "$PSScriptRoot\build_index.py" @('--no-embed')[$NoEmbed.IsPresent -eq $False]
} catch {
  Write-Host "Error running Python indexer: $_" -ForegroundColor Red
}

