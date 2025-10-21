
<#PSScriptInfo
.VERSION 2.0.0
.GUID 2b2a937a-6b9d-4f77-9d6c-d4a16b3f0c0e
.AUTHOR YourName
.COMPANYNAME Local
.COPYRIGHT (c) 2025
#>

<#
.SYNOPSIS
    Configures Aider, Continue, OpenHands, Open Interpreter, and OpenCode to use DeepSeek models via Ollama (Windows).

.DESCRIPTION
    Applies enterprise-grade practices:
      - Structured logging (JSON) with correlation IDs and multi-target output.
      - Centralized error handling with standardized exit codes.
      - Config discovery from SharedConfig.psd1 and environment variables.
      - Schema-based parameter validation and rich, descriptive error messaging.
      - Safe operations with -WhatIf / -Confirm (SupportsShouldProcess).

.PARAMETER Models
    One or more DeepSeek model tags to pull via Ollama (e.g., "deepseek-coder:latest", "deepseek-r1:latest").

.PARAMETER OllamaHost
    Base URL for the Ollama server (including protocol and port), e.g. http://127.0.0.1:11434

.PARAMETER InstallIfMissing
    If specified, attempts to install missing prerequisites (Ollama via winget).

.PARAMETER Force
    If specified, bypasses some safety prompts (still honors -WhatIf).

.EXAMPLE
    .\Setup-DeepSeek-Ollama-Apps.Refactored.ps1 -InstallIfMissing -Verbose

.EXAMPLE
    .\Setup-DeepSeek-Ollama-Apps.Refactored.ps1 -Models 'deepseek-r1:32b','deepseek-coder:latest' -WhatIf

.NOTES
    - Re-open terminals/VS Code after running to pick up environment changes.
    - Script is idempotent: repeated runs reconcile configs instead of overwriting blindly.
#>

[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
param(
    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string[]]$Models = @('deepseek-coder:latest','deepseek-r1:latest'),

    [Parameter()]
    [ValidatePattern('^https?://[a-zA-Z0-9\.\-]+(:\d+)?$')]
    [string]$OllamaHost = 'http://127.0.0.1:11434',

    [Parameter()]
    [switch]$InstallIfMissing,

    [Parameter()]
    [switch]$Force
)

# =============================================================================
# Bootstrap: Correlation, Paths, Defaults
# =============================================================================

$ErrorActionPreference = 'Stop'
$PSStyle.OutputRendering = 'Host' 2>$null

$CorrelationId = [Guid]::NewGuid().ToString('N').Substring(0,8)

$UserHome  = $env:USERPROFILE
$BinDir    = Join-Path $UserHome 'bin'
$LogBase   = $env:LOG_BASE_PATH
if (-not $LogBase) { $LogBase = Join-Path $UserHome 'Automation\Logs' }
$LogFile   = Join-Path $LogBase ("Setup-DeepSeek-Ollama-Apps_{0:yyyy-MM-dd}.log" -f (Get-Date))

$ContinueDir     = Join-Path $UserHome '.continue'
$ContinueConfig  = Join-Path $ContinueDir 'config.yaml'

$AiderSettings   = Join-Path $UserHome '.aider.model.settings.yml'
$AiderWrapper    = Join-Path $BinDir 'aider-ds-coder.ps1'

$InterpreterWrap = Join-Path $BinDir 'interpreter-ds-coder.ps1'

$OCDir           = Join-Path $UserHome '.config\opencode'
$OCConfig        = Join-Path $OCDir 'opencode.json'
$OCFallback      = Join-Path $UserHome '.opencode.json'

# =============================================================================
# Fallback Implementations (if user's shared modules aren't available)
# =============================================================================

function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('Debug','Info','Warning','Error','Critical')][string]$Level,
        [Parameter(Mandatory)][string]$Message,
        [string]$Category = 'Application',
        [int]$EventId = 0,
        [hashtable]$Data = @{},
        [System.Exception]$Exception,
        [string]$Recommendation,
        [string]$Source = $($MyInvocation.MyCommand.Name)
    )

    $entry = [ordered]@{
        timestamp      = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
        level          = $Level
        message        = $Message
        category       = $Category
        eventId        = $EventId
        correlationId  = $CorrelationId
        source         = $Source
        user           = $env:USERNAME
        computer       = $env:COMPUTERNAME
        data           = $Data
        recommendation = $Recommendation
    }

    if ($Exception) {
        $entry.exception = @{
            type    = $Exception.GetType().FullName
            message = $Exception.Message
            stack   = $Exception.ScriptStackTrace
        }
    }

    $json = $entry | ConvertTo-Json -Depth 6

    # Console
    if ($Level -in @('Error','Critical')) {
        Write-Error ($json)
    } elseif ($Level -eq 'Warning') {
        Write-Warning ($json)
    } else {
        Write-Host $json
    }

    # File
    try {
        if (-not (Test-Path $LogBase)) { New-Item -ItemType Directory -Force -Path $LogBase | Out-Null }
        Add-Content -Path $LogFile -Value $json
    } catch {
        Write-Warning "Failed to write log file: $($_.Exception.Message)"
    }
}

# If user's Write-StructuredLog exists, shim to it for richer logging
if (Get-Command -Name Write-StructuredLog -ErrorAction SilentlyContinue) {
    Remove-Item Function:\Write-Log -Force -ErrorAction SilentlyContinue
    function Write-Log {
        [CmdletBinding()]
        param(
            [Parameter(Mandatory)][ValidateSet('Debug','Info','Warning','Error','Critical')][string]$Level,
            [Parameter(Mandatory)][string]$Message,
            [string]$Category = 'Application',
            [int]$EventId = 0,
            [hashtable]$Data = @{},
            [System.Exception]$Exception,
            [string]$Recommendation,
            [string]$Source = $($MyInvocation.MyCommand.Name)
        )
        Write-StructuredLog -Level $Level -Message $Message -Data $Data -Exception $Exception -CorrelationId $CorrelationId -Category $Category -EventId $EventId -Source $Source
    }
    Write-Log -Level Debug -Message "Using Write-StructuredLog"
} else {
    Write-Log -Level Debug -Message "Using internal JSON logger"
}

# Central error handler (fallback)
function Invoke-ErrorHandler {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][System.Exception]$Exception,
        [string]$UserMessage = "An unexpected error occurred.",
        [string]$RootCause,
        [string]$SuggestedFix,
        [string]$NextSteps,
        [string]$Source = $($MyInvocation.MyCommand.Name),
        [int]$ExitCode = 100,
        [hashtable]$Context = @{}
    )

    $msg = @"
$UserMessage
— Root Cause: $RootCause
— Suggested Fix: $SuggestedFix
— Next Steps: $NextSteps
"@.Trim()

    Write-Log -Level Error -Message $msg -Data @{ Context = $Context } -Exception $Exception -Category 'System' -EventId $ExitCode -Source $Source

    # If user's framework is available, surface richer object
    if (Get-Command -Name Invoke-AutomationErrorHandler -ErrorAction SilentlyContinue) {
        return Invoke-AutomationErrorHandler -Exception $Exception -Context $Context -Source $Source -UserMessage $UserMessage
    } else {
        return [pscustomobject]@{
            CorrelationId = $CorrelationId
            ExitCode      = $ExitCode
            UserMessage   = $UserMessage
            RootCause     = $RootCause
            SuggestedFix  = $SuggestedFix
            NextSteps     = $NextSteps
            Context       = $Context
        }
    }
}

# =============================================================================
# Config Discovery (psd1/env) + Parameter Validation
# =============================================================================

function Get-SetupConfig {
    [CmdletBinding()]
    param(
        [string]$SharedConfigPath = (Join-Path $PSScriptRoot 'Config\SharedConfig.psd1')
    )

    $config = @{
        Logging = @{
            LogPath = $LogBase
        }
        Execution = @{
            ErrorActionPreference = 'Stop'
        }
    }

    try {
        if (Get-Command -Name Get-AutomationConfig -ErrorAction SilentlyContinue) {
            $cfg = Get-AutomationConfig -ErrorAction Stop
            if ($cfg.Logging.LogPath) { $config.Logging.LogPath = $cfg.Logging.LogPath }
            return $config
        }

        if (Test-Path $SharedConfigPath) {
            $psd1 = Import-PowerShellDataFile -Path $SharedConfigPath
            if ($psd1.Logging -and $psd1.Logging.LogPath) {
                $config.Logging.LogPath = $psd1.Logging.LogPath
            }
        }

        # .env style env vars
        if ($env:LOG_BASE_PATH) { $config.Logging.LogPath = $env:LOG_BASE_PATH }

        return $config
    }
    catch {
        Write-Log -Level Warning -Message "Config discovery failed, continuing with defaults." -Exception $_
        return $config
    }
}

function Test-SetupParameters {
    [CmdletBinding()]
    param(
        [string[]]$Models,
        [string]$OllamaHost
    )

    # Use user's Test-AutomationParameters if present
    if (Get-Command -Name Test-AutomationParameters -ErrorAction SilentlyContinue -CommandType Function) {
        $schema = New-Object PSObject -Property @{ } # placeholder if their New-AutomationInputSchema isn't present
        try {
            $params = @{ Models = $Models; OllamaHost = $OllamaHost }
            $result = Test-AutomationParameters -Parameters $params -Schema $schema -AllowPartial -TransformValues
            if (-not $result.IsValid) {
                throw "Parameter validation failed: $($result.Errors -join '; ')"
            }
        } catch {
            throw
        }
    } else {
        # Lightweight local checks
        foreach ($m in $Models) {
            if ([string]::IsNullOrWhiteSpace($m) -or $m -notmatch '^[a-z0-9\-\.:]+$') {
                throw "Invalid model tag: '$m'. Expected lowercase letters, numbers, '-', ':', '.'"
            }
        }
        if ($OllamaHost -notmatch '^https?://[a-zA-Z0-9\.\-]+(:\d+)?$') {
            throw "OllamaHost must be a URL like http://127.0.0.1:11434"
        }
    }
}

# =============================================================================
# Utilities
# =============================================================================

function Ensure-Command {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Cmd,
        [string]$WingetId
    )
    $found = Get-Command $Cmd -ErrorAction SilentlyContinue
    if (-not $found) {
        if ($InstallIfMissing -and $WingetId) {
            if ($PSCmdlet.ShouldProcess("$Cmd", "Install via winget $WingetId")) {
                try {
                    winget install --id $WingetId -e --accept-source-agreements --accept-package-agreements | Out-Null
                    Write-Log -Level Info -Message "Installed $Cmd via winget ($WingetId)"
                } catch {
                    $eh = Invoke-ErrorHandler -Exception $_ -UserMessage "Failed installing prerequisite: $Cmd" `
                        -RootCause "winget install error or package unavailable" `
                        -SuggestedFix "Check winget sources and try manual install from vendor" `
                        -NextSteps "Install $Cmd and re-run the script" `
                        -ExitCode 31 -Context @{ Command = $Cmd; WingetId = $WingetId }
                    throw ($eh.UserMessage)
                }
            }
        } else {
            throw "Command not found: $Cmd. Install it or re-run with -InstallIfMissing."
        }
    }
}

function Set-UserEnvVar {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Value
    )

    if ($PSCmdlet.ShouldProcess("env:$Name", "Set to $Value (User scope)")) {
        [Environment]::SetEnvironmentVariable($Name, $Value, "User")
        Write-Log -Level Info -Message "Set user env var" -Data @{ Name = $Name; Value = $Value }
    }
}

function Write-FileIfChanged {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [switch]$AsJson
    )

    $dir = Split-Path -Parent $Path
    if (-not (Test-Path $dir)) {
        if ($PSCmdlet.ShouldProcess($dir, "Create directory")) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
        }
    }

    $existing = ''
    if (Test-Path $Path) {
        $existing = Get-Content -Path $Path -Raw -ErrorAction SilentlyContinue
    }
    if ($AsJson) {
        # Normalize JSON for comparison
        try {
            $existingJson = if ($existing) { ($existing | ConvertFrom-Json -ErrorAction Stop | ConvertTo-Json -Depth 10) } else { '' }
            $newJson = ($Content | ConvertFrom-Json | ConvertTo-Json -Depth 10)
            $shouldWrite = ($existingJson -ne $newJson)
            $final = $newJson
        } catch {
            $shouldWrite = $true
            $final = $Content
        }
    } else {
        $shouldWrite = ($existing -ne $Content)
        $final = $Content
    }

    if ($shouldWrite) {
        if ($PSCmdlet.ShouldProcess($Path, "Write file")) {
            Set-Content -Encoding UTF8 -Path $Path -Value $final
            Write-Log -Level Info -Message "Wrote file" -Data @{ Path = $Path }
        }
    } else {
        Write-Log -Level Debug -Message "No change for file" -Data @{ Path = $Path }
    }
}

# =============================================================================
# Main
# =============================================================================

try {
    # Config & Validation
    $cfg = Get-SetupConfig
    if ($cfg.Logging.LogPath) {
        $LogBase = $cfg.Logging.LogPath
        $LogFile = Join-Path $LogBase ("Setup-DeepSeek-Ollama-Apps_{0:yyyy-MM-dd}.log" -f (Get-Date))
    }
    Write-Log -Level Info -Message "Starting setup" -Data @{ Models = $Models; OllamaHost = $OllamaHost }

    Test-SetupParameters -Models $Models -OllamaHost $OllamaHost

    # Prereqs
    Ensure-Command -Cmd 'powershell' # itself
    Ensure-Command -Cmd 'ollama' -WingetId 'Ollama.Ollama'

    # Pull models
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        foreach ($m in $Models) {
            try {
                if ($PSCmdlet.ShouldProcess("ollama model $m","Pull")) {
                    & ollama pull $m | Out-Null
                    Write-Log -Level Info -Message "Pulled Ollama model" -Data @{ Model = $m }
                }
            } catch {
                $eh = Invoke-ErrorHandler -Exception $_ -UserMessage "Failed to pull Ollama model: $m" `
                    -RootCause "Model tag is invalid or Ollama service not running" `
                    -SuggestedFix "Verify 'ollama serve' is running and the model tag exists. Try: 'ollama list' or 'ollama pull <model>' manually." `
                    -NextSteps "Correct the model tag or start Ollama, then rerun." `
                    -ExitCode 33 -Context @{ Model = $m; Host = $OllamaHost }
                throw ($eh.UserMessage)
            }
        }
    }

    # Env vars for OpenAI-compatible clients
    Set-UserEnvVar -Name 'OLLAMA_API_BASE' -Value $OllamaHost
    Set-UserEnvVar -Name 'OPENAI_API_BASE' -Value "$OllamaHost/v1"
    Set-UserEnvVar -Name 'OPENAI_BASE_URL' -Value "$OllamaHost/v1"
    Set-UserEnvVar -Name 'OPENAI_API_KEY'  -Value 'ollama'

    # Continue config
    $continueYaml = @"
name: Local DeepSeek via Ollama
version: 0.0.2
schema: v1

models:
  - name: DeepSeek Coder (Ollama)
    provider: ollama
    model: deepseek-coder:latest
    apiBase: $OllamaHost
    roles: [chat, edit, apply, autocomplete, rerank]

  - name: DeepSeek R1 (Ollama)
    provider: ollama
    model: deepseek-r1:latest
    apiBase: $OllamaHost
    roles: [chat]
"@
    Write-FileIfChanged -Path $ContinueConfig -Content $continueYaml

    # Aider: model settings + wrapper
    $aiderModelSettings = @"
- name: ollama/deepseek-coder:latest
  extra_params:
    num_ctx: 32768
"@
    Write-FileIfChanged -Path $AiderSettings -Content $aiderModelSettings
    $aiderWrapperContent = @"
# Launch Aider using DeepSeek Coder via Ollama
param([string]\$Repo = (Get-Location).Path)
Set-Location \$Repo
aider --model ollama_chat/deepseek-coder:latest
"@
    Write-FileIfChanged -Path $AiderWrapper -Content $aiderWrapperContent

    # Open Interpreter wrapper
    $oiWrapperContent = @"
# Launch Open Interpreter pointed at Ollama's OpenAI-compatible endpoint
interpreter --api_base $($OllamaHost)/v1 --model deepseek-coder:latest
"@
    if (-not (Test-Path $BinDir)) {
        if ($PSCmdlet.ShouldProcess($BinDir, "Create bin directory")) {
            New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
        }
    }
    Write-FileIfChanged -Path $InterpreterWrap -Content $oiWrapperContent

    # OpenCode config
    $opencodeJson = @"
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "name": "Ollama (local)",
      "options": { "baseURL": "$($OllamaHost)/v1" },
      "models": {
        "deepseek-coder:latest": { "name": "DeepSeek Coder (local)" },
        "deepseek-r1:latest":    { "name": "DeepSeek R1 (local)" }
      }
    }
  },
  "model": "ollama/deepseek-coder:latest"
}
"@
    Write-FileIfChanged -Path $OCConfig -Content $opencodeJson -AsJson
    Write-FileIfChanged -Path $OCFallback -Content $opencodeJson -AsJson

    Write-Log -Level Info -Message "Setup complete. Restart shells/VS Code to pick up env changes." -Data @{
        AiderWrapper = $AiderWrapper
        InterpreterWrapper = $InterpreterWrap
        ContinueConfig = $ContinueConfig
        OpenCodeConfig = $OCConfig
        LogFile = $LogFile
    }

} catch {
    $eh = Invoke-ErrorHandler -Exception $_ `
        -UserMessage "Setup failed — see logs for details (CorrelationId: $CorrelationId)." `
        -RootCause "One or more steps could not be completed (dependency, permissions, or configuration issue)." `
        -SuggestedFix "Review the JSON logs, fix the indicated step, and re-run. Try -InstallIfMissing for prerequisites and run PowerShell as admin if necessary." `
        -NextSteps "If failures persist, run with -Verbose and share the log file when seeking support." `
        -ExitCode 84 -Context @{ Step = 'TopLevel'; Models = $Models; Host = $OllamaHost }
    Write-Host "ERROR: $($eh.UserMessage)"
    exit $eh.ExitCode
}
