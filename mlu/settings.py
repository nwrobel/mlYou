'''
mlu.common.settings

Module containing the definition for setting values for MLU (project-wide constants).
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

def getProjectRootDirectory():
    thisScriptDir = mypycommons.file.getThisScriptCurrentDirectory()
    projectRootDir = mypycommons.file.joinPaths(thisScriptDir, '..')
    return projectRootDir

class MLUUserConfig:
    audioLibraryRootDirectory = ''
    mpdLogFilepath = ''
    mpdLogBackupDirectory = ''
    votePlaylistsRootDirectory = ''

    @classmethod
    def loadUserConfigFromConfigFile(self):
        configFilepath = mypycommons.file.joinPaths(getProjectRootDirectory(), 'mlu.config.json')
        configData = mypycommons.file.readJsonFile(configFilepath)

        self.audioLibraryRootDirectory = configData['audioLibraryRootDirectory']
        self.mpdLogFilepath = configData['mpdLogFilepath']
        self.mpdLogBackupDirectory = configData['mpdLogBackupDirectory']
        self.votePlaylistsRootDirectory = configData['votePlaylistsRootDirectory']

class MLUSettings:
    MLUUserConfig.loadUserConfigFromConfigFile()
    userConfig = MLUUserConfig

    projectRootDirectory = getProjectRootDirectory()
    logDirectory = mypycommons.file.joinPaths(projectRootDirectory, '~logs')
    cacheDirectory = mypycommons.file.joinPaths(projectRootDirectory, '~cache')

    # Dirs of where various types of cache files are stored
    tempDirectory = mypycommons.file.joinPaths(cacheDirectory, 'temp')

    # Test data
    testDataDir = mypycommons.file.joinPaths(projectRootDirectory, 'test/data')

    # Create empty directories
    if (not mypycommons.file.pathExists(logDirectory)):
        mypycommons.file.createDirectory(logDirectory)

    if (not mypycommons.file.pathExists(cacheDirectory)):
        mypycommons.file.createDirectory(cacheDirectory)

    if (not mypycommons.file.pathExists(tempDirectory)):
        mypycommons.file.createDirectory(tempDirectory)

