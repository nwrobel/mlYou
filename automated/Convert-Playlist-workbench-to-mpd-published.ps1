# These variables here represent the arguments to be passed to the convert-playlist.py script.
# Modify them to suit your automation needs.
$args = [PSCustomObject]@{
    SourcePlaylistDir = "Z:\Music Library\Playlist Workbench\Playlists-2020-08-18"
    OutputPlaylistDir = "Z:\Music Library\Content\!mpd-published-playlists\Playlists-2020-08-18"
    OldRoot = 'Z:\'
    NewRoot = '/datastore/nick/'
}

# Locate the convert-playlists.py script from here in this directory
$projectDir = (Get-Item -Path $PSScriptRoot).Parent.FullName
$scriptPath = Join-Path -Path $projectDir -ChildPath 'scripts\convert-playlist.py'

# Run the script with our arguments using python
python $scriptPath $args.SourcePlaylistDir $args.OutputPlaylistDir $args.OldRoot $args.NewRoot

