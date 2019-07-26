$VerbosePreference = 'Continue'
$ErrorActionPreference = 'Stop'

$pyCacheDirs = Get-ChildItem -Filter "__pycache__" -Directory -Recurse
$pyCacheDirs | Remove-Item -Force -Recurse -Confirm:$false

$pycFiles = Get-ChildItem -Filter "*.pyc" -File -Recurse
$pycFiles | Remove-Item -Force

Write-Host "The following cache files/folders were deleted:"
$pycFiles | Select-Object -ExpandProperty FullName
$pyCacheDirs | Select-Object -ExpandProperty FullName

$commitMsg = Read-Host -Prompt "Enter commit message"

git add --all
git commit -m $commitMsg
git push origin


Write-Host "Cleared cache and pushed changes successfully!" -ForegroundColor Green
