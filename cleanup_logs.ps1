# Cleanup installation logs and other temporary files

$parentDir = "C:\Users\Richard Wilks"

Write-Host "Cleaning up installation logs..." -ForegroundColor Yellow

# Remove old installation logs
$logFiles = Get-ChildItem "$parentDir\installation-*.log" -ErrorAction SilentlyContinue

if ($logFiles) {
    Write-Host "Found $($logFiles.Count) installation log files"
    $logFiles | Remove-Item -Force
    Write-Host "Removed $($logFiles.Count) log files" -ForegroundColor Green
} else {
    Write-Host "No installation log files found" -ForegroundColor Green
}

# Remove installation reports
$reportFiles = Get-ChildItem "$parentDir\installation-report-*.md" -ErrorAction SilentlyContinue
if ($reportFiles) {
    Write-Host "Found $($reportFiles.Count) installation report files"
    $reportFiles | Remove-Item -Force
    Write-Host "Removed $($reportFiles.Count) report files" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
