import argparse

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.settings import MLUSettings
import mlu.managers.load_tags
import mlu.managers.write_autoplaylists

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config-file", 
        help="config file name in mlu/config",
        default="mlu.config.json",
        type=str,
        dest='configFile'
    )
    args = parser.parse_args()

    settings = MLUSettings(configFilename=args.configFile)

    loggerWrapper = mypycommons.logger.CommonLogger(loggerName=settings.loggerName, logDir=settings.userConfig.logDir, logFilename="update-autoplaylists.py.log")
    logger = loggerWrapper.getLogger()

    provider = mlu.managers.load_tags.LoadLibraryTagsManager(settings, loggerWrapper)
    provider.saveLibraryTagsSnapshot()

    provider = mlu.managers.write_autoplaylists.WriteAutoplaylistsManager(settings, loggerWrapper)
    provider.writeRatingAutoplaylists()
    provider.writeUnratedSimpleGenreAutoplaylists()
    provider.writeUnratedAutoplaylists()

    settings.cleanupTempDir()
    logger.info('Script complete')