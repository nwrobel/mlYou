# These variables here represent the arguments to be passed to the convert-playlist.py script.
# Modify them to suit your automation needs.
$args = [PSCustomObject]@{
    SourcePlaylistDir = "C:\Users\user\nick-data\~Temp\convert-playlists-in"
    OutputPlaylistDir = "C:\Users\user\nick-data\~Temp\convert-playlists-out"
    OldRoot = 'C:\Users\user'
    NewRoot = '/datastore/nick/'
}

# Locate the convert-playlists.py script from here in this dir
$projectDir = (Get-Item -Path $PSScriptRoot).Parent.FullName
$scriptPath = Join-Path -Path $projectDir -ChildPath 'scripts\convert-playlist.py'

# Run the script with our arguments using python
python $scriptPath $args.SourcePlaylistDir $args.OutputPlaylistDir $args.OldRoot $args.NewRoot

