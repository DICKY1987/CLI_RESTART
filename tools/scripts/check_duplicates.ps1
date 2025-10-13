param(
  [string]$Root = "tools"
)

Write-Host "Scanning for duplicate files under '$Root'..." -ForegroundColor Cyan

$files = Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue
$entries = foreach ($f in $files) { 
  $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $f.FullName).Hash
  [PSCustomObject]@{ Name=$f.Name; Path=$f.FullName; Hash=$h }
}

$dupeContent = $entries | Group-Object Hash | Where-Object { $_.Count -gt 1 }
$dupeNames = $entries | Group-Object Name | Where-Object { $_.Count -gt 1 }

if ($dupeContent) {
  Write-Host "Duplicate content detected:" -ForegroundColor Yellow
  foreach ($g in $dupeContent) {
    Write-Host (" - HASH={0} COUNT={1}" -f $g.Name, $g.Count)
    $g.Group | ForEach-Object { Write-Host ("    " + $_.Path) }
  }
} else {
  Write-Host "No duplicate content found." -ForegroundColor Green
}

if ($dupeNames) {
  Write-Host "\nFiles sharing the same name:" -ForegroundColor Yellow
  foreach ($g in $dupeNames) {
    $distinct = ($g.Group | Select-Object -ExpandProperty Hash | Sort-Object -Unique).Count
    if ($distinct -gt 1) {
      Write-Host (" - NAME='{0}' INSTANCES={1} DISTINCT={2}" -f $g.Name, $g.Count, $distinct)
      $g.Group | ForEach-Object { Write-Host ("    " + $_.Path) }
    }
  }
} else {
  Write-Host "No same-named files across different paths." -ForegroundColor Green
}

Write-Host "\nDone." -ForegroundColor Cyan

