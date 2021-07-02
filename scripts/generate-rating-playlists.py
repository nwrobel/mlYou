'''
generate-rating-playlists.py

Creates autoplaylists based on song rating.

'''
from decimal import Decimal, ROUND_HALF_UP

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.settings import MLUSettings

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.display

mypycommons.logger.initSharedLogger(logDir=MLUSettings.logDir)
mypycommons.logger.setSharedLoggerConsoleOutputLogLevel("info")
mypycommons.logger.setSharedLoggerFileOutputLogLevel("info")
logger = mypycommons.logger.getSharedLogger()

# import project-related modules
import mlu.library.playlist
import mlu.tags.io
import mlu.library.musiclib

def _roundRatingValueForPlaylistMatching(ratingNum):
    value = Decimal(ratingNum).quantize(0, ROUND_HALF_UP)
    return int(value)

# ------------------------------- Main script procedure --------------------------------------------
#
if __name__ == "__main__":

    logger.info("Removing pre-existing (old) rating playlists")
    existingRatingPlaylists = mypycommons.file.GetAllFilesRecursive(MLUSettings.ratePlaylistsPublishedDir)
    for playlistFilepath in existingRatingPlaylists:
        mypycommons.file.DeleteFile(playlistFilepath)

    logger.info("Searching for all audio under music library root path '{}'".format(MLUSettings.musicLibraryRootDir))
    libraryAudioFiles = mlu.library.musiclib.getAllMusicLibraryAudioFilepaths()
    libraryAudioFilesCount = len(libraryAudioFiles)

    logger.info("Found {} audio files in library. Scanning rules".format(libraryAudioFilesCount))
    ratingPlaylistsData = []
    for rule in MLUSettings.ratePlaylistCreateRules:
        if (rule[0] == rule[1]):
            playlistBaseName = rule[0]
        else:
            playlistBaseName = "{}-{}".format(rule[0], rule[1])
        
        playlistName = "{}.m3u8".format(playlistBaseName)
        playlistFilepath = mypycommons.file.JoinPaths(MLUSettings.ratePlaylistsPublishedDir, playlistName)

        ratingPlaylistsData.append({
            'filepath': playlistFilepath,
            'allowedRatings': list(range(rule[0], rule[1] + 1)),
            'audioFilepaths': []
        })

    logger.info("Populating the rating playlists data based on rules")
    for i, audioFilepath in enumerate(libraryAudioFiles):
        tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFilepath)
        tags = tagHandler.getTags()
        
        if tags.rating:
            ratingNum = float(tags.rating)
            roundedRating = _roundRatingValueForPlaylistMatching(ratingNum)

            for ratingPlaylist in ratingPlaylistsData:
                if (roundedRating in ratingPlaylist['allowedRatings']):
                    ratingPlaylist['audioFilepaths'].append(audioFilepath)

        mypycommons.display.printProgressBar(i + 1, libraryAudioFilesCount, prefix='Filtering {} audio files into playlists:'.format(libraryAudioFilesCount), suffix='Done', length=80)

    logger.info("Writing playlist files")
    for ratingPlaylist in ratingPlaylistsData:
        mlu.library.playlist.createPlaylist(playlistFilepath=ratingPlaylist['filepath'], audioFilepaths=ratingPlaylist['audioFilepaths'])

    logger.info('Script complete')