'''
update-ratestat-tags-from-vote-playlists.py

This script uses the votes playlists (1-10) to add the new votes to and update the ratestat tags of 
audio files in the music library. 

'''
import argparse

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.settings import MLUSettings
import mlu.library.playlist

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config-file", 
        help="config file name located in root dir",
        default="mlu.TEST.config.json",
        type=str,
        dest='configFile'
    )
    args = parser.parse_args()

    settings = MLUSettings(configFilename=args.configFile)

    loggerWrapper = mypycommons.logger.CommonLogger(loggerName=settings.loggerName, logDir=settings.userConfig.logDir, logFilename="create-rating-autoplaylists.py.log")
    logger = loggerWrapper.getLogger()

    autoplaylistsOutputDir = settings.userConfig.autoplaylistsOutputDir

    playlistFilename = "Rating 7-10 (desc).m3u"
    playlistFilepath = mypycommons.file.joinPaths(autoplaylistsOutputDir, playlistFilename)
    items = mlu.library.playlist.createRatingAutoplaylist(settings.userConfig.audioLibraryRootDir, playlistFilepath, 7, 10)

    playlistFilename = "Rating 8-10 (desc).m3u"
    playlistFilepath = mypycommons.file.joinPaths(autoplaylistsOutputDir, playlistFilename)
    items = mlu.library.playlist.createRatingAutoplaylist(settings.userConfig.audioLibraryRootDir, playlistFilepath, 8, 10)

    playlistFilename = "Rating 9-10 (desc).m3u"
    playlistFilepath = mypycommons.file.joinPaths(autoplaylistsOutputDir, playlistFilename)
    items = mlu.library.playlist.createRatingAutoplaylist(settings.userConfig.audioLibraryRootDir, playlistFilepath, 9, 10)    

    settings.cleanupTempDir()
    logger.info('Script complete')
