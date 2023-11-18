'''

'''
import argparse

from com.nwrobel import mypycommons
from com.nwrobel.mypycommons.logger import CommonLogger, LogLevel
import com.nwrobel.mypycommons.file

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import mlu.tags.io
from mlu.mpd.log import MpdLog
from mlu.mpd.plays import MpdPlaybackProvider
from mlu.tags.playstats2 import PlaystatTagUpdaterForMpd
from mlu.settings import MLUSettings

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument("--config-file", 
        help="config file name located in root dir",
        default="mlu.config.json",
        type=str,
        dest='configFile'
    )
    group.add_argument('-l', '--load', 
        action='store_true',
        dest='load',
        help="Load the MPD log file and generate directory of output data"
    )

    group.add_argument("-s", "--save", 
        type=str,
        dest='saveFromDataDirectory',
        help="Update audio file playstats tags from previously generated output data"
    )
    args = parser.parse_args()

    settings = MLUSettings(configFilename=args.configFile)

    loggerWrapper = mypycommons.logger.CommonLogger(loggerName=settings.loggerName, logDir=settings.userConfig.logDir, logFilename="update-ratestat-tags-from-vote-playlists.py.log")
    logger = loggerWrapper.getLogger()

    provider = PlaystatTagUpdaterForMpd(settings, loggerWrapper)

    if (args.load):
        provider.processMpdLogFile()
    elif (args.saveFromDataDirectory):
        provider.updatePlaystatTags(args.saveFromDataDirectory)

    settings.cleanupTempDir()
    logger.info('Script complete')

