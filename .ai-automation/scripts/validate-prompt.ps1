<#
.SYNOPSIS
    Validate universal prompt JSON structure
.DESCRIPTION
    Checks that a task JSON file conforms to the universal prompt shape specification
.PARAMETER TaskFile
    Path to JSON task file to validate
.PARAMETER Strict
    Enable strict validation (require all recommended fields)
.EXAMPLE
    .\validate-prompt.ps1 -TaskFile task.json
    .\validate-prompt.ps1 -TaskFile task.json -Strict
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$TaskFile,
    [switch]$Strict
)

$ErrorActionPreference = 'Stop'

$REQUIRED_FIELDS = @('tool')
$RECOMMENDED_FIELDS = @('repo', 'prompt', 'timeoutSec')
$OPTIONAL_FIELDS = @('model', 'args', 'env', 'scope', 'checks', 'commit')
$VALID_TOOLS = @('aider', 'openinterpreter', 'opencode', 'claude', 'codex', 'gemini', 'llm', 'git')

function Write-ValidationResult([string]$msg, [string]$level='INFO'){
    $color = switch($level){
        'ERROR'   {'Red'}
        'WARN'    {'Yellow'}
        'SUCCESS' {'Green'}
        default   {'Cyan'}
    }
    $icon = switch($level){
        'ERROR'   {'✗'}
        'WARN'    {'⚠'}
        'SUCCESS' {'✓'}
        default   {'ℹ'}
    }
    Write-Host "$icon $msg" -ForegroundColor $color
}

if(-not (Test-Path $TaskFile)){
    Write-ValidationResult "Task file not found: $TaskFile" -level ERROR
    exit 1
}

Write-Host "`nValidating: $TaskFile`n" -ForegroundColor Cyan

# Parse JSON
try {
    $task = Get-Content -Raw $TaskFile | ConvertFrom-Json -Depth 8
} catch {
    Write-ValidationResult "Invalid JSON: $($_.Exception.Message)" -level ERROR
    exit 1
}

$errors = 0
$warnings = 0

# Check required fields
foreach($field in $REQUIRED_FIELDS){
    if(-not $task.PSObject.Properties.Name.Contains($field)){
        Write-ValidationResult "Missing required field: $field" -level ERROR
        $errors++
    } else {
        Write-ValidationResult "Required field present: $field" -level SUCCESS
    }
}

# Check recommended fields
foreach($field in $RECOMMENDED_FIELDS){
    if(-not $task.PSObject.Properties.Name.Contains($field)){
        $msg = "Missing recommended field: $field"
        if($Strict){
            Write-ValidationResult $msg -level ERROR
            $errors++
        } else {
            Write-ValidationResult $msg -level WARN
            $warnings++
        }
    } else {
        Write-ValidationResult "Recommended field present: $field" -level SUCCESS
    }
}

# Validate tool value
if($task.tool){
    $toolLower = $task.tool.ToLower()
    if($VALID_TOOLS -contains $toolLower){
        Write-ValidationResult "Valid tool: $($task.tool)" -level SUCCESS
    } else {
        Write-ValidationResult "Invalid tool: $($task.tool). Valid: $($VALID_TOOLS -join ', ')" -level ERROR
        $errors++
    }

    # Tool-specific validation
    if($toolLower -eq 'git'){
        if(-not $task.scope){
            Write-ValidationResult "Git tool requires 'scope' field" -level ERROR
            $errors++
        }
        if(-not $task.checks){
            Write-ValidationResult "Git tool should have 'checks' field" -level WARN
            $warnings++
        }
        if(-not $task.commit){
            Write-ValidationResult "Git tool should have 'commit' field" -level WARN
            $warnings++
        }
    }

    if($toolLower -in @('aider','openinterpreter','opencode','claude','codex','gemini')){
        if(-not $task.prompt -or [string]::IsNullOrWhiteSpace($task.prompt)){
            Write-ValidationResult "Tool '$($task.tool)' requires non-empty 'prompt' field" -level ERROR
            $errors++
        }
    }
}

# Validate repo path if present
if($task.repo -and $task.repo -ne '.'){
    if(-not (Test-Path $task.repo)){
        Write-ValidationResult "Repo path does not exist: $($task.repo)" -level WARN
        $warnings++
    }
}

# Validate timeout
if($task.timeoutSec){
    if($task.timeoutSec -lt 1 -or $task.timeoutSec -gt 3600){
        Write-ValidationResult "Timeout should be between 1 and 3600 seconds" -level WARN
        $warnings++
    }
}

# Check for unrecognized fields
$allKnownFields = $REQUIRED_FIELDS + $RECOMMENDED_FIELDS + $OPTIONAL_FIELDS + @('name','description','placeholders','usage')
foreach($prop in $task.PSObject.Properties.Name){
    if($allKnownFields -notcontains $prop){
        Write-ValidationResult "Unrecognized field: $prop" -level WARN
        $warnings++
    }
}

# Universal prompt shape validation (if prompt field exists)
if($task.prompt){
    $prompt = $task.prompt
    $expectedSections = @('Task:', 'Scope:', 'Constraints:', 'Checks:', 'Artifacts:', 'Commit:', 'Success:')
    $foundSections = @()

    foreach($section in $expectedSections){
        if($prompt -match [regex]::Escape($section)){
            $foundSections += $section
        }
    }

    if($foundSections.Count -ge 4){
        Write-ValidationResult "Prompt follows universal shape (found $($foundSections.Count)/7 sections)" -level SUCCESS
    } elseif($foundSections.Count -gt 0) {
        Write-ValidationResult "Prompt partially follows universal shape ($($foundSections.Count)/7 sections)" -level WARN
        $warnings++
    } else {
        Write-ValidationResult "Prompt does not follow universal shape (consider adding: Task, Scope, Checks, etc.)" -level WARN
        $warnings++
    }
}

# Summary
Write-Host "`n---`n" -ForegroundColor Gray
if($errors -eq 0 -and $warnings -eq 0){
    Write-ValidationResult "Validation passed with no issues!" -level SUCCESS
    exit 0
} elseif($errors -eq 0){
    Write-ValidationResult "Validation passed with $warnings warning(s)" -level WARN
    exit 0
} else {
    Write-ValidationResult "Validation failed with $errors error(s) and $warnings warning(s)" -level ERROR
    exit 1
}
