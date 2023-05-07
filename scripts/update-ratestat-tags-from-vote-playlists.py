'''
update-ratestat-tags-from-vote-playlists.py

This script uses the votes playlists (1-10) to add the new votes to and update the ratestat tags of 
audio files in the music library. 

'''

# import external Python modules

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger

from mlu.settings import MLUSettings
from mlu.tags.ratestats import RatestatTagsUpdater

if __name__ == "__main__":
    settings = MLUSettings()
    loggerWrapper = mypycommons.logger.CommonLogger(loggerName=settings.loggerName, logDir=settings.logDir, logFilename=__name__)
    logger = loggerWrapper.getLogger()

    ratestatsProcessor = RatestatTagsUpdater(mluSettings=settings, commonLogger=loggerWrapper)
    ratestatsProcessor.processVotePlaylists()

    settings.cleanupTempDir()
    logger.info('Script complete')
