'''
mlu.common.settings

Module containing the definition for setting values for MLU (project-wide constants).
'''

import mlu.common.file

class MLUSettings:
    projectRoot = mlu.common.file.getMLUProjectRoot()
    logDir = mlu.common.file.JoinPaths(projectRoot, '~logs')
    cacheDir = mlu.common.file.JoinPaths(projectRoot, '~cache')
    
    musicLibraryRootDir = "Z:\\Music Library\\Content"
    votePlaylistsDir = mlu.common.file.JoinPaths(cacheDir, 'vote-playlists-converted-tmp')
    votePlaylistsArchiveDir = mlu.common.file.JoinPaths(cacheDir, 'vote-playlists-archive')
    mpdLogsDir = "D:\\Temp\\mlu-test\\test-mpd-logs"
    mpdLogsArchiveDir = mlu.common.file.JoinPaths(cacheDir, 'mpd-logs-archive')
    tagBackupsDir = mlu.common.file.JoinPaths(cacheDir, 'audio-tag-backups')
    testDataDir = ''

    # Create empty directories if any of the ones defined above don't exist
    if (not mlu.common.file.directoryExists(logDir)):
        mlu.common.file.createDirectory(logDir)

    if (not mlu.common.file.directoryExists(cacheDir)):
        mlu.common.file.createDirectory(cacheDir)

    if (not mlu.common.file.directoryExists(votePlaylistsArchiveDir)):
        mlu.common.file.createDirectory(votePlaylistsArchiveDir)

    if (not mlu.common.file.directoryExists(mpdLogsArchiveDir)):
        mlu.common.file.createDirectory(mpdLogsArchiveDir)

    if (not mlu.common.file.directoryExists(tagBackupsDir)):
        mlu.common.file.createDirectory(tagBackupsDir)