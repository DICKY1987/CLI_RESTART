Param(
  [Parameter(Mandatory=$true)][string]$Question,
  [string]$ContextJson
)
$argsList = @('--question', $Question)
if ($ContextJson) { $argsList += @('--context_json', $ContextJson) }
& python "$PSScriptRoot\ask_deepseek.py" @argsList

