Shell completion for cli-orchestrator

Supported shells
- bash
- zsh
- PowerShell

Generate scripts
- python scripts/generate_completions.py

Install
- bash: copy completions/bash/cli-orchestrator to /etc/bash_completion.d/ or source it in ~/.bashrc
- zsh: copy completions/zsh/_cli-orchestrator into a directory in $fpath and run `compinit`
- PowerShell: Add the path to your profile: `Invoke-Expression (Get-Content completions/powershell/cli-orchestrator.ps1 -Raw)`

CI/Release
- Release workflow packages completion scripts as artifacts.
