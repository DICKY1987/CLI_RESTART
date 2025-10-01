<#
 .SYNOPSIS
   Background health monitor that writes periodic health status to health.json.

 .DESCRIPTION
   Monitors system health and writes status updates to a JSON file at regular intervals.
   Tracks:
   - Process health
   - Disk space
   - Memory usage
   - Timestamp of last check

 .PARAMETER OutputPath
   Path where health.json will be written (default: ./health.json).

 .PARAMETER IntervalSeconds
   Interval between health checks in seconds (default: 30).

 .PARAMETER MaxChecks
   Maximum number of health checks to perform. If 0, runs indefinitely (default: 0).

 .EXAMPLE
   .\health-monitor.ps1 -OutputPath .sessions/current/health.json -IntervalSeconds 10 -MaxChecks 6
#>

param(
  [string]$OutputPath = (Join-Path $PSScriptRoot '../health.json'),
  [int]$IntervalSeconds = 30,
  [int]$MaxChecks = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'  # Continue on errors to keep monitoring

function Get-HealthStatus {
  $status = @{
    timestamp = (Get-Date).ToString('o')
    healthy = $true
    checks = @{}
  }

  # Check disk space
  try {
    $drive = Get-PSDrive -Name C -PSProvider FileSystem -ErrorAction Stop
    $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
    $usedSpaceGB = [math]::Round($drive.Used / 1GB, 2)
    $totalSpaceGB = [math]::Round(($drive.Free + $drive.Used) / 1GB, 2)
    $freePercent = [math]::Round(($freeSpaceGB / $totalSpaceGB) * 100, 2)

    $status.checks['disk'] = @{
      status = if ($freePercent -lt 10) { 'warning' } else { 'ok' }
      freeGB = $freeSpaceGB
      usedGB = $usedSpaceGB
      totalGB = $totalSpaceGB
      freePercent = $freePercent
    }

    if ($freePercent -lt 10) {
      $status.healthy = $false
    }
  }
  catch {
    $status.checks['disk'] = @{
      status = 'error'
      error = $_.Exception.Message
    }
    $status.healthy = $false
  }

  # Check memory
  try {
    if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) {
      $os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
      $totalMemoryGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
      $freeMemoryGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
      $usedMemoryGB = $totalMemoryGB - $freeMemoryGB
      $usedPercent = [math]::Round(($usedMemoryGB / $totalMemoryGB) * 100, 2)

      $status.checks['memory'] = @{
        status = if ($usedPercent -gt 90) { 'warning' } else { 'ok' }
        totalGB = $totalMemoryGB
        usedGB = $usedMemoryGB
        freeGB = $freeMemoryGB
        usedPercent = $usedPercent
      }

      if ($usedPercent -gt 90) {
        $status.healthy = $false
      }
    }
    else {
      $status.checks['memory'] = @{
        status = 'skipped'
        reason = 'Not available on this platform'
      }
    }
  }
  catch {
    $status.checks['memory'] = @{
      status = 'error'
      error = $_.Exception.Message
    }
  }

  # Check process count
  try {
    $processCount = (Get-Process).Count
    $status.checks['processes'] = @{
      status = 'ok'
      count = $processCount
    }
  }
  catch {
    $status.checks['processes'] = @{
      status = 'error'
      error = $_.Exception.Message
    }
  }

  return $status
}

function Write-HealthStatus {
  param(
    [string]$Path,
    [hashtable]$Status
  )

  try {
    $json = $Status | ConvertTo-Json -Depth 10
    $json | Out-File -FilePath $Path -Encoding UTF8 -Force
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Health status written to: $Path" -ForegroundColor Green
  }
  catch {
    Write-Warning "Failed to write health status: $($_.Exception.Message)"
  }
}

# Main monitoring loop
Write-Host "Starting health monitor..." -ForegroundColor Cyan
Write-Host "  Output: $OutputPath" -ForegroundColor Cyan
Write-Host "  Interval: ${IntervalSeconds}s" -ForegroundColor Cyan
Write-Host "  Max checks: $(if ($MaxChecks -eq 0) { 'unlimited' } else { $MaxChecks })" -ForegroundColor Cyan

$checkCount = 0

while ($true) {
  $checkCount++

  # Perform health check
  $health = Get-HealthStatus
  Write-HealthStatus -Path $OutputPath -Status $health

  if (-not $health.healthy) {
    Write-Warning "Health check failed at $(Get-Date)"
  }

  # Check if we've reached max checks
  if ($MaxChecks -gt 0 -and $checkCount -ge $MaxChecks) {
    Write-Host "Reached maximum checks ($MaxChecks). Exiting." -ForegroundColor Yellow
    break
  }

  # Wait for next interval
  Start-Sleep -Seconds $IntervalSeconds
}

Write-Host "Health monitor stopped." -ForegroundColor Yellow
