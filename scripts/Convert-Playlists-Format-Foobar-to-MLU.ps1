$ErrorActionPreference = 'Stop'

$playlistsHomeDir = 'Z:\Music Library\Playlists\'
$mpdPlaylistsDir = 'Z:\Music Library\Content\!mpd-published-playlists\'
$mpdDataRoot = '/datastore/nick/'
$windowsDataRoot = 'Z:\'

$confirm = Read-Host -Prompt "Warning: this script will remove any pre-existing playlists in the MPD playlist dir '$mpdPlaylistsDir' to repalce them with the playlists in the home playlist dir. Are you sure you want to continue? [y/n]"
if ($confirm -ne 'y') {
    throw 'Script operation stopped by user: no permission to remove playlists from MPD playlists dir'
} 

Get-ChildItem -Path $mpdPlaylistsDir -Recurse | Remove-Item -Recurse -Force
Copy-Item -Path "$playlistsHomeDir*" -Destination $mpdPlaylistsDir -Recurse -Container
$copiedPlaylistFiles = Get-ChildItem -Path $mpdPlaylistsDir -Filter '*.m3u*' -Recurse
$numPlaylists = @($copiedPlaylistFiles).Count 

foreach ($playlist in $copiedPlaylistFiles) {
    
    $newPlaylistLines = New-Object System.Collections.ArrayList
    $playlistFullPath = $playlist.FullName
    
    Get-Content -Path $playlistFullPath | ForEach-Object {
        $fixedLine = $_.Replace($windowsDataRoot, $mpdDataRoot)
        $fixedLine = $fixedLine.Replace('\', '/')
        $newPlaylistLines.Add($fixedLine) > $null
    }

    if ($newPlaylistLines[0] -eq '#') {
        $newPlaylistLines.RemoveAt(0)
    }

    $newPlaylistLines | Out-File -FilePath $playlistFullPath -Encoding utf8
    Write-Host "Playlist converted to MLU format successfully, location: $playlistFullPath" -ForegroundColor Cyan
}

Write-Host "$numPlaylists playlist files converted and saved successfully!" -ForegroundColor Green