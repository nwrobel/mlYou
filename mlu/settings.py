'''
mlu.common.settings

Module containing the definition for setting values for MLU (project-wide constants).
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

def getProjectRootDir():
    thisScriptDir = mypycommons.file.getThisScriptCurrentDirectory()
    projectRootDir = mypycommons.file.JoinPaths(thisScriptDir, '..')
    return projectRootDir

class MLUSettings:
    projectRootDir = getProjectRootDir()
    logDir = mypycommons.file.JoinPaths(projectRootDir, '~logs')
    cacheDir = mypycommons.file.JoinPaths(projectRootDir, '~cache')
    
    # Root of where the library music files are found
    #musicLibraryRootDir = "Z:\\Music Library\\Content"
    musicLibraryRootDir = "/datastore/nick/Music Library/Content"

    # Dir of where the vote playlists can be found
    #votePlaylistsDir = "Z:\\Music Library\\!mpd-saved-playlists"
    votePlaylistsDir = "/datastore/nick/Music Library/!mpd-saved-playlists"

    # Filepath to the MPD log file
    mpdLogFilepath = "/var/log/mpd-master.log"


    # Dirs of where various types of cache files are stored
    tagBackupsDir = mypycommons.file.JoinPaths(cacheDir, 'audio-tag-backups')
    votePlaylistsTempDir = mypycommons.file.JoinPaths(cacheDir, 'vote-playlists-temp')
    votePlaylistsArchiveDir = mypycommons.file.JoinPaths(cacheDir, 'vote-playlists-archive')
    mpdLogsArchiveDir = mypycommons.file.JoinPaths(cacheDir, 'mpd-logs-archive')

    # Dirs of where various test data is stored: static test files
    testDataStaticDir = 'Z:\\Development\\Test Data\\mlYou'
    testDataStaticAudioFilesDir = mypycommons.file.JoinPaths(testDataStaticDir, 'test-audio-files')

    # Dirs of where various test data is stored: generated temp test files
    testDataGenTempDir = mypycommons.file.JoinPaths(cacheDir, '_test-data-generated')
    testDataGenAudioFilesDir = mypycommons.file.JoinPaths(testDataGenTempDir, 'test-audio-files')
    testDataGenVotePlaylistsDir = mypycommons.file.JoinPaths(testDataGenTempDir, 'test-vote-playlists')

    # Create empty directories if any of the ones defined above don't exist
    if (not mypycommons.file.directoryExists(logDir)):
        mypycommons.file.createDirectory(logDir)

    if (not mypycommons.file.directoryExists(cacheDir)):
        mypycommons.file.createDirectory(cacheDir)

    # -----------
    if (not mypycommons.file.directoryExists(testDataGenTempDir)):
        mypycommons.file.createDirectory(testDataGenTempDir)

    if (not mypycommons.file.directoryExists(testDataGenAudioFilesDir)):
        mypycommons.file.createDirectory(testDataGenAudioFilesDir)

    if (not mypycommons.file.directoryExists(testDataGenVotePlaylistsDir)):
        mypycommons.file.createDirectory(testDataGenVotePlaylistsDir)

    if (not mypycommons.file.directoryExists(votePlaylistsTempDir)):
        mypycommons.file.createDirectory(votePlaylistsTempDir)

    if (not mypycommons.file.directoryExists(votePlaylistsArchiveDir)):
        mypycommons.file.createDirectory(votePlaylistsArchiveDir)

    if (not mypycommons.file.directoryExists(mpdLogsArchiveDir)):
        mypycommons.file.createDirectory(mpdLogsArchiveDir)

    if (not mypycommons.file.directoryExists(tagBackupsDir)):
        mypycommons.file.createDirectory(tagBackupsDir)