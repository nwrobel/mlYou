'''
mlu.common.settings

Module containing the definition for setting values for MLU (project-wide constants).
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

class MLUUserConfig:
    def __init__(self):
        self.audioLibraryRootDir = ''
        self.mpdLogFilepath = ''
        self.mpdLogBackupDir = ''
        self.votePlaylistsDir = ''
        self.votePlaylistsArchiveDir = ''

class MLUSettings:
    def __new__(cls):
        """ creates a singleton object, if it is not created,
        or else returns the previous singleton object"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(MLUSettings, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.userConfig = None
        self.projectRootDir = ''
        self.logDir = ''
        self.cacheDir = ''
        self.tempDir = ''
        self.testDataDir = ''
        self.loggerName = "mlu-script"

        self._loadSettings()
        self._createDirectories()

    def cleanupTempDir(self):
        ''' 
        Removes the project's temp dir, which can contain old cache files
        ''' 
        if (mypycommons.file.pathExists(self.tempDir)):
            mypycommons.file.deletePath(self.tempDir)

    def _loadSettings(self):
        self.userConfig = self._getUserConfig()

        self.projectRootDir = self._getProjectRootDirectory()
        self.logDir = mypycommons.file.joinPaths(self.projectRootDir, '~logs')
        self.cacheDir = mypycommons.file.joinPaths(self.projectRootDir, '~cache')
        self.tempDir = mypycommons.file.joinPaths(self.cacheDir, 'temp')
        self.testDataDir = mypycommons.file.joinPaths(self.projectRootDir, 'test/data')    

    def _createDirectories(self):
        if (not mypycommons.file.pathExists(self.logDir)):
            mypycommons.file.createDirectory(self.logDir)

        if (not mypycommons.file.pathExists(self.cacheDir)):
            mypycommons.file.createDirectory(self.cacheDir)

        if (not mypycommons.file.pathExists(self.tempDir)):
            mypycommons.file.createDirectory(self.tempDir)

    def _getUserConfig(self):
        configFilepath = mypycommons.file.joinPaths(self._getProjectRootDirectory(), 'mlu.config.json')
        configData = mypycommons.file.readJsonFile(configFilepath)

        userConfig = MLUUserConfig()
        userConfig.audioLibraryRootDir = configData['audioLibraryRootDir']
        userConfig.mpdLogFilepath = configData['mpdLogFilepath']
        userConfig.mpdLogBackupDir = configData['mpdLogBackupDir']
        userConfig.votePlaylistsDir = configData['votePlaylistsDir']
        userConfig.votePlaylistsArchiveDir = configData['votePlaylistsArchiveDir']

        return userConfig

    def _getProjectRootDirectory(self):
        thisScriptDir = mypycommons.file.getThisScriptCurrentDirectory()
        projectRootDir = mypycommons.file.joinPaths(thisScriptDir, '..')
        return projectRootDir

