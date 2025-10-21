# Universal Prompt Shape & Headless CLI Guide  
**Scope:** This document summarizes our conversation and consolidates working patterns, prompt structure, and code examples for running AI‑assisted development **headlessly** with your DeepSeek‑via‑Ollama setup.  
**Explicit exclusions:** *Continue* and *OpenHands* are intentionally **not covered**.

---

## 1) TL;DR
- Use a **universal prompt shape** so the same task spec drives different tools deterministically.
- Prefer **Git as the contract**: each tool runs headless → edits → commits → next step reads repo state.
- Keep **Scope** narrow (allow‑list), make **Checks** executable, and assert **Artifacts**. That’s your guardrail trio.
- For providers (Claude, Codex, Gemini), the same universal prompt can be sent via CLI/API wrappers; locally you can route to **DeepSeek** with **Ollama**.

---

## 2) Universal Prompt Shape
A single, repeatable structure that captures everything an agent needs while remaining model/tool agnostic.

```
Task:        <one‑sentence objective written as an action>
Scope:       <allow‑list of files/dirs the tool may modify>
Constraints: <style, APIs, dependency rules, quality bars>
Checks:      <shell commands run to prove success>
Artifacts:   <files/paths that must be created or updated>
Commit:      <short imperative subject for the commit>
Context:     <read‑only references: docs, configs, standards>
Limits:      <iteration/time/token guards>
Success:     <pass/fail acceptance criteria>
```

### Why this works
- **Determinism**: same fields, same order → lower ambiguity.
- **Portability**: translates cleanly to different tools.
- **Auditability**: simple to diff in Git, easy to log as JSONL.
- **Guardrails**: **Scope + Checks + Success** map directly to enforcement in CI and local scripts.

### JSON form (for automation)
```json
{
  "task": "Refactor utils/logger.py into src/logging/* with structured JSON logs",
  "scope": ["src/logging/**", "tests/logging/**"],
  "constraints": ["No new dependencies", "Keep public API stable", "PEP8; mypy clean"],
  "checks": ["ruff check .", "pytest -q", "mypy ."],
  "artifacts": ["docs/logging/README.md", "tests/logging/test_handlers.py"],
  "commit": "refactor(logging): extract handlers and add tests",
  "context": ["docs/Engineering-Standards.md", ".pre-commit-config.yaml"],
  "limits": { "max_iterations": 5, "soft_time": "10m" },
  "success": ["All checks pass", "No edits outside Scope", "≥90% coverage on new code"]
}
```

---

## 3) Headless Execution Patterns
1. **Git as the contract (recommended):**
   - Tool runs headless → makes small, reviewable commits → downstream steps inspect/verify.
2. **Files/STDIO JSON:**
   - Write `task.request.json`, capture `task.result.json` + exit code; great for CI and orchestrators.
3. **HTTP where available:**
   - For LLM providers (or Ollama), POST the rendered prompt block and parse JSON responses.

---

## 4) Tool‑by‑Tool Mapping (excluding Continue & OpenHands)

### 4.1 Aider (terminal‑first pair programmer)
**How it ingests the shape:** put the whole block into `--message`, pass targeted file paths **after** the command to reinforce Scope. Use `--yes` for non‑interactive.

**Example**
```bash
aider --model ollama_chat/deepseek-coder:latest \
  --message "Task: Extract logger into src/logging/*\nScope: src/logging/**; tests/logging/**\nConstraints: no new deps; keep API stable\nChecks: ruff check . && pytest -q && mypy .\nArtifacts: docs/logging/README.md\nCommit: refactor(logging): extract handlers and add tests\nSuccess: checks pass; edits stay within Scope" \
  --yes src/utils/logger.py src/logging tests/logging
```

---

### 4.2 Open Interpreter (programmatic local execution)
**How it ingests the shape:** embed the block in a `interpreter.chat("""...""")` message; be explicit about writing files and printing JSON.

**Python snippet**
```python
from interpreter import interpreter
interpreter.chat("""
Task: list functions in src/logging
Scope: src/logging/**
Checks: print JSON summary only
Artifacts: artifacts/functions.csv
Success: CSV exists with 2 columns
""")
```

---

### 4.3 OpenCode (TUI + one‑shot run)
**How it ingests the shape:** pass the block to `opencode run` for non‑interactive one‑offs, or run as a server and POST.

**Example**
```bash
opencode run "Task: summarize src/logging\nScope: src/logging/**\nArtifacts: docs/logging-summary.md\nSuccess: file created with key sections"
```

---

### 4.4 Git CLI (enforcement, not generation)
**How it uses the shape:**
- **Scope →** pathspec allow‑list for staging/committing.
- **Checks →** commands that must pass (exit code 0) before committing.
- **Artifacts →** assert files exist/changed.
- **Commit →** the commit subject.
- **Success →** verify checks + confirm changed files are inside Scope.

**PowerShell enforcement sketch**
```powershell
param(
  [string[]]$Scope = @('src/logging','tests/logging'),
  [string[]]$Checks = @('ruff check .','pytest -q','mypy .'),
  [string]$Commit = 'refactor(logging): extract handlers and add tests'
)

# Stage only within scope
foreach ($p in $Scope) { git add $p }

# Verify no out‑of‑scope changes staged
$changed = git diff --name-only --cached | Where-Object { $_ }
$allowed = $true
foreach ($f in $changed) {
  if (-not ($Scope | ForEach-Object { $f -like ("$_/*") -or $f -eq $_ })) { $allowed = $false }
}
if (-not $allowed) { throw "Staged change outside Scope" }

# Run checks
foreach ($c in $Checks) {
  & powershell -NoProfile -Command $c
  if ($LASTEXITCODE -ne 0) { throw "Check failed: $c" }
}

# Commit
git commit -m $Commit
```

---

### 4.5 Claude Code, Codex, Gemini (provider‑style ingestion)
These are typically accessed via **CLI wrappers or APIs/SDKs**. The universal block is passed as the **prompt payload**. With your setup, it’s common to route coding tasks to **DeepSeek via Ollama** locally; the same shape still applies.

**Generic HTTP (Ollama chat) example**
```bash
curl -s http://127.0.0.1:11434/api/chat \
  -H 'Content-Type: application/json' \
  -d '{
        "model": "deepseek-coder",
        "messages": [
          {"role":"user","content":"Task: Summarize src/logging\\nScope: src/logging/**\\nArtifacts: docs/logging-summary.md\\nSuccess: file created with key sections"}
        ]
      }'
```
> Swap the endpoint/fields per provider if calling their native APIs. The **prompt content** remains the universal shape.

---

## 5) Tiny PowerShell Adapter (lite, no Continue/OpenHands)
This adapter reads a **JSON request**, runs the chosen tool headlessly, captures stdout/stderr/exit code, and snapshots Git state before/after. Supported tools in this lite version: **aider**, **openinterpreter**, **opencode**, plus a generic **llm** (HTTP) and a **git** enforcement path.

> Set `env.OLLAMA_API_BASE` to point at your local Ollama (`http://127.0.0.1:11434`).

```powershell
<#! ToolAdapter_Lite.ps1 (no Continue/OpenHands) !>
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
  if(-not $p.WaitForExit($TimeoutSec*1000)){ try{$p.Kill($true)}catch{}; return @{exit=124;out=$out.Result;err=("TIMEOUT %ss"-f$TimeoutSec)+$err.Result;cmd="$Exe $($psi.Arguments)";start=$start;end=Get-Date} }
  return @{exit=$p.ExitCode;out=$out.Result;err=$err.Result;cmd="$Exe $($psi.Arguments)";start=$start;end=Get-Date}
}

function GitState([string]$path){ try{@{branch=(git -C $path rev-parse --abbrev-ref HEAD).Trim(); head=(git -C $path rev-parse HEAD).Trim(); dirty=([string]::IsNullOrWhiteSpace((git -C $path status --porcelain)) -eq $false)} }catch{ @{branch='';head='';dirty=$false} } }
function NewCommits($path,$before,$after){ if(!$before -or !$after -or $before -eq $after){return @()}; try{ (git -C $path rev-list "$before..$after" --no-merges).Trim().Split("`n")|?{$_} }catch{ @() } }

# Read request JSON
$reqJson = if($RequestPath){ Get-Content -Raw -Path $RequestPath } else { $input|Out-String }
if(-not $reqJson){ throw 'No JSON request provided.' }
$req = $reqJson | ConvertFrom-Json -Depth 8
$tool=($req.tool??'').ToLower(); $repo=($req.repo??(Get-Location).Path); $prompt=($req.prompt??''); $model=($req.model??$null)
$args=@($req.args)|?{$_}; $envH=@{}; if($req.env){ $req.env.psobject.Properties|%{ $envH[$_.Name]=[string]$_.Value } }
if(-not $envH.ContainsKey('OLLAMA_API_BASE')){ $envH['OLLAMA_API_BASE']='http://127.0.0.1:11434' }
$timeout=[int]($req.timeoutSec??600)

$before = GitState $repo

switch($tool){
  'aider' {
    $exe='aider'; $a=@(); if($model){$a+='--model';$a+=$model}; if($prompt){$a+='--message';$a+=$prompt}; $a+='--yes'; if($args.Count){$a+=$args}
    $r=Invoke-External -Exe $exe -Args $a -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
  }
  'openinterpreter' {
    $exe='python'; $tmp=[IO.Path]::Combine([IO.Path]::GetTempPath(),"oi_"+[Guid]::NewGuid().ToString('N')+".py")
    ($"from interpreter import interpreter\ninterpreter.chat(\"\"\"{($prompt -replace '"""','\"\"\"')}\"\"\")\n") | Set-Content -Encoding UTF8 -Path $tmp
    $r=Invoke-External -Exe $exe -Args @($tmp)+$args -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
    Remove-Item -Force $tmp -ErrorAction SilentlyContinue
  }
  'opencode' {
    $exe='opencode'; $a=@('run'); if($prompt){$a+=$prompt}; if($args.Count){$a+=$args}
    $r=Invoke-External -Exe $exe -Args $a -Cwd $repo -EnvVars $envH -TimeoutSec $timeout
  }
  'llm' {
    # Generic HTTP post (e.g., Ollama). Args[0]=endpoint, Args[1]=model (optional)
    $endpoint = if($args.Count -ge 1){ $args[0] } else { 'http://127.0.0.1:11434/api/chat' }
    $mdl = if($args.Count -ge 2){ $args[1] } else { 'deepseek-coder' }
    $body = @{ model=$mdl; messages=@(@{role='user';content=$prompt}) } | ConvertTo-Json -Depth 6
    $resp = Invoke-RestMethod -Method Post -Uri $endpoint -Body $body -ContentType 'application/json'
    $r = @{ exit=0; out=($resp|ConvertTo-Json -Depth 6); err=''; cmd="POST $endpoint"; start=Get-Date; end=Get-Date }
  }
  'git' {
    # Lightweight enforcement path: stage Scope, run Checks, commit
    $scope = @($req.scope) | ?{ $_ }
    $checks= @($req.checks) | ?{ $_ }
    $subject= ($req.commit ?? 'chore: automated change')
    foreach($p in $scope){ git -C $repo add $p }
    $changed = git -C $repo diff --name-only --cached | ?{ $_ }
    foreach($f in $changed){ if(-not ($scope | % { $f -like ("$_/*") -or $f -eq $_ })) { throw "Staged change outside Scope: $f" } }
    foreach($c in $checks){ & powershell -NoProfile -Command $c; if($LASTEXITCODE -ne 0){ throw "Check failed: $c" } }
    git -C $repo commit -m $subject
    $r=@{ exit=0; out='git enforcement OK'; err=''; cmd='git add+commit'; start=Get-Date; end=Get-Date }
  }
  default { throw "Unsupported tool '$tool'. Use: aider | openinterpreter | opencode | llm | git" }
}

$after = GitState $repo; $new = NewCommits $repo $before.head $after.head
$result = @{ ok=($r.exit -eq 0); tool=$tool; started=$r.start.ToUniversalTime().ToString('o'); finished=$r.end.ToUniversalTime().ToString('o'); duration_ms=[math]::Round(((Get-Date)-$r.start).TotalMilliseconds); exit_code=$r.exit; stdout=$r.out; stderr=$r.err; repo_state=@{branch=$after.branch; head_before=$before.head; head_after=$after.head; dirty_after=[bool]$after.dirty; new_commits=@($new)}; meta=@{command=$r.cmd; cwd=$repo} }
$result | ConvertTo-Json -Depth 8 -Compress
```

**Example requests**

*Aider one‑shot refactor*
```json
{
  "tool": "aider",
  "repo": "C:/dev/myrepo",
  "prompt": "Task: Extract logger into src/logging/*\nScope: src/logging/**; tests/logging/**\nChecks: ruff check . && pytest -q\nCommit: refactor(logging): extract handlers",
  "model": "ollama_chat/deepseek-coder:latest",
  "env": { "OLLAMA_API_BASE": "http://127.0.0.1:11434" }
}
```

*Open Interpreter (generate CSV)*
```json
{
  "tool": "openinterpreter",
  "repo": "C:/dev/myrepo",
  "prompt": "Task: list functions in src/logging\nScope: src/logging/**\nArtifacts: artifacts/functions.csv\nSuccess: CSV exists with 2 columns"
}
```

*OpenCode summary*
```json
{
  "tool": "opencode",
  "repo": "C:/dev/myrepo",
  "prompt": "Task: summarize src/logging\nScope: src/logging/**\nArtifacts: docs/logging-summary.md"
}
```

*Generic LLM via HTTP (Ollama DeepSeek)*
```json
{
  "tool": "llm",
  "repo": "C:/dev/myrepo",
  "prompt": "Task: Outline test plan for logging module\nScope: src/logging/**\nArtifacts: docs/logging-test-plan.md",
  "args": ["http://127.0.0.1:11434/api/chat", "deepseek-coder"]
}
```

*Git enforcement*
```json
{
  "tool": "git",
  "repo": "C:/dev/myrepo",
  "scope": ["src/logging", "tests/logging"],
  "checks": ["ruff check .", "pytest -q"],
  "commit": "refactor(logging): extract handlers and add tests"
}
```

---

## 6) Practical Tips
- Keep prompts **short and surgical**; prefer small diffs and frequent commits.
- Always include **Scope** and **Checks**—they convert prose into enforceable actions.
- Use **`--yes`** (Aider) and one‑shot runs (OpenCode) for headless operation.
- Route provider prompts through **Ollama** for local, predictable costs; swap models as needed.
- Log every run (append‑only JSONL) and store prompt blocks under `.runs/<RUN_ID>/prompts/` for audits.

---

## 7) Next Steps (optional)
- Add a `Convert-UniversalPrompt` step that renders the JSON form into the text block automatically for each tool.
- Wire the adapter into your quality gates: after each run, execute **Checks**, assert **Artifacts**, and fail fast if any condition is not met.
- Extend the adapter with additional tools as needed, keeping the same I/O contract.

