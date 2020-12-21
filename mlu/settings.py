'''
mlu.common.settings

Module containing the definition for setting values for MLU (project-wide constants).
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.system

# ====================== DEFINE USER SETTINGS HERE FOR YOUR OS ==============================
def getUserSettingsWindows():
    return {
        'musicLibraryRootDir': "Z:\\Music Library\\Content",
        'votePlaylistsDir': "Z:\\Music Library\\!mpd-saved-playlists",
        'mpdLogFilepath': "D:\\Temp\\mpd-master-test.log"
    }

def getUserSettingsLinux(): 
    return {
        'musicLibraryRootDir': "/datastore/nick/Music Library/Content",
        'votePlaylistsDir': "/datastore/nick/Music Library/!mpd-saved-playlists",
        'mpdLogFilepath': "/var/log/mpd-master.log"
    }  
# ============= END OF USER SETTINGS DEFINITIONS ================

def getProjectRootDir():
    thisScriptDir = mypycommons.file.getThisScriptCurrentDirectory()
    projectRootDir = mypycommons.file.JoinPaths(thisScriptDir, '..')
    return projectRootDir

class MLUSettings:  
    # User setting values -------------------------------------------------------  
    if (mypycommons.system.thisMachineIsWindowsOS()):
        userSettings = getUserSettingsWindows()
    else:
        userSettings = getUserSettingsLinux()
        
    # Root of where the library music files are found
    musicLibraryRootDir = userSettings['musicLibraryRootDir']

    # Dir of where the vote playlists can be found
    votePlaylistsDir = userSettings['votePlaylistsDir']

    # Filepath to the MPD log file
    mpdLogFilepath = userSettings['mpdLogFilepath']

    # Derived setting values ---------------------------------------------------
    projectRootDir = getProjectRootDir()
    logDir = mypycommons.file.JoinPaths(projectRootDir, '~logs')
    cacheDir = mypycommons.file.JoinPaths(projectRootDir, '~cache')

    # Dirs of where various types of cache files are stored
    tempDir = mypycommons.file.JoinPaths(cacheDir, '_temp')
    tagBackupsDir = mypycommons.file.JoinPaths(cacheDir, 'audio-tag-backups')
    votePlaylistsArchiveDir = mypycommons.file.JoinPaths(cacheDir, 'vote-playlists-archive')
    mpdLogsArchiveDir = mypycommons.file.JoinPaths(cacheDir, 'mpd-logs-archive')

    # Dirs of where various test data is stored: static test files
    testDataStaticDir = 'Z:\\Development\\Test Data\\mlYou'
    testDataStaticAudioFilesDir = mypycommons.file.JoinPaths(testDataStaticDir, 'test-audio-files')
    testDataStaticAudioFilesTagsFile = mypycommons.file.JoinPaths(testDataStaticDir, 'test-audio-files-tags.json')

    # Dirs of where various test data is stored: generated temp test files
    testDataGenTempDir = mypycommons.file.JoinPaths(cacheDir, '_test-data-generated')
    testDataGenAudioFilesDir = mypycommons.file.JoinPaths(testDataGenTempDir, 'test-audio-files')
    testDataGenVotePlaylistsDir = mypycommons.file.JoinPaths(testDataGenTempDir, 'test-vote-playlists')
    testDataGenArchivedVotePlaylistsDir = mypycommons.file.JoinPaths(testDataGenTempDir, 'test-vote-playlists-archived')

    # Create empty directories ------------------------------------------------------
    if (not mypycommons.file.directoryExists(logDir)):
        mypycommons.file.createDirectory(logDir)

    if (not mypycommons.file.directoryExists(cacheDir)):
        mypycommons.file.createDirectory(cacheDir)

    if (not mypycommons.file.directoryExists(testDataGenTempDir)):
        mypycommons.file.createDirectory(testDataGenTempDir)

    if (not mypycommons.file.directoryExists(testDataGenAudioFilesDir)):
        mypycommons.file.createDirectory(testDataGenAudioFilesDir)

    if (not mypycommons.file.directoryExists(testDataGenVotePlaylistsDir)):
        mypycommons.file.createDirectory(testDataGenVotePlaylistsDir)

    if (not mypycommons.file.directoryExists(testDataGenArchivedVotePlaylistsDir)):
        mypycommons.file.createDirectory(testDataGenArchivedVotePlaylistsDir)

    if (not mypycommons.file.directoryExists(votePlaylistsArchiveDir)):
        mypycommons.file.createDirectory(votePlaylistsArchiveDir)

    if (not mypycommons.file.directoryExists(mpdLogsArchiveDir)):
        mypycommons.file.createDirectory(mpdLogsArchiveDir)

    if (not mypycommons.file.directoryExists(tagBackupsDir)):
        mypycommons.file.createDirectory(tagBackupsDir)

    # Delete the temp dir if it exists, then recreate it fresh
    # Temp dir should be fresh/empty at the start of any MLU script
    if (mypycommons.file.directoryExists(tempDir)):
        mypycommons.file.DeleteDirectory(tempDir)

    mypycommons.file.createDirectory(tempDir)
