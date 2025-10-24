Param(
  [Parameter(Mandatory=$true)][string]$Query
)
$ErrorActionPreference = 'Stop'
& python "$PSScriptRoot\retrieve.py" --query "$Query"

