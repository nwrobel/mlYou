$ConfigFilename = "mlu.TEST.config.json"

function Main {
    $votePlaylistRealDir = "Z:\Music Library\!mpd-saved-playlists"

    $projectDir = (Get-Item -Path $PSScriptRoot).Parent.FullName
    $configFilepath = Join-Path $projectDir -ChildPath $ConfigFilename
    $configs = Get-Configs -ConfigFile $configFilepath

    Write-Host "Deleting existing files from convert playlist input dir"
    Get-ChildItem $configs.convertPlaylistsInputDir | Remove-Item -Verbose -Confirm

    Write-Host "Copying existing vote playlists into convert playlist input dir"
    $votePlaylistsSrc = Get-VotePlaylistFiles -VotePlaylistDir $votePlaylistRealDir -ConfigFile $configFilepath
    $votePlaylistsSrc | Copy-Item -Destination $configs.convertPlaylistsInputDir

    ConvertPlaylists

    Write-Host "Copying converted vote playlists into rating processing dir"
    Get-ChildItem $configs.convertPlaylistsOutputDir | Copy-Item -Destination $configs.votePlaylistConfig.votePlaylistInputDir

    ProcessVotePlaylists

    Write-Host "Copying (overwrite) reset vote playlists into real dir"
    Get-ChildItem $configs.votePlaylistConfig.votePlaylistInputDir | Copy-Item -Destination $votePlaylistRealDir -Verbose -Confirm -Force

    Write-Host "Cleaning files"
    Get-ChildItem $configs.convertPlaylistsInputDir | Remove-Item -Verbose -Confirm
    Get-ChildItem $configs.convertPlaylistsOutputDir | Remove-Item -Verbose -Confirm
    Get-ChildItem $configs.votePlaylistConfig.votePlaylistInputDir | Remove-Item -Verbose -Confirm

}

function ConvertPlaylists {
    $args = [PSCustomObject]@{
        OldRoot = '/datastore/nick/'
        NewRoot = 'Z:\'
        FileExtension = 'm3u'
        ConfigFile = $ConfigFilename
    }

    # Locate the convert-playlists.py script from here in this directory
    $projectDir = (Get-Item -Path $PSScriptRoot).Parent.FullName
    $activateFilepath = Join-Path $projectDir -ChildPath 'py-venv-windows\Scripts\activate'
    $scriptPath = Join-Path -Path $projectDir -ChildPath 'scripts\change-playlist-items-root-path.py'

    # start the virtualenv
    & $activateFilepath

    # Run the script with our arguments using python
    python $scriptPath $args.OldRoot $args.NewRoot '--extension' $args.FileExtension '--config-file' $args.ConfigFile
}

function ProcessVotePlaylists {
    $args = [PSCustomObject]@{
        ConfigFile = $ConfigFilename
    }

    # Locate the convert-playlists.py script from here in this directory
    $projectDir = (Get-Item -Path $PSScriptRoot).Parent.FullName
    $activateFilepath = Join-Path $projectDir -ChildPath 'py-venv-windows\Scripts\activate'
    $scriptPath = Join-Path -Path $projectDir -ChildPath 'scripts\update-ratestat-tags-from-vote-playlists.py'

    # start the virtualenv
    & $activateFilepath

    # Run the script with our arguments using python
    python $scriptPath '--config-file' $args.ConfigFile
}

function Get-VotePlaylistFiles {
    param (
        $VotePlaylistDir,
        $ConfigFile
    )

    $filesList = @()
    $config = Get-Content $ConfigFile | Out-String | ConvertFrom-Json
    $voteFilesConfig = $config.votePlaylistConfig.votePlaylistFiles

    foreach ($voteFileConfig in $voteFilesConfig) {
        $filesList += Join-Path $VotePlaylistDir -ChildPath $voteFileConfig.filename
    }

    return $filesList
}

function Get-Configs {
    param($ConfigFile)

    $config = Get-Content $ConfigFile | Out-String | ConvertFrom-Json

    return $config
}

Main



