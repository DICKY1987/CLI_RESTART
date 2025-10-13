# APPLY DELETION PLAN FROM CSV
# Consumes a CSV produced from dedupe grouping and deletes only those rows,
# writing adjacent .DELETED_RECORD files before deletion. Mirrors the
# autonomous pipeline behavior but constrained to an explicit plan.

param(
  [Parameter(Mandatory=$true)]
  [ValidateScript({ Test-Path $_ -PathType Leaf })]
  [string]$PlanCsv,

  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function To-LongPath([string]$p) {
  if ($p.StartsWith('\\?\')) { return $p }
  if ($p.StartsWith('\\'))   { return "\\?\UNC\" + $p.TrimStart('\\') }
  if ($p -match '^[A-Za-z]:\\') { return "\\?\$p" }
  return $p
}

$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$rootForLogs = Split-Path -Path (Resolve-Path -LiteralPath $PlanCsv) -Parent
$logDir = Join-Path $rootForLogs ("PLAN_EXEC_" + $ts)
$null = New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$resultCsv = Join-Path $logDir ("plan_results_" + $ts + ".csv")
$summary   = Join-Path $logDir ("summary_" + $ts + ".txt")
"timestamp,deleted_file,kept_file,size_bytes,reason,hash,status,message" | Set-Content -LiteralPath $resultCsv -Encoding UTF8

Write-Host ""
Write-Host "=============================================================="
Write-Host "  APPLYING DEDUPLICATION PLAN (CSV)                           "
Write-Host "=============================================================="
Write-Host ("Plan:        {0}" -f (Resolve-Path -LiteralPath $PlanCsv))
Write-Host ("Dry run:     {0}" -f $DryRun.IsPresent)
Write-Host ("Log folder:  {0}" -f $logDir)
Write-Host ""

$deletedCount = 0
$spaceSaved   = [int64]0
$errorCount   = 0
$rowCount     = 0

$rows = Import-Csv -LiteralPath $PlanCsv

foreach ($r in $rows) {
  $rowCount++
  $deleted = $r.deleted_file
  $kept    = $r.kept_file
  $sizeStr = $r.size_bytes
  $reason  = $r.reason
  $hash    = $r.hash

  if (-not $deleted -or -not $kept) {
    $msg = 'Missing deleted_file or kept_file in row.'
    Add-Content -LiteralPath $resultCsv -Value ("{0},,,,{1},{2},error,{3}" -f ((Get-Date).ToString('o')), $reason, $hash, ($msg -replace '"','""')) -Encoding UTF8
    $errorCount++
    continue
  }

  try {
    $dInfo = Get-Item -LiteralPath $deleted -ErrorAction Stop
  } catch {
    $msg = "Deleted path not found: $deleted"
    Add-Content -LiteralPath $resultCsv -Value ("{0},{1},{2},,{3},{4},skip,{5}" -f ((Get-Date).ToString('o')), ($deleted -replace '"','""'), ($kept -replace '"','""'), $reason, $hash, ($msg -replace '"','""')) -Encoding UTF8
    continue
  }
  $size = if ($sizeStr) { [int64]$sizeStr } else { [int64]$dInfo.Length }

  $recordPath = "$($dInfo.FullName).DELETED_RECORD"
  $recordBody = @"
DELETED FILE RECORD
============================================================

Original File:     $($dInfo.FullName)
Deleted:           $(Get-Date).ToString("o")
Size:              $size bytes ($([math]::Round($size / 1MB, 2)) MB)
Kept Version:      $kept
Deletion Reason:   $reason
File Hash:         $hash

This file was deleted according to an explicit deletion plan.
The kept version is identical in content.
"@

  try {
    Set-Content -LiteralPath (To-LongPath $recordPath) -Value $recordBody -Encoding UTF8 -Force
    if (-not $DryRun) {
      Remove-Item -LiteralPath (To-LongPath $dInfo.FullName) -Force
    }
    $deletedCount++
    $spaceSaved += $size
    $line = '{0},{1},{2},{3},{4},{5},ok,' -f (
      (Get-Date).ToString('o'),
      ($dInfo.FullName -replace '"','""'),
      ($kept -replace '"','""'),
      $size,
      $reason,
      ($hash -replace '"','""')
    )
    Add-Content -LiteralPath $resultCsv -Value $line -Encoding UTF8
    Write-Host ("• Deleted: {0}`n    ↳ Kept: {1} ({2})" -f $dInfo.FullName, $kept, $reason)
  }
  catch {
    $errorCount++
    $msg = $_.Exception.Message
    $line = '{0},{1},{2},{3},{4},{5},error,{6}' -f (
      (Get-Date).ToString('o'),
      ($dInfo.FullName -replace '"','""'),
      ($kept -replace '"','""'),
      $size,
      $reason,
      ($hash -replace '"','""'),
      ($msg -replace '"','""')
    )
    Add-Content -LiteralPath $resultCsv -Value $line -Encoding UTF8
  }
}

$mb = [math]::Round($spaceSaved / 1MB, 2)
$summaryBody = @"
DELETION PLAN EXECUTION SUMMARY
======================================================================

Completed:        $((Get-Date).ToString('o'))
Plan CSV:         $PlanCsv
Rows in plan:     $rowCount
Files deleted:    $deletedCount
Space reclaimed:  $spaceSaved bytes ($mb MB)
Errors:           $errorCount

Artifacts:
  - Results CSV: $resultCsv
"@
Set-Content -LiteralPath $summary -Encoding UTF8 -Value $summaryBody

Write-Host ""
Write-Host "=============================================================="
Write-Host "PLAN EXECUTION COMPLETE"
Write-Host "=============================================================="
Write-Host ("Rows in plan:     {0}" -f $rowCount)
Write-Host ("Files deleted:    {0}" -f $deletedCount)
Write-Host ("Space reclaimed:  {0} bytes ({1} MB)" -f $spaceSaved, $mb)
Write-Host ("Errors:           {0}" -f $errorCount)
Write-Host ""
Write-Host "Artifacts:"
Write-Host "  • Results CSV: $resultCsv"
Write-Host "  • Summary: $summary"
Write-Host ""

exit ([int]([bool]($errorCount -gt 0)))

