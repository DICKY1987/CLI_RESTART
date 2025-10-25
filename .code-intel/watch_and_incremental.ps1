Param(
  [double]$Interval = 2.0
)
$ErrorActionPreference = 'Stop'
& python "$PSScriptRoot\watch_and_incremental.py" --interval $Interval

