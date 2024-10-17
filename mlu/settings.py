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

class MLURatingAutoplaylistConfigItem:
    def __init__(self, filename: str, minValue: float, maxValue: float):
        self.filename = filename
        self.minValue = minValue
        self.maxValue = maxValue

class MLUUnratedAutoplaylistSimpleConfigItem:
    def __init__(self, filenamePattern: str, genres: List):
        if ("{}" not in filenamePattern):
            raise Exception("need token replacement char '{}' in filenamePattern")

        self.filenamePattern = filenamePattern
        self.genres = genres

class MLUUnratedAutoplaylistAdvancedConfigItem:
    def __init__(self, filename: str, query: str):
        self.filename = filename
        self.query = query


class MLUUnratedAutoplaylistConfig:
    def __init__(self, jsonConfig: dict):
        simpleCfg = jsonConfig['simpleGenreConfig']
        advancedCfg = jsonConfig['advancedGenreConfig']

        self.simpleCfg = MLUUnratedAutoplaylistSimpleConfigItem(
            simpleCfg['filenamePattern'],
            simpleCfg['genres']
        )      

        self.advancedConfigs = []  
        
        for advConfigItem in advancedCfg:
            self.advancedConfigs.append(
                MLUUnratedAutoplaylistAdvancedConfigItem(
                    advConfigItem['filename'], 
                    advConfigItem['query'])
            )


class MLURatingConfig:
    def __init__(self, jsonConfig: dict):
        if (jsonConfig is None):
            self.votePlaylistInputDir = ''
            self.votePlaylistArchiveDir = ''
            self.votePlaylistFiles = []
        else:  
            self.votePlaylistInputDir = jsonConfig['votePlaylistInputDir']
            self.votePlaylistArchiveDir = jsonConfig['votePlaylistArchiveDir']
            self.votePlaylistFiles = []

            for votePlaylistFileJsonCfg in jsonConfig['votePlaylistFiles']:
                self.votePlaylistFiles.append(
                    MLUVotePlaylistFileConfigItem(votePlaylistFileJsonCfg['filename'], votePlaylistFileJsonCfg['value'])
                )


class MLUAutoPlaylistsConfig:
    def __init__(self, jsonConfig: dict):
        self.outputDir = ''
        self.ratingConfigs = []  
        self.unratedConfig = None

        self.outputDir = jsonConfig['outputDir']

        for ratingPlaylistCfg in jsonConfig['rating']:
            self.ratingConfigs.append(
                MLURatingAutoplaylistConfigItem(
                    ratingPlaylistCfg['filename'], 
                    ratingPlaylistCfg['minValue'],
                    ratingPlaylistCfg['maxValue']
                )
            )

        self.unratedConfig = MLUUnratedAutoplaylistConfig(jsonConfig['unrated'])


class MLUConvertPlaylistsConfig:
    def __init__(self, jsonConfig: dict):
        if (jsonConfig is None):
            self.inputDir = ''
            self.outputDir = ''
        else:      
            self.inputDir = jsonConfig['inputDir']
            self.outputDir = jsonConfig['outputDir']

class MLUMpdConfig:
    def __init__(self, jsonConfig: dict):
        if (jsonConfig is None):
            self.logFilepath = ''
            self.logArchiveDir = ''
            self.outputDir = ''
        else:
            self.logFilepath = jsonConfig['logFilepath']
            self.logArchiveDir = jsonConfig['logArchiveDir']
            self.outputDir = jsonConfig['outputDir']

def getConfigOrNull(jsonConfig, keyName):
    try:
        return jsonConfig[keyName]
    except:
        return None

class MLUUserConfig:
    def __init__(self, jsonConfig: dict):
        self.audioLibraryRootDir = jsonConfig['audioLibraryRootDir']
        self.tagBackupFilepath = jsonConfig['tagBackupFilepath']
        
        logDir = jsonConfig['logDir']
        if (logDir):
            self.logDir = logDir
        else:
            self.logDir = self.defaultLogDir 

        self.autoplaylistsConfig = MLUAutoPlaylistsConfig(getConfigOrNull(jsonConfig, 'autoplaylists'))
        self.convertPlaylistsConfig = MLUConvertPlaylistsConfig(getConfigOrNull(jsonConfig, 'convertPlaylists'))
        self.ratingConfig = MLURatingConfig(getConfigOrNull(jsonConfig, 'rating'))
        self.mpdConfig = MLUMpdConfig(getConfigOrNull(jsonConfig, 'mpd'))



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
        configFilepath = mypycommons.file.joinPaths(self._getProjectRootDirectory(), 'config/{}'.format(configFilename))
        configData = mypycommons.file.readJsonFile(configFilepath)

        userConfig = MLUUserConfig(configData)
        return userConfig

    def _getProjectRootDirectory(self):
        thisScriptDir = mypycommons.file.getThisScriptCurrentDirectory()
        projectRootDir = mypycommons.file.joinPaths(thisScriptDir, '..')
        return projectRootDir 

