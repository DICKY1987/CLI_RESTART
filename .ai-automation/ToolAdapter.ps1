<#
.SYNOPSIS
    Universal AI Tool Adapter - Extended version with Claude Code, Codex, and Gemini CLI support
.DESCRIPTION
    Runs AI-assisted development tools headlessly with universal prompt shape.
    Supports: aider, openinterpreter, opencode, claude, codex, gemini, llm (HTTP), git
.PARAMETER RequestPath
    Path to JSON request file, or reads from stdin if not provided
.EXAMPLE
    .\ToolAdapter.ps1 -RequestPath task.json
    Get-Content task.json | .\ToolAdapter.ps1
#>
[CmdletBinding()] param([string]$RequestPath)
$ErrorActionPreference = 'Stop'

function NowIso { [DateTime]::UtcNow.ToString('o') }
function Escape-Arg([string]$s){ if($s -notmatch '[\s"`\'']'){return $s}; '"'+($s -replace '"','\"')+'"' }

function Invoke-External {
  param([string]$Exe,[string[]]$Args=@(),[string]$Cwd=(Get-Location).Path,[hashtable]$EnvVars=@{},[int]$TimeoutSec=600)
  $psi = [Diagnostics.ProcessStartInfo]::new(); $psi.FileName=$Exe; $psi.Arguments=($Args|%{Escape-Arg $_}-join ' ')
  $psi.WorkingDirectory=$Cwd; $psi.RedirectStandardOutput=$true; $psi.RedirectStandardError=$true; $psi.UseShellExecute=$false; $psi.CreateNoWindow=$true
  foreach($k in [Environment]::GetEnvironmentVariables().Keys){ $psi.Environment[$k] = [Environment]::GetEnvironmentVariable($k) }
  foreach($k in $EnvVars.Keys){ $psi.Environment[$k] = [string]$EnvVars[$k] }
  $p=[Diagnostics.Process]::new(); $p.StartInfo=$psi; $null=$p.Start(); $start=Get-Date
  $out=$p.StandardOutput.ReadToEndAsync(); $err=$p.StandardError.ReadToEndAsync();
  if(-not $p.WaitForExit($TimeoutSec*1000)){ try{$p.Kill($true)}catch{}; return @{exit=124;out=$out.Result;err=("TIMEOUT {0}s"-f$TimeoutSec)+$err.Result;cmd="$Exe $($psi.Arguments)";start=$start;end=Get-Date} }
  return @{exit=$p.ExitCode;out=$out.Result;err=$err.Result;cmd="$Exe $($psi.Arguments)";start=$start;end=Get-Date}
}

function GitState([string]$path){
    try{
        $branch = (git -C $path rev-parse --abbrev-ref HEAD 2>$null).Trim()
        $head = (git -C $path rev-parse HEAD 2>$null).Trim()
        $status = (git -C $path status --porcelain 2>$null)
        $dirty = -not [string]::IsNullOrWhiteSpace($status)
        @{branch=$branch; head=$head; dirty=$dirty}
    }catch{
        @{branch='';head='';dirty=$false}
    }
}

function NewCommits($path,$before,$after){
    if(!$before -or !$after -or $before -eq $after){return @()}
    try{
        $commits = (git -C $path rev-list "$before..$after" --no-merges 2>$null).Trim()
        if($commits){ $commits.Split("`n")|?{$_} }else{ @() }
    }catch{ @() }
}

function Write-Log([string]$message,[string]$level='INFO'){
    $timestamp = NowIso
    Write-Host "[$timestamp] [$level] $message" -ForegroundColor $(if($level -eq 'ERROR'){'Red'}elseif($level -eq 'WARN'){'Yellow'}else{'Cyan'})
}

# Read request JSON
$reqJson = if($RequestPath){ Get-Content -Raw -Path $RequestPath } else { $input|Out-String }
if(-not $reqJson){ throw 'No JSON request provided.' }
$req = $reqJson | ConvertFrom-Json -Depth 8

# Parse request fields
$tool=($req.tool??'').ToLower()
$repo=($req.repo??(Get-Location).Path)
$prompt=($req.prompt??'')
$model=($req.model??$null)
$args=@($req.args)|?{$_}
$envH=@{}
if($req.env){ $req.env.psobject.Properties|%{ $envH[$_.Name]=[string]$_.Value } }
if(-not $envH.ContainsKey('OLLAMA_API_BASE')){ $envH['OLLAMA_API_BASE']='http://127.0.0.1:11434' }
$timeout=[int]($req.timeoutSec??600)

Write-Log "Starting execution: tool=$tool, repo=$repo"
$before = GitState $repo

switch($tool){
  'aider' {
    Write-Log "Running Aider..."
    $exe='aider'; $a=@()
    if($model){$a+='--model';$a+=$model}
    if($prompt){$a+='--message';$a+=$prompt}
    $a+='--yes'
    if($args.Count){$a+=$args}
    $r=Invoke-External -Exe $exe -Args $a -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
  }

  'openinterpreter' {
    Write-Log "Running Open Interpreter..."
    $exe='python'; $tmp=[IO.Path]::Combine([IO.Path]::GetTempPath(),"oi_"+[Guid]::NewGuid().ToString('N')+".py")
    ($"from interpreter import interpreter`ninterpreter.chat(\"\"\"{($prompt -replace '"""','\"\"\"')}\"\"\")`n") | Set-Content -Encoding UTF8 -Path $tmp
    $r=Invoke-External -Exe $exe -Args @($tmp)+$args -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
    Remove-Item -Force $tmp -ErrorAction SilentlyContinue
  }

  'opencode' {
    Write-Log "Running OpenCode..."
    $exe='opencode'; $a=@('run')
    if($prompt){$a+=$prompt}
    if($args.Count){$a+=$args}
    $r=Invoke-External -Exe $exe -Args $a -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
  }

  'claude' {
    Write-Log "Running Claude Code CLI..."
    $exe='claude'
    $a=@()
    # Claude Code CLI typically uses: claude <prompt> or claude --model <model> <prompt>
    if($model){$a+='--model';$a+=$model}
    if($prompt){$a+=$prompt}
    if($args.Count){$a+=$args}
    $r=Invoke-External -Exe $exe -Args $a -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
  }

  'codex' {
    Write-Log "Running Codex CLI..."
    $exe='codex'
    $a=@()
    # Codex CLI usage may vary - adjust based on actual CLI interface
    if($prompt){$a+=$prompt}
    if($model){$a+='--model';$a+=$model}
    if($args.Count){$a+=$args}
    $r=Invoke-External -Exe $exe -Args $a -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
  }

  'gemini' {
    Write-Log "Running Gemini CLI..."
    $exe='gemini'
    $a=@()
    # Gemini CLI usage - adjust based on actual CLI interface
    if($prompt){$a+=$prompt}
    if($model){$a+='--model';$a+=$model}
    if($args.Count){$a+=$args}
    $r=Invoke-External -Exe $exe -Args $a -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
  }

  'llm' {
    Write-Log "Running generic LLM via HTTP..."
    # Generic HTTP post (e.g., Ollama). Args[0]=endpoint, Args[1]=model (optional)
    $endpoint = if($args.Count -ge 1){ $args[0] } else { $envH['OLLAMA_API_BASE']+'/api/chat' }
    $mdl = if($args.Count -ge 2){ $args[1] } elseif($model){ $model } else { 'deepseek-coder' }
    $body = @{ model=$mdl; messages=@(@{role='user';content=$prompt}) } | ConvertTo-Json -Depth 6
    try {
        $resp = Invoke-RestMethod -Method Post -Uri $endpoint -Body $body -ContentType 'application/json' -TimeoutSec $timeout
        $r = @{ exit=0; out=($resp|ConvertTo-Json -Depth 6); err=''; cmd="POST $endpoint"; start=Get-Date; end=Get-Date }
    } catch {
        $r = @{ exit=1; out=''; err=$_.Exception.Message; cmd="POST $endpoint"; start=Get-Date; end=Get-Date }
    }
  }

  'git' {
    Write-Log "Running Git enforcement workflow..."
    # Lightweight enforcement path: stage Scope, run Checks, commit
    $scope = @($req.scope) | ?{ $_ }
    $checks= @($req.checks) | ?{ $_ }
    $subject= ($req.commit ?? 'chore: automated change')

    try {
        foreach($p in $scope){
            Write-Log "Staging: $p"
            git -C $repo add $p
        }

        $changed = git -C $repo diff --name-only --cached | ?{ $_ }
        Write-Log "Changed files: $($changed -join ', ')"

        foreach($f in $changed){
            $inScope = $false
            foreach($s in $scope){
                if($f -like ("$s/*") -or $f -eq $s){ $inScope = $true; break }
            }
            if(-not $inScope){ throw "Staged change outside Scope: $f" }
        }

        foreach($c in $checks){
            Write-Log "Running check: $c"
            & powershell -NoProfile -Command $c
            if($LASTEXITCODE -ne 0){ throw "Check failed: $c" }
        }

        Write-Log "Committing: $subject"
        git -C $repo commit -m $subject
        $r=@{ exit=0; out='git enforcement OK'; err=''; cmd='git add+commit'; start=Get-Date; end=Get-Date }
    } catch {
        $r=@{ exit=1; out=''; err=$_.Exception.Message; cmd='git enforcement'; start=Get-Date; end=Get-Date }
    }
  }

  default {
    throw "Unsupported tool '$tool'. Use: aider | openinterpreter | opencode | claude | codex | gemini | llm | git"
  }
}

# Capture post-execution state
$after = GitState $repo
$new = NewCommits $repo $before.head $after.head

# Log to JSONL if runs directory exists
$runsDir = Join-Path $repo '.ai-automation/runs'
if(Test-Path $runsDir){
    $logFile = Join-Path $runsDir "executions.jsonl"
    $logEntry = @{
        timestamp = (NowIso)
        tool = $tool
        exit_code = $r.exit
        duration_ms = [math]::Round(($r.end - $r.start).TotalMilliseconds)
        repo = $repo
        new_commits = @($new)
    } | ConvertTo-Json -Depth 2 -Compress
    Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
    Write-Log "Logged to: $logFile"
}

# Build result
$result = @{
    ok = ($r.exit -eq 0)
    tool = $tool
    started = $r.start.ToUniversalTime().ToString('o')
    finished = $r.end.ToUniversalTime().ToString('o')
    duration_ms = [math]::Round(($r.end - $r.start).TotalMilliseconds)
    exit_code = $r.exit
    stdout = $r.out
    stderr = $r.err
    repo_state = @{
        branch = $after.branch
        head_before = $before.head
        head_after = $after.head
        dirty_after = [bool]$after.dirty
        new_commits = @($new)
    }
    meta = @{
        command = $r.cmd
        cwd = $repo
    }
}

Write-Log "Execution completed: exit_code=$($r.exit), duration=$($result.duration_ms)ms" -level $(if($r.exit -eq 0){'INFO'}else{'ERROR'})

# Output result JSON
$result | ConvertTo-Json -Depth 8 -Compress
