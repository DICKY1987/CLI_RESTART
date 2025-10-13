# AUTONOMOUS DEDUPLICATION PIPELINE (Windows PowerShell 7)
# See: SPEC-1-Autonomous Deduplication Pipeline

param(
  [Parameter(Mandatory=$true)]
  [ValidateNotNullOrEmpty()]
  [string]$RootPath,

  [string[]]$Include = @(),
  [string[]]$Exclude = @(),
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info($msg)  { Write-Host $msg }
function Write-Warn($msg)  { Write-Host "WARN: $msg" }
function Write-Err($msg)   { Write-Host "ERR : $msg" }

# Resolve and normalize root
$RootPath = (Resolve-Path -LiteralPath $RootPath).Path

# Timestamp + per-run dirs
$ts        = Get-Date -Format 'yyyyMMdd_HHmmss'
$logRoot   = Join-Path $RootPath '.dedup_logs'
$runDir    = Join-Path $logRoot $ts
$toolsDir  = Join-Path $RootPath '.tools\fclones'
$null = New-Item -ItemType Directory -Force -Path $runDir, $toolsDir | Out-Null

$dupJson   = Join-Path $runDir "duplicates_${ts}.json"
$csvLog    = Join-Path $runDir "deleted_files_${ts}.csv"
$summary   = Join-Path $runDir "summary_${ts}.txt"
$fileList  = Join-Path $runDir "files_${ts}.txt"

# ---------- Helpers ----------
function Invoke-FclonesWithCmdPipe([string]$exe, [string]$inputFile, [string]$stdoutFile, [string]$stderrFile) {
  $cmd = "type `"$inputFile`" | `"$exe`" group --stdin --depth 0 --format json 1> `"$stdoutFile`" 2> `"$stderrFile`""
  $p = Start-Process -FilePath cmd.exe -ArgumentList @('/c', $cmd) -NoNewWindow -PassThru -Wait
  return $p.ExitCode
}
function To-LongPath([string]$p) {
  if ($p.StartsWith('\\?\')) { return $p }
  if ($p.StartsWith('\\'))   { return "\\?\UNC\" + $p.TrimStart('\\') }
  if ($p -match '^[A-Za-z]:\\') { return "\\?\$p" }
  return $p
}

function MatchesAny([string]$path, [string[]]$patterns) {
  if (-not $patterns -or $patterns.Count -eq 0) { return $true }
  foreach ($pat in $patterns) { if ($path -like $pat) { return $true } }
  return $false
}
function ExcludedByAny([string]$path, [string[]]$patterns) {
  foreach ($pat in $patterns) { if ($path -like $pat) { return $true } }
  return $false
}

function Get-FclonesPath {
  $cmd = Get-Command fclones -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Path }

  $cached = Join-Path $toolsDir 'fclones.exe'
  if (Test-Path $cached) { return $cached }

  Write-Info "[setup] fclones not found; downloading latest Windows x64 build..."
  $api = "https://api.github.com/repos/pkolaczk/fclones/releases/latest"
  $headers = @{ 'User-Agent' = 'autonomous-dedupe' }
  if ($env:GITHUB_TOKEN) { $headers['Authorization'] = "Bearer $($env:GITHUB_TOKEN)" }

  try {
    $rel = Invoke-RestMethod -Uri $api -Headers $headers
    $asset = $rel.assets | Where-Object { $_.name -match 'windows-x86_64\.zip$' } | Select-Object -First 1
    if (-not $asset) { throw "No Windows x64 asset found on latest release." }

    $zipPath = Join-Path $toolsDir $asset.name
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath -UseBasicParsing
    Expand-Archive -LiteralPath $zipPath -DestinationPath $toolsDir -Force

    $exe = Get-ChildItem -LiteralPath $toolsDir -Filter 'fclones.exe' -Recurse | Select-Object -First 1
    if (-not $exe) { throw "fclones.exe not found after extraction." }

    if ($exe.FullName -ne $cached) {
      Copy-Item -LiteralPath $exe.FullName -Destination $cached -Force
    }
    Remove-Item -LiteralPath $zipPath -Force
    return $cached
  }
  catch {
    throw "Failed to auto-install fclones: $($_.Exception.Message)"
  }
}

# ---------- Banner ----------
Write-Host ""
Write-Host "=============================================================="
Write-Host "  AUTONOMOUS DUPLICATE REMOVAL PIPELINE (Windows)             "
Write-Host "=============================================================="
Write-Host ""
Write-Host ("Root:        {0}" -f $RootPath)
Write-Host ("Started:     {0}" -f (Get-Date))
Write-Host ("Run folder:  {0}" -f $runDir)
Write-Host ""
Write-Host "Rules:"
Write-Host "  1) Keep LARGER file"
Write-Host "  2) If equal size – keep NEWER LastWriteTimeUtc"
Write-Host "  3) If tie – alphabetical path"
Write-Host ""

# ---------- Locate or fetch fclones ----------
$fclones = Get-FclonesPath

# ---------- Enumerate files (skip reparse points + default excludes) ----------
$defaultExcludeNames = @(
  '$Recycle.Bin', 'System Volume Information', '.git', '.hg', '.svn', '.dedup_logs'
)
$excludeRegex = ('(^|\\)(' + ($defaultExcludeNames -join '|').Replace('.','\.') + ')(\\|$)')

Write-Info "[1/4] Enumerating files..."
$files = Get-ChildItem -LiteralPath $RootPath -File -Recurse -Force -Attributes !ReparsePoint -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch $excludeRegex } |
  Select-Object -ExpandProperty FullName

$files = $files | Where-Object { MatchesAny $_ $Include } | Where-Object { -not (ExcludedByAny $_ $Exclude) }
$files = $files | Sort-Object { $_ } -Culture 'en-US'

if (-not $files -or $files.Count -eq 0) {
  Write-Host "• No files to scan under root (after filters). Exiting."
  exit 0
}

$files | Set-Content -LiteralPath $fileList -Encoding UTF8

# ---------- Run fclones (JSON output) ----------
Write-Info "[2/4] Grouping duplicates with fclones..."
$fclog = Join-Path $runDir "fclones_${ts}.log"
$exit = Invoke-FclonesWithCmdPipe -exe $fclones -inputFile $fileList -stdoutFile $dupJson -stderrFile $fclog
if ($exit -ne 0) {
  Write-Warn "fclones exited with code $exit. See log: $fclog"
}

if (-not (Test-Path $dupJson) -or (Get-Item $dupJson).Length -eq 0) {
  Write-Host "• No duplicates found (empty JSON). Exiting."
  exit 0
}

# ---------- Parse JSON & apply keep policy ----------
Write-Info "[3/4] Applying deterministic keep policy and deleting..."
"timestamp,deleted_file,kept_file,size_bytes,reason,hash" | Set-Content -LiteralPath $csvLog -Encoding UTF8

$deletedCount = 0
$spaceSaved   = [int64]0
$errorCount   = 0

try {
  $json = Get-Content -LiteralPath $dupJson -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
  Write-Err "Failed to parse fclones JSON: $($_.Exception.Message)"
  exit 1
}

$groups = @()
if ($json.groups) { $groups = $json.groups }
elseif ($json -is [array]) { $groups = $json }

$groupTotal = $groups.Count
Write-Host "Processing $groupTotal duplicate groups..."

for ($i = 0; $i -lt $groupTotal; $i++) {
  $g = $groups[$i]
  $filesInGroup = @()

  if ($g.files) {
    foreach ($path in $g.files) {
      if (-not $path) { continue }
      try {
        $fi = Get-Item -LiteralPath $path -ErrorAction Stop
        $filesInGroup += [pscustomobject]@{
          Path   = $fi.FullName
          Size   = if ($g.file_len) { [int64]$g.file_len } else { [int64]$fi.Length }
          MTime  = $fi.LastWriteTimeUtc
        }
      } catch {
        $errorCount++
        Write-Warn "Skipping missing/inaccessible file: $path"
      }
    }
  }

  if ($filesInGroup.Count -lt 2) { continue }

  $sorted = $filesInGroup | Sort-Object `
    @{ Expression = { $_.Size };  Descending = $true },
    @{ Expression = { $_.MTime }; Descending = $true },
    @{ Expression = { $_.Path };  Descending = $false }

  $keeper = $sorted[0]
  $dups   = $sorted[1..($sorted.Count-1)]
  $hash   = if ($g.file_hash) { $g.file_hash } else { $g.hash }

  foreach ($d in $dups) {
    $reason = if ($d.Size -lt $keeper.Size) {
      'smaller_file'
    } elseif ($d.MTime -lt $keeper.MTime) {
      'older_modified_date'
    } else {
      'alphabetical_tiebreaker'
    }

    $recordPath = "$($d.Path).DELETED_RECORD"
    $recordBody = @"
DELETED FILE RECORD
============================================================

Original File:     $($d.Path)
Deleted:           $(Get-Date).ToString("o")
Size:              $($d.Size) bytes ($([math]::Round($d.Size / 1MB, 2)) MB)
Kept Version:      $($keeper.Path)
Deletion Reason:   $reason
File Hash:         $hash

This file was automatically deleted by the deduplication pipeline.
The kept version is identical in content.
"@

    try {
      Set-Content -LiteralPath (To-LongPath $recordPath) -Value $recordBody -Encoding UTF8 -Force

      if (-not $DryRun) {
        Remove-Item -LiteralPath (To-LongPath $d.Path) -Force
      }

      $line = '{0},{1},{2},{3},{4},{5}' -f (
        (Get-Date).ToString('o'),
        ($d.Path -replace '"','""'),
        ($keeper.Path -replace '"','""'),
        $d.Size,
        $reason,
        ($hash -replace '"','""')
      )
      Add-Content -LiteralPath $csvLog -Value $line -Encoding UTF8

      $deletedCount++
      $spaceSaved += $d.Size

      Write-Host ("• [{0}/{1}] Deleted: {2}`n    ↳ Kept: {3} ({4})" -f ($i+1), $groupTotal, $d.Path, $keeper.Path, $reason)
    }
    catch {
      $errorCount++
      Write-Err "Deletion failed for '$($d.Path)': $($_.Exception.Message)"
      if (-not $DryRun) {
        try { Remove-Item -LiteralPath (To-LongPath $recordPath) -Force -ErrorAction SilentlyContinue } catch {}
      }
    }
  }
}

# ---------- Summary ----------
$mb = [math]::Round($spaceSaved / 1MB, 2)
$summaryBody = @"
AUTONOMOUS DEDUPLICATION SUMMARY
======================================================================

Completed:        $((Get-Date).ToString('o'))
Root:             $RootPath
Files deleted:    $deletedCount
Space reclaimed:  $spaceSaved bytes ($mb MB)
Errors:           $errorCount
Dry run:          $($DryRun.IsPresent)

Artifacts:
  - Duplicates JSON: $dupJson
  - Deleted files CSV: $csvLog
  - File list: $fileList
"@
Set-Content -LiteralPath $summary -Encoding UTF8 -Value $summaryBody

Write-Host ""
Write-Host "=============================================================="
Write-Host "DELETION COMPLETE"
Write-Host "=============================================================="
Write-Host ("Files deleted:    {0}" -f $deletedCount)
Write-Host ("Space reclaimed:  {0} bytes ({1} MB)" -f $spaceSaved, $mb)
Write-Host ("Errors:           {0}" -f $errorCount)
Write-Host ""
Write-Host "Artifacts:"
Write-Host "  • JSON: $dupJson"
Write-Host "  • CSV : $csvLog"
Write-Host "  • Summary: $summary"
Write-Host ""

exit ([int]([bool]($errorCount -gt 0)))
