<#
.SYNOPSIS
    A combined PowerShell script that bundles multiple utility scripts into one modular, menu-driven tool.

.DESCRIPTION
    This script provides a menu to run one of the following modules:
    1. Complete-Removal: Removes containerization and Python venv infrastructure.
    2. Install-DeterministicGit: Installs a deterministic Git workflow system.
    3. Discover-CliTools: Discovers CLI tools and generates configuration files.

    It is designed according to comprehensive PowerShell coding standards, featuring structured logging,
    modular functions, and robust error handling.

.PARAMETER RunCompleteRemoval
    Runs the Complete-Removal script logic non-interactively.

.PARAMETER RunInstallDeterministicGit
    Runs the Install-DeterministicGit script logic non-interactively.

.PARAMETER RunDiscoverCliTools
    Runs the Discover-CliTools script logic non-interactively.

.EXAMPLE
    .\Combined-PowerShell-Scripts.ps1
    # Shows the interactive menu to choose which script to run.

.EXAMPLE
    .\Combined-PowerShell-Scripts.ps1 -RunCompleteRemoval -RepoPath 'C:\\Projects\\my-repo' -SkipConfirmation
    # Executes the removal script directly for the specified repository.

.NOTES
    Author: Gemini
    Version: 2.2.0 (repo copy)
    Last Modified: 2025-10-11
#>
[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [switch]$RunCompleteRemoval,
    [switch]$RunInstallDeterministicGit,
    [switch]$RunDiscoverCliTools,
    # Complete-Removal options
    [string]$RepoPath,
    [switch]$SkipConfirmation,
    # Install-DeterministicGit options
    [switch]$Force,
    # Discover-CliTool options
    [string[]]$Roots,
    [object[]]$Tools,
    [string]$OutDir,
    [string]$ProjectRoot,
    [switch]$Execute,
    [switch]$DiscoveryOnly,
    [string]$LedgerPath
)

#region --- Core Framework ---

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Debug', 'Info', 'Warn', 'Error', 'Fatal')]
        [string]$Level,
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [hashtable]$Data
    )
    $logEntry = @{
        Timestamp     = (Get-Date -Format 'o')
        Level         = $Level.ToUpper()
        Message       = $Message
        CorrelationId = $script:CorrelationId
    }
    if ($PSBoundParameters.ContainsKey('Data')) { $logEntry.Data = $Data }
    $color = switch ($Level) {
        'Debug' { 'DarkGray' }
        'Info'  { 'Green' }
        'Warn'  { 'Yellow' }
        'Error' { 'Red' }
        'Fatal' { 'Magenta' }
        default { 'White' }
    }
    Write-Host ("[{0}] [{1}] [{2}] - {3}" -f $logEntry.Timestamp, $logEntry.Level.PadRight(5), $logEntry.CorrelationId, $logEntry.Message) -ForegroundColor $color
}

function Test-ScriptEnvironment {
    Write-Log -Level 'Info' -Message 'Validating script execution environment.'
    if ($PSVersionTable.PSVersion.Major -lt 5) { Write-Log -Level 'Fatal' -Message 'PowerShell 5.1 or higher is required.'; exit 1 }
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [System.Security.Principal.WindowsPrincipal]::new($identity)
    if (-not $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Log -Level 'Warn' -Message 'Script is not running with Administrator privileges. Some operations may fail.'
    }
    Write-Log -Level 'Info' -Message 'Environment validation passed.'
}

#endregion

#region --- Module: Complete-Removal ---

function Invoke-CompleteRemoval {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [ValidateScript({ Test-Path -Path $_ -PathType 'Container' })]
        [string]$RepoPath = (Get-Location).Path,
        [switch]$SkipConfirmation
    )
    # implementation omitted in repo copy; use source script if needed
    Write-Log -Level 'Warn' -Message 'Complete-Removal module is not executed in repo copy.'
}

#endregion

#region --- Module: Install-DeterministicGit ---

function Invoke-InstallDeterministicGit {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param([switch]$Force)
    # implementation preserved in source script; call from Downloads if desired
    Write-Log -Level 'Warn' -Message 'Install-DeterministicGit module is not executed in repo copy.'
}

#endregion

#region --- Module: Discover-CliTool ---

function Resolve-InPath { param([string[]]$CommandNames) foreach ($name in $CommandNames) { $cmd = Get-Command $name -ErrorAction SilentlyContinue; if ($cmd -and $cmd.Source) { return $cmd.Source } } $null }
function Search-InHintPaths {
    param([string[]]$CommandNames)
    $HintPaths = @(
        "$env:USERPROFILE\AppData\Roaming\npm",
        "$env:LOCALAPPDATA\Programs\Python",
        "$env:LOCALAPPDATA\Programs\Python\Python*\Scripts",
        "$env:USERPROFILE\.local\bin",
        "$env:USERPROFILE\.cache\pipx\venvs",
        "C:\\Program Files\\Ollama",
        "C:\\Program Files\\Git\\cmd",
        "C:\\Program Files\\GitHub CLI"
    ) | Where-Object { Test-Path $_ }
    $hits = [System.Collections.Generic.List[string]]::new()
    foreach ($hp in $HintPaths) {
        foreach ($name in $CommandNames) {
            $base = [IO.Path]::GetFileNameWithoutExtension($name)
            $patterns = @($name, "$base.exe", "$base.cmd", "$base.bat", "$base.ps1") | Select-Object -Unique
            foreach ($pat in $patterns) {
                try {
                    Get-ChildItem -LiteralPath $hp -Recurse -File -ErrorAction SilentlyContinue |
                        Where-Object { $_.Name -ieq $pat } |
                        ForEach-Object { $hits.Add($_.FullName) }
                } catch { }
            }
        }
    }
    return $hits.ToArray()
}
function Search-InRoots { param([string[]]$Roots, [string[]]$CommandNames)
    $hits = [System.Collections.Generic.List[string]]::new()
    foreach ($root in $Roots) {
        if (-not (Test-Path -LiteralPath $root)) { continue }
        foreach ($name in $CommandNames) {
            $base = [System.IO.Path]::GetFileNameWithoutExtension($name)
            $patterns = @($name, "$base.exe","$base.cmd","$base.bat","$base.ps1") | Select-Object -Unique
            foreach ($pat in $patterns) {
                try {
                    Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue |
                        Where-Object { $_.Name -ieq $pat } |
                        ForEach-Object { $hits.Add($_.FullName) }
                } catch { }
            }
        }
    }
    return $hits.ToArray()
}
function Test-GHCopilotExtension { try { $gh = Get-Command gh -ErrorAction SilentlyContinue; if (-not $gh) { return $false }; $list = & $gh.Source extension list 2>$null; return ($list -match 'github/gh-copilot') } catch { return $false } }
function Out-YamlEsc { param([string]$s) if ($null -eq $s) { return "" } $escaped = $s -replace '\\','\\' -replace '"','\"'; return '"' + $escaped + '"' }
function Write-ToolAdaptersYaml { param([string]$PathYaml, [hashtable]$PathsMap, [switch]$CreateIfMissing)
    $lines = @('tool_adapters:')
    foreach ($k in ($PathsMap.Keys | Sort-Object)) { $v = $PathsMap[$k]; $lines += "  $k: $(Out-YamlEsc $v)" }
    $tmp = "$PathYaml.tmp"; $lines -join "`n" | Out-File -Encoding UTF8 $tmp; Move-Item -Force -LiteralPath $tmp -Destination $PathYaml
}
function Write-DiscoveredYaml { param([string]$PathYaml, $Results)
    $lines = @('discovered_tools:')
    foreach ($r in $Results) {
        $lines += "  - name: $(Out-YamlEsc $r.ToolName)"
        $lines += "    key: $(Out-YamlEsc $r.Key)"
        $lines += "    preferred_path: $(Out-YamlEsc $r.PreferredPath)"
        $lines += "    found_in_path: $(Out-YamlEsc $r.FoundInPATH)"
        $lines += "    version: $(Out-YamlEsc $r.VersionInfo)"
    }
    $tmp = "$PathYaml.tmp"; $lines -join "`n" | Out-File -Encoding UTF8 $tmp; Move-Item -Force -LiteralPath $tmp -Destination $PathYaml
}
function Ensure-EnvTemplate { param([string]$EnvPath)
    if (Test-Path -LiteralPath $EnvPath) { return }
    @(
        "# Generated by Discover-CliTool",
        "# Copy to .env and adjust as needed",
        "CLI_ORCHESTRATOR_OPTS="
    ) | Out-File -Encoding UTF8 "$EnvPath.example"
}

function Get-VersionString { param([string]$ExePath, [string]$ToolName)
    $VersionArgsMap = @{
        "Aider" = @("--version"); "Continue CLI" = @("--version","version"); "OpenCode CLI" = @("--version","version","-v");
        "Claude Code CLI" = @("--version","version"); "Gemini CLI" = @("--version","version","-v"); "GitHub Copilot CLI" = @("--version","version");
        "Open Codex CLI" = @("--version","version","-v"); "Ollama" = @("version","--version"); "Git" = @("--version"); "GitHub CLI" = @("--version","version");
        "Node.js" = @("--version"); "npm" = @("--version","-v"); "Python" = @("--version","-V"); "pipx" = @("--version") }
    $args = $VersionArgsMap[$ToolName]; if (-not $args) { $args = @("--version","-v","version") }
    try {
        foreach ($a in $args) {
            $pinfo = [System.Diagnostics.ProcessStartInfo]::new(); $pinfo.FileName = $ExePath; $pinfo.Arguments = $a; $pinfo.RedirectStandardOutput = $true; $pinfo.RedirectStandardError = $true; $pinfo.UseShellExecute = $false; $pinfo.CreateNoWindow = $true
            $p = [System.Diagnostics.Process]::new(); $p.StartInfo = $pinfo
            if ($p.Start()) { $null = $p.WaitForExit(3000); $out = $p.StandardOutput.ReadToEnd().Trim(); $err = $p.StandardError.ReadToEnd().Trim(); if ($p.ExitCode -eq 0 -and $out) { return $out }; if ($err) { return $err } }
        }
    } catch { }
    return $null
}

function Invoke-DiscoverCliTool {
    [CmdletBinding()]
    param(
        [string[]]$Roots = @("C:\\Users\\Richard Wilks", "C:\\Users\\Richard Wilks\\Downloads"),
        [object[]]$Tools = @(
            @{ Name = "Aider"; Key="aider"; Commands = @("aider.exe","aider") },
            @{ Name = "Continue CLI"; Key="continue"; Commands = @("cn.exe","cn") },
            @{ Name = "OpenCode CLI"; Key="opencode"; Commands = @("opencode.exe","opencode.cmd","opencode") },
            @{ Name = "Claude Code CLI"; Key="claude"; Commands = @("claude.exe","claude","claude-code.exe","claude-code") },
            @{ Name = "Gemini CLI"; Key="gemini"; Commands = @("gemini.exe","gemini","gemini-cli.exe","gemini-cli") },
            @{ Name = "GitHub Copilot CLI"; Key="github-copilot"; Commands = @("github-copilot.exe","gh-copilot.exe","copilot.exe","github-copilot","gh-copilot","copilot") },
            @{ Name = "Open Codex CLI"; Key="opencodex"; Commands = @("opencodex.exe","opencodex","codex.exe","codex") },
            @{ Name = "Ollama"; Key="ollama"; Commands = @("ollama.exe","ollama") },
            @{ Name = "Git"; Key="git"; Commands = @("git.exe","git") },
            @{ Name = "GitHub CLI"; Key="gh"; Commands = @("gh.exe","gh") },
            @{ Name = "Node.js"; Key="node"; Commands = @("node.exe","node") },
            @{ Name = "npm"; Key="npm"; Commands = @("npm.cmd","npm") },
            @{ Name = "Python"; Key="python"; Commands = @("python.exe","py.exe","python","py") },
            @{ Name = "pipx"; Key="pipx"; Commands = @("pipx.exe","pipx") }
        ),
        [string]$OutDir = (Join-Path (Get-Location) 'local\\cli_discovery'),
        [string]$ProjectRoot = (Get-Location).Path,
        [switch]$Execute,
        [switch]$DiscoveryOnly,
        [string]$LedgerPath
    )

    $IsDryRun = $true
    if ($Execute.IsPresent -and -not $DiscoveryOnly.IsPresent) { $IsDryRun = $false }
    Write-Log -Level 'Info' -Message "Starting CLI tool discovery (dry_run=$IsDryRun)"

    try {
        if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
        $configDir = Join-Path $ProjectRoot "config"
        if (-not (Test-Path -LiteralPath $configDir)) { New-Item -ItemType Directory -Path $configDir -Force | Out-Null }

        $results = [System.Collections.Generic.List[pscustomobject]]::new()
        foreach ($tool in ($Tools | Sort-Object Name)) {
            $name = $tool.Name
            $key = $tool.Key
            $cmds = [string[]]$tool.Commands
            $pathHit = Resolve-InPath -CommandNames $cmds
            if ($name -eq "GitHub Copilot CLI" -and -not $pathHit) {
                if (Test-GHCopilotExtension) { $ghCmd = Get-Command gh -ErrorAction SilentlyContinue; if ($ghCmd) { $pathHit = $ghCmd.Source } }
            }
            $hintHits = Search-InHintPaths -CommandNames $cmds
            $rootHits = @()
            if (@($hintHits).Count -gt 0) { $rootHits += $hintHits }
            $rootHits += Search-InRoots -Roots $Roots -CommandNames $cmds
            $rootHits = @($rootHits | Select-Object -Unique | Sort-Object)

            $primary = if ($pathHit) { $pathHit } elseif (@($rootHits).Count -gt 0) { $rootHits[0] } else { $null }
            $version = $null
            if ($primary) { $version = Get-VersionString -ExePath $primary -ToolName $name }

            $results.Add([pscustomobject]@{
                ToolName = $name
                Key = $key
                CommandNames = ($cmds -join ", ")
                FoundInPATH = [bool]$pathHit
                PATHLocation = $pathHit
                FoundInHints = [bool](@($hintHits).Count -gt 0)
                FoundInRoots = [bool](@($rootHits).Count -gt 0)
                RootMatches = $rootHits -join " | "
                PreferredPath = $primary
                VersionInfo = $version
                Timestamp = (Get-Date).ToString("s")
            })
        }

        $jsonPath = Join-Path $OutDir "cli_tools_inventory.json"
        $csvPath = Join-Path $OutDir "cli_tools_inventory.csv"
        if (-not $IsDryRun) {
            $tmpJson = "$jsonPath.tmp"; $tmpCsv = "$csvPath.tmp"
            $results | ConvertTo-Json -Depth 5 | Out-File -Encoding UTF8 $tmpJson
            $results | Export-Csv -NoTypeInformation -Encoding UTF8 $tmpCsv
            Move-Item -Force -LiteralPath $tmpJson -Destination $jsonPath
            Move-Item -Force -LiteralPath $tmpCsv -Destination $csvPath
            Write-Log -Level 'Info' -Message "Inventory written to $jsonPath and $csvPath"
        }

        $results | Sort-Object ToolName | Select-Object ToolName, FoundInPATH, FoundInHints, FoundInRoots, PreferredPath, VersionInfo | Format-Table -AutoSize
        if (-not $DiscoveryOnly) {
            $pathsMap = @{}
            foreach ($r in $results) { if ($r.PreferredPath) { $pathsMap[$r.Key] = $r.PreferredPath } }
            $toolAdaptersPath = Join-Path $configDir "tool_adapters.yaml"
            if (-not $IsDryRun) { Write-ToolAdaptersYaml -PathYaml $toolAdaptersPath -PathsMap $pathsMap -CreateIfMissing }
            $discoveredPath = Join-Path $configDir "discovered_tools.yaml"
            if (-not $IsDryRun) { Write-DiscoveredYaml -PathYaml $discoveredPath -Results $results }
            $envPath = Join-Path $ProjectRoot ".env"; if (-not $IsDryRun) { Ensure-EnvTemplate -EnvPath $envPath }
        }
        Write-Log -Level 'Info' -Message 'Discover-CliTool module finished successfully.'
    }
    catch {
        Write-Log -Level 'Fatal' -Message "A critical error occurred during discovery: $($_.Exception.Message)"
    }
}

#endregion

#region --- Main Entry Point ---

function Show-MainMenu {
    while ($true) {
        Clear-Host
        Write-Host "=================================================" -ForegroundColor Green
        Write-Host "    Combined PowerShell Scripts Menu" -ForegroundColor Green
        Write-Host "================================================="
        Write-Host ""
        Write-Host "1. Run Complete Removal Script"
        Write-Host "2. Run Install Deterministic Git Script"
        Write-Host "3. Run Discover CLI Tools Script"
        Write-Host "Q. Quit"
        Write-Host ""
        $choice = Read-Host "Enter your choice"
        switch ($choice) { '1' { Invoke-CompleteRemoval; break } '2' { Invoke-InstallDeterministicGit; break } '3' { Invoke-DiscoverCliTool; break } 'q' { Write-Host "Exiting."; return } default { Write-Host "Invalid choice. Please try again." -ForegroundColor Red; Start-Sleep -Seconds 2 } }
    }
}

$script:CorrelationId = [guid]::NewGuid().ToString().Substring(0, 8)
Test-ScriptEnvironment

if ($RunCompleteRemoval) {
    $p = @{}; foreach ($k in @('RepoPath','SkipConfirmation')) { if ($PSBoundParameters.ContainsKey($k)) { $p[$k] = $PSBoundParameters[$k] } }
    Invoke-CompleteRemoval @p
}
elseif ($RunInstallDeterministicGit) {
    $p = @{}; foreach ($k in @('Force')) { if ($PSBoundParameters.ContainsKey($k)) { $p[$k] = $PSBoundParameters[$k] } }
    Invoke-InstallDeterministicGit @p
}
elseif ($RunDiscoverCliTools) {
    $p = @{}; foreach ($k in @('Roots','Tools','OutDir','ProjectRoot','Execute','DiscoveryOnly','LedgerPath')) { if ($PSBoundParameters.ContainsKey($k)) { $p[$k] = $PSBoundParameters[$k] } }
    Invoke-DiscoverCliTool @p
}
else { Show-MainMenu }

Write-Log -Level 'Info' -Message 'Script execution finished.'

#endregion

