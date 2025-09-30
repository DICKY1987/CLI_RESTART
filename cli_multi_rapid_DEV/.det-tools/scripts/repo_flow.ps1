param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("begin","save","consolidate","cleanup")]
  [string]$cmd,
  [string]$message
)

$ErrorActionPreference = "Stop"

function Import-GitConfig {
  $cfg = Join-Path (git rev-parse --show-toplevel) ".gitconfig.local"
  if (Test-Path $cfg) {
    git config --local include.path ".gitconfig.local" | Out-Null
  }
}

function Ensure-Branch {
  param([string]$ToolName = "tool")
  $date = Get-Date -Format "yyyy-MM-dd"
  $topic = $(git rev-parse --short HEAD)
  $branch = "ws/$date-$ToolName-$topic"
  if (git rev-parse --verify $branch 2>$null) {
    git checkout $branch | Out-Null
  } else {
    git checkout -b $branch | Out-Null
  }
  return $branch
}

function Begin {
  $tool = $env:REPO_FLOW_TOOL
  if ([string]::IsNullOrWhiteSpace($tool)) { $tool = "generic" }
  Import-GitConfig
  $b = Ensure-Branch -ToolName $tool
  Write-Host "On $b"
}

function Save {
  param([string]$Msg)
  if ([string]::IsNullOrWhiteSpace($Msg)) { $Msg = "update" }
  Import-GitConfig
  $cur = git rev-parse --abbrev-ref HEAD
  if ($cur -eq "main") { throw "Refusing to commit on main. Run: repo_flow.ps1 begin" }
  git add -A
  git commit -m $Msg --allow-empty
  git push -u origin $cur
  try {
    gh pr view --json number 1>$null 2>$null
    gh pr edit --title "$cur" --body "Automated PR by repo_flow" | Out-Null
  } catch {
    gh pr create --fill --title "$cur" --body "Automated PR by repo_flow" --base main --head $cur | Out-Null
  }
  try { gh pr edit --add-label "auto-merge" | Out-Null } catch {}
  Write-Host "Pushed and PR ready for $cur"
}

function Consolidate {
  git fetch --prune
  git remote prune origin | Out-Null
  Write-Host "Consolidation queued (server-side action will process)."
  try {
    gh api repos/{owner}/{repo}/dispatches -f event_type="consolidate-branches" | Out-Null
  } catch {}
}

function Cleanup {
  git fetch --prune
  $merged = git branch --merged origin/main | ForEach-Object { $_.Trim() } | Where-Object {$_ -notmatch "^\*|main$"}
  foreach ($b in $merged) {
    git branch -d $b | Out-Null
  }
  Write-Host "Local merged branches cleaned."
}

switch ($cmd) {
  "begin"       { Begin }
  "save"        { Save -Msg $message }
  "consolidate" { Consolidate }
  "cleanup"     { Cleanup }
}

