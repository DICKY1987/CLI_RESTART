# OpenCode wrapper script to use DeepSeek via Ollama
# Usage: .\opencode-deepseek.ps1 [project] [options]

$model = "ollama/deepseek-coder-v2:lite"
$opencodeCmd = "opencode"

# Pass all arguments to opencode with the -m flag
& $opencodeCmd -m $model @args
