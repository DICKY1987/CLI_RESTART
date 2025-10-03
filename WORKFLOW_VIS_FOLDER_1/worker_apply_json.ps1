<#
.SYNOPSIS
  Worker that pulls JSON tasks from a folder, runs a CLI tool per file,
  creates a branch, commits/pushes, and repeats until no files remain.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$WorkingDir,             # repo root
  [Parameter(Mandatory=$true)][string]$QueueDir,               # folder containing *.json tasks
  [Parameter()][string]$InProgressDir = "$QueueDir\inprogress",
  [Parameter()][string]$DoneDir       = "$QueueDir\done",
  [Parameter()][string]$ErrorDir      = "$QueueDir\error",
  [Parameter()][string]$ToolName      = "codex",               # for logging only
  [Parameter()][string]$CommandTemplate = 'codex run --file "{file}"', # replace with real CLI
  [Parameter()][string]$BaseBranch    = "main",
  [Parameter()][string]$RemoteName    = "origin",
  [Parameter()][string]$BranchPrefix  = "auto",
  [Parameter()][int]$IdleExitSeconds  = 15,                    # exit if no work after this long
  [Parameter()][int]$PollMs           = 1000                   # poll delay when idle
)

$ErrorActionPreference = "Stop"

function Write-Info($msg){ Write-Host "[$(Get-Date -Format HH:mm:ss)] [$ToolName] $msg" }
function Safe-MakeDir([string]$p){ try { if(-not (Test-Path $p)){ New-Item -ItemType Directory -Path $p -Force | Out-Null } } catch { } }

Safe-MakeDir $InProgressDir
Safe-MakeDir $DoneDir
Safe-MakeDir $ErrorDir

# Ensure git ready
Set-Location $WorkingDir
Write-Info "Using repo: $WorkingDir"
git rev-parse --is-inside-work-tree | Out-Null

$lastWork = Get-Date

while ($true) {
  # Pull next JSON atomically by moving it into inprogress with a unique suffix.
  $next = Get-ChildItem -Path $QueueDir -Filter *.json -File -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $next) {
    if ((Get-Date) -gt $lastWork.AddSeconds($IdleExitSeconds)) {
      Write-Info "No more work found for $IdleExitSeconds s. Exiting."
      break
    }
    Start-Sleep -Milliseconds $PollMs
    continue
  }

  $stamp = Get-Date -Format "yyyyMMdd-HHmmss-ffff"
  $claimed = Join-Path $InProgressDir ($next.BaseName + "." + $stamp + $next.Extension)
  try {
    Move-Item -LiteralPath $next.FullName -Destination $claimed -ErrorAction Stop
  } catch {
    # If we fail to move, another worker probably took it; try again.
    continue
  }

  $lastWork = Get-Date
  Write-Info "Claimed: $(Split-Path $claimed -Leaf)"

  # Refresh base branch
  try {
    git fetch $RemoteName --prune
    git switch $BaseBranch
    git pull --ff-only $RemoteName $BaseBranch
  } catch {
    Write-Info "Git refresh failed: $($_.Exception.Message)"
    # Return file to queue
    try { Move-Item -LiteralPath $claimed -Destination (Join-Path $QueueDir (Split-Path $claimed -Leaf)) -Force } catch {}
    throw
  }

  # Branch per task
  $fileTag = [IO.Path]::GetFileNameWithoutExtension($claimed) -replace '[^a-zA-Z0-9\-]+','-'
  $branch  = "$BranchPrefix/$ToolName/$fileTag-$stamp"
  try {
    git switch -c $branch
  } catch {
    Write-Info "Branch create failed: $($_.Exception.Message)"
    try { Move-Item -LiteralPath $claimed -Destination (Join-Path $ErrorDir (Split-Path $claimed -Leaf)) -Force } catch {}
    continue
  }
  Write-Info "Created branch: $branch"

  # Run the tool on the file
  $cmd = $CommandTemplate.Replace("{file}", $claimed)
  Write-Info "Running: $cmd"
  $exitCode = 0
  try {
    # Use cmd.exe to allow complex commands/quoting
    cmd.exe /c $cmd
    $exitCode = $LASTEXITCODE
  } catch {
    $exitCode = 1
  }

  if ($exitCode -ne 0) {
    Write-Info "Tool failed (exit $exitCode). Moving to error."
    try { Move-Item -LiteralPath $claimed -Destination (Join-Path $ErrorDir (Split-Path $claimed -Leaf)) -Force } catch {}
    try {
      git switch $BaseBranch
      git branch -D $branch | Out-Null
    } catch { }
    continue
  }

  # Stage & commit any repo changes made by the tool
  $changes = git status --porcelain
  if (-not $changes) {
    Write-Info "No changes detected. Marking file as done without commit."
    try { Move-Item -LiteralPath $claimed -Destination (Join-Path $DoneDir (Split-Path $claimed -Leaf)) -Force } catch {}
    git switch $BaseBranch | Out-Null
    try { git branch -D $branch | Out-Null } catch {}
    continue
  }

  git add -A
  git commit -m "Apply modifications from task: $(Split-Path $claimed -Leaf) via $ToolName"
  try {
    git push -u $RemoteName $branch
    Write-Info "Pushed branch: $branch"
    Move-Item -LiteralPath $claimed -Destination (Join-Path $DoneDir (Split-Path $claimed -Leaf)) -Force
  } catch {
    Write-Info "Push failed: $($_.Exception.Message)"
    Move-Item -LiteralPath $claimed -Destination (Join-Path $ErrorDir (Split-Path $claimed -Leaf)) -Force
  } finally {
    # Return to base for next loop
    try { git switch $BaseBranch | Out-Null } catch {}
  }
}
