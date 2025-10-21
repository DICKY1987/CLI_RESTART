<#
.SYNOPSIS
    User-friendly wrapper for running AI automation tasks
.DESCRIPTION
    Executes tasks using the ToolAdapter with convenient parameter handling and output formatting
.PARAMETER TaskFile
    Path to JSON task file (absolute or relative to .ai-automation/prompts/)
.PARAMETER Template
    Use a predefined template (e.g., "testing/generate-tests")
.PARAMETER Variables
    Hashtable of placeholder replacements (e.g., @{TARGET_MODULE="src/core.py"})
.PARAMETER OutputJson
    Path to save result JSON
.PARAMETER Quiet
    Suppress verbose output, only show final result
.EXAMPLE
    .\run-task.ps1 -Template testing/generate-tests -Variables @{TARGET_MODULE="src/utils/logger.py"; TARGET_FILE="logger"}
.EXAMPLE
    .\run-task.ps1 -TaskFile custom-task.json -OutputJson result.json
#>
[CmdletBinding(DefaultParameterSetName='TaskFile')]
param(
    [Parameter(ParameterSetName='TaskFile', Mandatory=$true)]
    [string]$TaskFile,

    [Parameter(ParameterSetName='Template', Mandatory=$true)]
    [string]$Template,

    [Parameter(ParameterSetName='Template')]
    [hashtable]$Variables = @{},

    [string]$OutputJson,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$adapterPath = Join-Path $rootDir "ToolAdapter.ps1"

function Write-Status([string]$msg, [string]$level='INFO'){
    if($Quiet){return}
    $color = switch($level){
        'ERROR'   {'Red'}
        'WARN'    {'Yellow'}
        'SUCCESS' {'Green'}
        default   {'Cyan'}
    }
    Write-Host "[$level] $msg" -ForegroundColor $color
}

# Resolve task file
if($PSCmdlet.ParameterSetName -eq 'Template'){
    $TaskFile = Join-Path $rootDir "prompts\$Template.json"
    if(-not (Test-Path $TaskFile)){
        Write-Status "Template not found: $Template" -level ERROR
        Write-Status "Available templates:" -level INFO
        Get-ChildItem (Join-Path $rootDir "prompts") -Recurse -Filter *.json | ForEach-Object {
            $rel = $_.FullName.Replace((Join-Path $rootDir "prompts\"), "").Replace(".json", "")
            Write-Host "  - $rel" -ForegroundColor Gray
        }
        exit 1
    }
}

if(-not (Test-Path $TaskFile)){
    Write-Status "Task file not found: $TaskFile" -level ERROR
    exit 1
}

Write-Status "Loading task: $TaskFile"

# Load and process task JSON
$taskJson = Get-Content -Raw $TaskFile | ConvertFrom-Json -Depth 8

# Replace placeholders if variables provided
if($Variables.Count -gt 0){
    Write-Status "Applying variables: $($Variables.Keys -join ', ')"
    $taskStr = $taskJson | ConvertTo-Json -Depth 8
    foreach($key in $Variables.Keys){
        $value = $Variables[$key]
        $taskStr = $taskStr -replace "\{$key\}", $value
    }
    $taskJson = $taskStr | ConvertFrom-Json -Depth 8
}

# Resolve repo path if relative
if($taskJson.repo -and $taskJson.repo -eq '.'){
    $taskJson.repo = (Get-Location).Path
}

# Convert back to JSON for adapter
$requestJson = $taskJson | ConvertTo-Json -Depth 8

Write-Status "Executing task with tool: $($taskJson.tool)"
Write-Status "Target repo: $($taskJson.repo)"

# Execute via adapter
try {
    $result = $requestJson | & $adapterPath
    $resultObj = $result | ConvertFrom-Json -Depth 8

    if($resultObj.ok){
        Write-Status "Task completed successfully!" -level SUCCESS
        Write-Status "Duration: $($resultObj.duration_ms)ms"
        if($resultObj.repo_state.new_commits.Count -gt 0){
            Write-Status "New commits: $($resultObj.repo_state.new_commits.Count)" -level SUCCESS
            $resultObj.repo_state.new_commits | ForEach-Object {
                Write-Host "  - $_" -ForegroundColor Green
            }
        }
    } else {
        Write-Status "Task failed with exit code: $($resultObj.exit_code)" -level ERROR
        if($resultObj.stderr){
            Write-Status "Error output:" -level ERROR
            Write-Host $resultObj.stderr -ForegroundColor Red
        }
    }

    # Save output if requested
    if($OutputJson){
        $result | Set-Content -Path $OutputJson -Encoding UTF8
        Write-Status "Result saved to: $OutputJson"
    }

    # Show stdout/stderr if not quiet
    if(-not $Quiet){
        if($resultObj.stdout){
            Write-Host "`nStdout:" -ForegroundColor Cyan
            Write-Host $resultObj.stdout
        }
        if($resultObj.stderr -and $resultObj.ok){
            Write-Host "`nStderr:" -ForegroundColor Yellow
            Write-Host $resultObj.stderr
        }
    }

    # Exit with appropriate code
    exit $resultObj.exit_code

} catch {
    Write-Status "Execution failed: $($_.Exception.Message)" -level ERROR
    exit 1
}
