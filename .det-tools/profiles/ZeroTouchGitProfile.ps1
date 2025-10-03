# Zero-touch Git safety on PowerShell exit
$env:AI_TOOL_NAME = "generic"
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
  try {
    if (Test-Path .git) {
      $ts = Get-Date -Format "yyyyMMdd_HHmmss"
      git add -A | Out-Null
      git commit -m "WIP: Auto-save on exit [$ts]" --no-verify | Out-Null
      $branch = git branch --show-current
      if (-not [string]::IsNullOrEmpty($branch)) {
        git push origin "HEAD:refs/heads/wip/$branch" --force-with-lease | Out-Null
      }
    }
  } catch { }
}
function gacp-safe([string]$message = "WIP: $(Get-Date -Format 'HH:mm')") {
  git add -A
  git commit -m $message --no-verify
  git push origin HEAD --force-with-lease
}
function Start-ToolSafe([Parameter(Mandatory)][string]$tool_exec, [Parameter(ValueFromRemainingArguments=$true)][string[]]$args) {
  $env:AI_TOOL_NAME = [System.IO.Path]::GetFileNameWithoutExtension($tool_exec)
  & git add -A | Out-Null
  & git commit -m "checkpoint: before $($env:AI_TOOL_NAME)" --no-verify | Out-Null
  & $tool_exec @args
  & git add -A | Out-Null
  & git commit -m "checkpoint: after $($env:AI_TOOL_NAME)" --no-verify | Out-Null
  & git push origin HEAD --force-with-lease | Out-Null
}
Set-Alias tool-safe Start-ToolSafe
