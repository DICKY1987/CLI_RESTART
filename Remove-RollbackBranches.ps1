# File: Remove-RollbackBranches.ps1
#Requires -Version 5.1
Set-StrictMode -Version Latest

<#
.SYNOPSIS
Removes all local and remote Git branches matching a prefix (default: "rollback/").

.DESCRIPTION
Safely deletes local branches and remote branches on a remote (default: 'origin')
that start with a given prefix. Honors -WhatIf/-Confirm. Offers exclusions,
protection of current branch, and soft vs force delete.

.PARAMETER RepositoryPath
Path to the local Git repository.

.PARAMETER Prefix
Branch name prefix to target (e.g., "rollback/"). Case-sensitive by Git convention.

.PARAMETER RemoteName
Remote to operate on for remote branch deletion. Default: origin.

.PARAMETER Exclude
One or more branch-name wildcard patterns to exclude (e.g., "rollback/safe-*").

.PARAMETER Force
Use force delete (-D). Without -Force uses safe delete (-d) which fails if not merged.

.PARAMETER ProtectCurrent
Prevent deleting the currently checked-out branch if it matches. Default: true.

.PARAMETER LocalOnly
Only delete local branches; skip remote operations.

.PARAMETER RemoteOnly
Only delete remote branches; skip local operations.

.PARAMETER NoVerify
Pass --no-verify to git push when deleting remote branches (skip hooks).

.PARAMETER ProtectBranches
Additional branch wildcard patterns to always protect (e.g., 'main','master','release/*').

.PARAMETER PassThru
Return a summary object containing deleted/failed branches and correlation id.

.PARAMETER BatchLocal
Attempt batch local deletion (faster). Falls back to per-branch on failure.

.PARAMETER Verify
After deletion, verify no matching branches remain; fail if any found.

.EXAMPLE
.\Remove-RollbackBranches.ps1 -RepositoryPath "C:\repo" -WhatIf

.EXAMPLE
.\Remove-RollbackBranches.ps1 -RepositoryPath "C:\repo" -Verbose -Force

.NOTES
Requires Git CLI on PATH.
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$RepositoryPath,

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$Prefix = 'rollback/',

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$RemoteName = 'origin',

    [Parameter()]
    [string[]]$Exclude = @(),

    [Parameter()]
    [switch]$Force,

    [Parameter()]
    [switch]$ProtectCurrent = $true,

    [Parameter()]
    [switch]$LocalOnly,

    [Parameter()]
    [switch]$RemoteOnly,

    [Parameter()]
    [switch]$NoVerify,

    [Parameter()]
    [string[]]$ProtectBranches = @(),

    [Parameter()]
    [switch]$PassThru,

    [Parameter()]
    [switch]$BatchLocal,

    [Parameter()]
    [switch]$Verify
)

# --- Helpers ---

function Assert-GitAvailable {
    [CmdletBinding()]
    param()
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git executable not found on PATH."
    }
}

function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter()][ValidateSet('Debug','Info','Warning','Error','Critical','Audit','Security')]
        [string]$Level = 'Info',
        [Parameter()][string]$Message,
        [Parameter()][hashtable]$Data = @{},
        [Parameter()][string]$CorrelationId
    )
    $ws = Get-Command -Name Write-StructuredLog -ErrorAction SilentlyContinue
    if ($ws) {
        Write-StructuredLog -Level $Level -Message $Message -Data $Data -CorrelationId $CorrelationId -Category 'Application' -Source 'Remove-RollbackBranches'
    } else {
        # Fallback: minimal console output
        switch ($Level) {
            'Error'   { Write-Error $Message }
            'Warning' { Write-Warning $Message }
            default   { Write-Verbose $Message }
        }
    }
}

function Assert-Repository {
    [CmdletBinding()]
    param([string]$Path)

    if (-not (Test-Path -Path $Path -PathType Container)) {
        throw "Repository path not found: $Path"
    }
    $gitMeta = Join-Path $Path '.git'
    if (-not (Test-Path -Path $gitMeta)) {
        throw "No .git entry found in: $Path"
    }
    # Support both directory and file (worktrees/submodules use file pointing to gitdir)
    if (-not (Test-Path -Path $gitMeta -PathType Container)) {
        # .git is a file; validate it points to a real gitdir
        try {
            $content = Get-Content -LiteralPath $gitMeta -TotalCount 1 -ErrorAction Stop
            if ($content -notmatch '^gitdir:\s*(.+)$') {
                throw "Invalid .git file format"
            }
            $gitDir = $Matches[1].Trim()
            $resolved = if ([System.IO.Path]::IsPathRooted($gitDir)) { $gitDir } else { Join-Path $Path $gitDir }
            if (-not (Test-Path -Path $resolved -PathType Container)) {
                throw "Resolved gitdir not found: $resolved"
            }
        } catch {
            throw "Invalid .git metadata in: $Path. $($_.Exception.Message)"
        }
    }
}

function Invoke-Git {
    <#
      Why: Centralized git invocation with consistent error/WhatIf handling.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$Args,
        [switch]$Destructive,
        [string]$Target = ""
    )

    $cmd = "git $($Args -join ' ')"
    Write-Verbose "Executing: $cmd"

    if ($Destructive) {
        $action = "Execute Git command"
        $targetLabel = if ($Target) { $Target } else { $cmd }
        if (-not $PSCmdlet.ShouldProcess($targetLabel, $action)) { return $null }
    }

    $output = & git @Args 2>&1
    if ($LASTEXITCODE -ne 0) {
        $errorMessage = "Git command failed: $cmd`nOutput:`n$output"
        Write-Error $errorMessage
        throw $errorMessage
    }
    return $output
}

function Get-CurrentBranch {
    [CmdletBinding()]
    param()
    try {
        $name = (Invoke-Git -Args @('rev-parse', '--abbrev-ref', 'HEAD')).Trim()
        return $name
    } catch {
        return $null
    }
}

function Filter-Excluded {
    [CmdletBinding()]
    param(
        [string[]]$Branches,
        [string[]]$ExcludePatterns
    )
    if (-not $ExcludePatterns -or $Branches.Count -eq 0) { return ,$Branches }

    $filtered = New-Object System.Collections.Generic.List[string]
    foreach ($b in $Branches) {
        $skip = $false
        foreach ($pat in $ExcludePatterns) {
            if ($b -like $pat) { $skip = $true; break }
        }
        if (-not $skip) { [void]$filtered.Add($b) }
    }
    return ,$filtered.ToArray()
}

function Get-LocalBranchesByPrefix {
    [CmdletBinding()]
    param([string]$Prefix)

    # Use --list to avoid formatting; still strips leading '* ' on current branch.
    $raw = Invoke-Git -Args @('branch', '--list', "$Prefix*")
    if (-not $raw) { return @() }

    $clean = $raw |
        ForEach-Object { $_.Trim() -replace '^\* ', '' } |
        Where-Object { $_ -ne '' } |
        Sort-Object -Unique

    return ,$clean
}

function Get-RemoteBranchesByPrefix {
    [CmdletBinding()]
    param(
        [string]$Remote,
        [string]$Prefix
    )
    # Use ls-remote --heads to get authoritative ref list, avoid parsing `git branch -r`
    $raw = Invoke-Git -Args @('ls-remote', '--heads', $Remote, "$Prefix*")
    if (-not $raw) { return @() }

    $names = @()
    foreach ($line in $raw) {
        # format: <sha>\trefs/heads/<branch>
        $parts = $line -split "`t"
        if ($parts.Count -ge 2) {
            $ref = $parts[1]
            if ($ref -like 'refs/heads/*') {
                $names += ($ref -replace '^refs/heads/', '')
            }
        }
    }
    $names | Sort-Object -Unique
}

function Get-RemoteTrackingBranchesByPrefix {
    [CmdletBinding()]
    param(
        [string]$Remote,
        [string]$Prefix
    )
    # Enumerate local remote-tracking refs after fetch --prune; avoids extra network roundtrips
    $pattern = "refs/remotes/$Remote/$Prefix*"
    $raw = Invoke-Git -Args @('for-each-ref', '--format=%(refname:short)', $pattern)
    if (-not $raw) { return @() }
    $names = @()
    foreach ($line in $raw) {
        # Convert origin/foo/bar -> foo/bar
        if ($line -like "$Remote/*") {
            $names += ($line -replace "^$([Regex]::Escape($Remote))/", '')
        }
    }
    $names | Sort-Object -Unique
}

# --- Main ---

$originalLocation = Get-Location
$correlationId = [Guid]::NewGuid().ToString()

try {
    if ($LocalOnly -and $RemoteOnly) { throw "-LocalOnly and -RemoteOnly cannot be used together." }
    Assert-GitAvailable
    Assert-Repository -Path $RepositoryPath

    Write-Verbose "Changing directory to '$RepositoryPath'."
    Set-Location -Path $RepositoryPath

    $current = Get-CurrentBranch
    Write-Host "--- Cleanup: '$RepositoryPath' (CorrId: $correlationId) ---" -ForegroundColor Yellow
    Write-Host "Target prefix: '$Prefix' | Remote: '$RemoteName' | Force: $Force | ProtectCurrent: $ProtectCurrent" -ForegroundColor DarkGray
    if ($LocalOnly) { Write-Host "Mode: LocalOnly" -ForegroundColor DarkGray }
    if ($RemoteOnly) { Write-Host "Mode: RemoteOnly" -ForegroundColor DarkGray }
    if ($NoVerify) { Write-Host "Remote push: --no-verify" -ForegroundColor DarkGray }
    if ($Exclude.Count) { Write-Host "Exclude: $($Exclude -join ', ')" -ForegroundColor DarkGray }
    if ($ProtectBranches.Count) { Write-Host "Protect: $($ProtectBranches -join ', ')" -ForegroundColor DarkGray }

    $summary = [ordered]@{
        CorrelationId = $correlationId
        DeletedLocal = @()
        FailedLocal = @()
        DeletedRemote = @()
        FailedRemote = @()
    }
    Write-Log -Level Info -Message 'Branch cleanup starting' -CorrelationId $correlationId -Data @{
        RepositoryPath = $RepositoryPath
        Prefix = $Prefix
        Remote = $RemoteName
        Force = $Force.IsPresent
        ProtectCurrent = $ProtectCurrent.IsPresent
        LocalOnly = $LocalOnly.IsPresent
        RemoteOnly = $RemoteOnly.IsPresent
        Exclude = $Exclude
        Protect = $ProtectBranches
    }

    # Local --------------------------------------------------------------------
    if (-not $RemoteOnly) {
        Write-Host "`nLocal branches matching '$Prefix*':" -ForegroundColor Cyan
        $local = Get-LocalBranchesByPrefix -Prefix $Prefix
        if ($ProtectCurrent -and $current) {
            $local = $local | Where-Object { $_ -ne $current }
        }
        # Apply general exclusions and protected patterns
        $local = Filter-Excluded -Branches $local -ExcludePatterns ($Exclude + $ProtectBranches)

        if ($local.Count -gt 0) {
            Write-Host "Found $($local.Count) local branch(es) to delete." -ForegroundColor DarkGray
            $deleteFlag = if ($Force) { '-D' } else { '-d' }
            $batched = $false
            if ($BatchLocal) {
                try {
                    $batched = $true
                    $args = @('branch', $deleteFlag) + $local
                    $target = "Delete $($local.Count) local branches in batch"
                    [void](Invoke-Git -Args $args -Destructive -Target $target)
                    foreach ($lb in $local) { $summary.DeletedLocal += $lb; Write-Host "  Deleted local: $lb" -ForegroundColor DarkGreen }
                } catch {
                    Write-Warning "Batch local delete failed; falling back to per-branch. $($_.Exception.Message)"
                    $batched = $false
                }
            }
            if (-not $batched) {
                foreach ($lb in $local) {
                    try {
                        $args = @('branch', $deleteFlag, $lb)
                        $target = "Delete local branch $lb"
                        [void](Invoke-Git -Args $args -Destructive -Target $target)
                        Write-Host "  Deleted local: $lb" -ForegroundColor DarkGreen
                        $summary.DeletedLocal += $lb
                    } catch {
                        $summary.FailedLocal += $lb
                        Write-Warning "Failed to delete local branch: $lb. $($_.Exception.Message)"
                    }
                }
            }
        } else {
            Write-Host "No local branches found." -ForegroundColor Green
            if ($ProtectCurrent -and $current -like "$Prefix*") {
                Write-Host "Note: Current branch '$current' is protected." -ForegroundColor DarkGray
            }
        }
    }

    # Remote -------------------------------------------------------------------
    if (-not $LocalOnly) {
        Write-Host "`nRemote branches on '$RemoteName' matching '$Prefix*':" -ForegroundColor Cyan

        # Verify remote exists
        try {
            $remoteCheck = Invoke-Git -Args @('remote', 'get-url', $RemoteName)
            Write-Verbose "Remote '$RemoteName' URL: $remoteCheck"
        } catch {
            Write-Warning "Remote '$RemoteName' not found. Skipping remote cleanup." 
            $LocalOnly = $true # to allow finalization and summary
        }

        if (-not $LocalOnly) {
            # Fetch and prune stale refs, honor -WhatIf/-Confirm
            Write-Verbose "Fetching and pruning stale remote refs..."
            [void](Invoke-Git -Args @('fetch', $RemoteName, '--prune') -Destructive -Target "Fetch --prune from $RemoteName")

            # After pruning, remote-tracking refs are authoritative; avoid extra network calls
            $remote = Get-RemoteTrackingBranchesByPrefix -Remote $RemoteName -Prefix $Prefix
            $remote = Filter-Excluded -Branches $remote -ExcludePatterns ($Exclude + $ProtectBranches)

            if ($remote.Count -gt 0) {
                Write-Host "Found $($remote.Count) remote branch(es) to delete from remote '$RemoteName'." -ForegroundColor DarkGray

                $deleted = 0
                $failed = @()

                # Try batched push --delete to reduce roundtrips
                $batchSucceeded = $false
                try {
                    $pushArgs = @('push', $RemoteName, '--delete') + $remote
                    if ($NoVerify) { $pushArgs += '--no-verify' }
                    [void](Invoke-Git -Args $pushArgs -Destructive -Target "Delete $($remote.Count) remote branches on '$RemoteName'")
                    foreach ($rb in $remote) {
                        $deleted += 1
                        $summary.DeletedRemote += $rb
                        Write-Host "  Deleted remote: $RemoteName/$rb" -ForegroundColor DarkGreen
                    }
                    $batchSucceeded = $true
                } catch {
                    Write-Warning "Batch remote delete failed; falling back to per-branch. $($_.Exception.Message)"
                }

                if (-not $batchSucceeded) {
                    foreach ($rb in $remote) {
                        $target = "$RemoteName/$rb"
                        try {
                            $pushArgs = @('push', $RemoteName, '--delete', $rb)
                            if ($NoVerify) { $pushArgs += '--no-verify' }
                            [void](Invoke-Git -Args $pushArgs -Destructive -Target "Delete remote branch $target")
                            $deleted += 1
                            $summary.DeletedRemote += $rb
                            Write-Host "  Deleted remote: $target" -ForegroundColor DarkGreen
                        } catch {
                            $failed += $rb
                            $summary.FailedRemote += $rb
                            Write-Warning "Failed to delete remote branch: $target. $($_.Exception.Message)"
                        }
                    }
                }

                Write-Host "`nRemote deletion summary: deleted=$deleted; failed=$($failed.Count)" -ForegroundColor Green
                if ($failed.Count -gt 0) {
                    Write-Host "Failed branches: $($failed -join ', ')" -ForegroundColor DarkYellow
                }
            } else {
                Write-Host "No remote branches found. All clean!" -ForegroundColor Green
            }

            # Final prune of remote tracking refs (honor -WhatIf)
            Write-Verbose "Final prune of remote tracking branches..."
            [void](Invoke-Git -Args @('remote', 'prune', $RemoteName) -Destructive -Target "Prune remote tracking '$RemoteName'")
        }
    }

    if ($Verify) {
        Write-Verbose "Verifying no matching branches remain..."
        $postLocal = @()
        $postRemote = @()
        if (-not $RemoteOnly) {
            $postLocal = Get-LocalBranchesByPrefix -Prefix $Prefix
            if ($ProtectCurrent -and $current) { $postLocal = $postLocal | Where-Object { $_ -ne $current } }
            $postLocal = Filter-Excluded -Branches $postLocal -ExcludePatterns ($Exclude + $ProtectBranches)
        }
        if (-not $LocalOnly) {
            [void](Invoke-Git -Args @('fetch', $RemoteName, '--prune') -Destructive -Target "Fetch --prune from $RemoteName (verify)")
            $postRemote = Get-RemoteTrackingBranchesByPrefix -Remote $RemoteName -Prefix $Prefix
            $postRemote = Filter-Excluded -Branches $postRemote -ExcludePatterns ($Exclude + $ProtectBranches)
        }
        if (($postLocal.Count + $postRemote.Count) -gt 0) {
            Write-Log -Level Error -Message 'Verification failed: branches remain' -CorrelationId $correlationId -Data @{
                RemainingLocal = $postLocal
                RemainingRemote = $postRemote
            }
            throw "Verification failed. Remaining local: $($postLocal -join ', '); remaining remote: $($postRemote -join ', ')"
        }
        Write-Verbose "Verification passed."
    }

    Write-Host "`n--- Cleanup Complete ---" -ForegroundColor Yellow
    Write-Log -Level Info -Message 'Branch cleanup complete' -CorrelationId $correlationId -Data @{
        DeletedLocal = $summary.DeletedLocal
        FailedLocal = $summary.FailedLocal
        DeletedRemote = $summary.DeletedRemote
        FailedRemote = $summary.FailedRemote
    }
    if ($PassThru) {
        # Emit a simple summary object suitable for programmatic use
        [PSCustomObject]$summary
    }

} catch {
    Write-Error "A terminating error occurred: $($_.Exception.Message)"
    Write-Log -Level Error -Message 'Branch cleanup failed' -CorrelationId $correlationId -Data @{
        Error = $_.Exception.Message
    }
    throw
} finally {
    Write-Verbose "Restoring original location to $($originalLocation.Path)"
    Set-Location -Path $originalLocation
}
