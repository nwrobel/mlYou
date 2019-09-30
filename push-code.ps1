$VerbosePreference = 'Continue'
$ErrorActionPreference = 'Stop'

$pyCacheDirs = Get-ChildItem -Filter "__pycache__" -Directory -Recurse
$pyCacheDirs | Remove-Item -Force -Recurse -Confirm:$false

$pyCacheFiles = Get-ChildItem -Filter "*.pyc" -File -Recurse
$pyCacheFiles | Remove-Item -Force

if ($pyCacheDirs -or $pyCacheFiles) {
    Write-Host "The following Python cache files/folders were deleted (pre-commit cleanup procedure):"
    $pycFiles | Select-Object -ExpandProperty FullName
    $pyCacheDirs | Select-Object -ExpandProperty FullName
}

$commitMsg = Read-Host -Prompt "`nEnter commit message"

git add --all
git commit -m $commitMsg
git push origin

Write-Host "Commit pushed successfully!" -ForegroundColor Green

