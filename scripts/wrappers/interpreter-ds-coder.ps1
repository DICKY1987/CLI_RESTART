[CmdletBinding()]
param(
  [string]$Model = 'deepseek-coder-v2:lite',
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$Args
)
$ErrorActionPreference = 'Stop'
if (-not $env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL = 'http://127.0.0.1:11434/v1' }
if (-not $env:OPENAI_API_KEY)  { $env:OPENAI_API_KEY  = 'ollama' }
try {
  & interpreter --model $Model @Args
} catch {
  Write-Host "Open Interpreter not found in PATH. Install via: pipx install open-interpreter" -ForegroundColor Yellow
  exit 1
}
