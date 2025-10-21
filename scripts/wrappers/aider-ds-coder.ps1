[CmdletBinding()]
param(
  [string]$Model = 'ollama_chat/deepseek-coder-v2:lite',
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$Args
)
$ErrorActionPreference = 'Stop'
if (-not $env:OLLAMA_API_BASE) { $env:OLLAMA_API_BASE = 'http://127.0.0.1:11434' }
try {
  & aider --model $Model @Args
} catch {
  Write-Host "Aider CLI not found. Install via: pipx install aider-install"
  exit 1
}
