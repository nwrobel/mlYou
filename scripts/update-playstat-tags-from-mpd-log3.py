'''

'''
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from com.nwrobel import mypycommons
from com.nwrobel.mypycommons.logger import CommonLogger, LogLevel

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.mpd.log import MpdLog
from mlu.mpd.plays import MpdPlaybackProvider
from mlu.tags.playstats2 import PlaystatTagUpdaterForMpd
from mlu.settings import MLUSettings

class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    mluSettings = providers.Singleton(
        MLUSettings
    )

    commonLogger = providers.Singleton(
        CommonLogger,
        loggerName=mluSettings().loggerName,
        logDir=mluSettings().logDir,
        logFilename=__name__
    )

    mpdLog = providers.Singleton(
        MpdLog,
        logFilepath=mluSettings().userConfig.mpdLogFilepath,
        commonLogger=commonLogger
    )

    mpdPlaybackProvider = providers.Singleton(
        MpdPlaybackProvider,
        mpdLog=mpdLog,
        audioLibraryRootDir=mluSettings().userConfig.audioLibraryRootDir,
        commonLogger=commonLogger
    )

    playstatTagUpdaterForMpd = providers.Singleton(
        PlaystatTagUpdaterForMpd,
        mpdPlaybackProvider=mpdPlaybackProvider,
        mluSettings=mluSettings,
        commonLogger=commonLogger
    )


if __name__ == "__main__":
    container = Container()

    mluSettings = container.mluSettings()
    commonLogger = container.commonLogger()
    provider = container.playstatTagUpdaterForMpd()

    commonLogger.setFileOutputLogLevel(LogLevel.DEBUG)
    logger = commonLogger.getLogger()

    provider.processMpdLogFile()

    mluSettings.cleanupTempDir()
    logger.info('Script complete')
