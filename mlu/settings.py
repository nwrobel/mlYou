'''
mlu.common.settings

Module containing the definition for setting values for MLU (project-wide constants).
'''

from typing import List

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

class MLUVotePlaylistFileConfigItem:
    def __init__(self, filename: str, value: float):
        self.filename = filename
        self.value = value

class MLUVotePlaylistConfig:
    def __init__(self, jsonConfig: dict):
        self.votePlaylistInputDir = jsonConfig['votePlaylistInputDir']
        self.votePlaylistArchiveDir = jsonConfig['votePlaylistArchiveDir']
        self.votePlaylistFiles = []

        for votePlaylistFileJsonCfg in jsonConfig['votePlaylistFiles']:
            self.votePlaylistFiles.append(
                MLUVotePlaylistFileConfigItem(votePlaylistFileJsonCfg['filename'], votePlaylistFileJsonCfg['value'])
            )


class MLUUserConfig:
    def __init__(self):
        self.audioLibraryRootDir = ''
        self.mpdLogFilepath = ''
        self.mpdLogArchiveDir = ''
        self.convertPlaylistsInputDir = ''
        self.convertPlaylistsOutputDir = ''
        self.logDir = ''
        self.playlistsDir = ''
        self.votePlaylistConfig = None

class MLUSettings:
    @staticmethod
    def getTempDir():
        thisScriptDir = mypycommons.file.getThisScriptCurrentDirectory()
        projectRootDir = mypycommons.file.joinPaths(thisScriptDir, '..')
        cacheDir = mypycommons.file.joinPaths(projectRootDir, '~cache')
        tempDir = mypycommons.file.joinPaths(cacheDir, 'temp')  
        return tempDir    

    def __init__(self, configFilename: str):
        self.userConfig = None
        self.projectRootDir = ''
        self.defaultLogDir = ''
        self.cacheDir = ''
        self.tempDir = ''
        self.testDataDir = ''
        self.loggerName = "mlu-script"

        self._loadSettings(configFilename)
        self._createDirectories()

    def cleanupTempDir(self):
        ''' 
        Removes the project's temp dir, which can contain old cache files
        ''' 
        if (mypycommons.file.pathExists(self.tempDir)):
            mypycommons.file.deletePath(self.tempDir)

    def _loadSettings(self, configFilename: str):
        self.projectRootDir = self._getProjectRootDirectory()
        self.defaultLogDir = mypycommons.file.joinPaths(self.projectRootDir, '~logs')
        self.cacheDir = mypycommons.file.joinPaths(self.projectRootDir, '~cache')
        self.tempDir = mypycommons.file.joinPaths(self.cacheDir, 'temp')
        self.testDataDir = mypycommons.file.joinPaths(self.projectRootDir, 'test/data') 

        self.userConfig = self._getUserConfig(configFilename)

    def _createDirectories(self):
        if (not mypycommons.file.pathExists(self.defaultLogDir)):
            mypycommons.file.createDirectory(self.defaultLogDir)

        if (self.userConfig.logDir and not mypycommons.file.pathExists(self.userConfig.logDir)):
            mypycommons.file.createDirectory(self.userConfig.logDir)

        if (not mypycommons.file.pathExists(self.cacheDir)):
            mypycommons.file.createDirectory(self.cacheDir)

        if (not mypycommons.file.pathExists(self.tempDir)):
            mypycommons.file.createDirectory(self.tempDir)

    def _getUserConfig(self, configFilename: str):
        configFilepath = mypycommons.file.joinPaths(self._getProjectRootDirectory(), configFilename)
        configData = mypycommons.file.readJsonFile(configFilepath)

        userConfig = MLUUserConfig()
        userConfig.audioLibraryRootDir = configData['audioLibraryRootDir']
        userConfig.mpdLogFilepath = configData['mpdLogFilepath']
        userConfig.mpdLogArchiveDir = configData['mpdLogArchiveDir']
        userConfig.convertPlaylistsInputDir = configData['convertPlaylistsInputDir']
        userConfig.convertPlaylistsOutputDir = configData['convertPlaylistsOutputDir']
        userConfig.playlistsDir = configData['playlistsDir']
        
        logDir = configData['logDir']
        if (logDir):
            userConfig.logDir = logDir
        else:
            userConfig.logDir = self.defaultLogDir 

        userConfig.votePlaylistConfig = MLUVotePlaylistConfig(configData['votePlaylistConfig'])

        return userConfig

    def _getProjectRootDirectory(self):
        thisScriptDir = mypycommons.file.getThisScriptCurrentDirectory()
        projectRootDir = mypycommons.file.joinPaths(thisScriptDir, '..')
        return projectRootDir 

