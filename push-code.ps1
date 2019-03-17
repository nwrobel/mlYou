$VerbosePreference = 'Continue'
$ErrorActionPreference = 'Stop'

$pycFiles = Get-ChildItem -Filter "*.pyc" -File -Recurse
$pycFiles | Remove-Item -Force

Write-Host "The following cache files were deleted:"
$pycFiles | Select-Object -ExpandProperty FullName

$commitMsg = Read-Host -Prompt "Enter commit message"

git add --all
git commit -m $commitMsg
git push origin


Write-Host "Cleared cache and pushed changes successfully!" -ForegroundColor Green
