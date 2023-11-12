# To schedule with task scheduler, run powershell as program with args:
# -WindowStyle minimized -File "C:\nick-local-data\local-dev-my\mlu\automation\Update-RatingFromVotePlaylists.ps1"

$ConfigFilename = "mlu.config.json"

function Main {
    $projectDir = (Get-Item -Path $PSScriptRoot).Parent.FullName
    $configFilepath = Join-Path $projectDir -ChildPath $ConfigFilename
    $configs = Get-Configs -ConfigFile $configFilepath

    Write-Host "Deleting existing files from convert playlist input dir"
    Get-ChildItem $configs.convertPlaylistsInputDir | Remove-Item -Verbose

    Write-Host "Copying existing vote playlists into convert playlist input dir"
    $votePlaylistsSrc = Get-VotePlaylistFiles -VotePlaylistDir $configs.playlistsDir -ConfigFile $configFilepath
    $votePlaylistsSrc | Copy-Item -Destination $configs.convertPlaylistsInputDir

    ConvertPlaylists

    Write-Host "Copying converted vote playlists into rating processing dir"
    Get-ChildItem $configs.convertPlaylistsOutputDir | Copy-Item -Destination $configs.votePlaylistConfig.votePlaylistInputDir

    ProcessVotePlaylists

    Write-Host "Copying (overwrite) reset vote playlists into real dir"
    Get-ChildItem $configs.votePlaylistConfig.votePlaylistInputDir | Copy-Item -Destination $configs.playlistsDir -Verbose -Force

    Write-Host "Cleaning files"
    Get-ChildItem $configs.convertPlaylistsInputDir | Remove-Item -Verbose
    Get-ChildItem $configs.convertPlaylistsOutputDir | Remove-Item -Verbose
    Get-ChildItem $configs.votePlaylistConfig.votePlaylistInputDir | Remove-Item -Verbose

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
    $activateFilepath = Join-Path $projectDir -ChildPath 'py-venv-windows\Scripts\activate.ps1'
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
    $activateFilepath = Join-Path $projectDir -ChildPath 'py-venv-windows\Scripts\activate.ps1'
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



