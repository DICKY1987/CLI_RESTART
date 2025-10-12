# OpenCode run wrapper for quick commands with DeepSeek
# Usage: .\opencode-deepseek-run.ps1 "your message here"

$model = "ollama/deepseek-coder-v2:lite"
$opencodeCmd = "opencode"

# Use opencode run command with DeepSeek model
& $opencodeCmd run -m $model @args
