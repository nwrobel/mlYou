'''
update-rating-tags-for-library.py

This script goes through all songs in the music library and ensures the RATING tag is correctly
set, based on the current values in the VOTES array tag. All songs with an incorrect RATING tag
are corrected and reported when the script finishes.

'''

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

# import external Python modules
from prettytable import PrettyTable

from mlu.settings import MLUSettings

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

mypycommons.logger.initSharedLogger(logDir=MLUSettings.logDir)
mypycommons.logger.setSharedLoggerConsoleOutputLogLevel("info")
mypycommons.logger.setSharedLoggerFileOutputLogLevel("info")
logger = mypycommons.logger.getSharedLogger()

# import project-related modules
import mlu.tags.backup
import mlu.ratestats
import mlu.library.musiclib

def _getRatingTagUpdatesSummaryFilepath():
    '''
    Returns the filepath for the ratestat tags updates summary log file.
    '''
    backupFilename = "[{}] update-rating-tags-for-library_tag-updates-summary.txt".format(
        mypycommons.time.getCurrentTimestampForFilename()
    )
    filepath = mypycommons.file.JoinPaths(MLUSettings.logDir, backupFilename)

    return filepath

def _writeRatingTagUpdatesSummaryFile(updatedAudioFilesResults, summaryFilepath):
    '''
    Writes out a log file containing a table in pretty format with the ratestat tags updates.

    Params:
        audioFileVoteDataList: list of AudioFileVoteData objects, the new votes data
        summaryFilepath: path of the log output file to be written
    '''
    tagUpdatesTable = PrettyTable()
    tagUpdatesTable.field_names = ["Title", "Artist", "Old Rating", "New Rating"]
    tagUpdatesTable.align["Title"] = "l"
    tagUpdatesTable.align["Artist"] = "l"
    tagUpdatesTable.align["Old Rating"] = "r"
    tagUpdatesTable.align["New Rating"] = "r"

    for updateResult in updatedAudioFilesResults:
        tagHandler = mlu.tags.io.AudioFileTagIOHandler(updateResult.audioFilepath)
        currentTags = tagHandler.getTags()

        tagUpdatesTable.add_row([
            currentTags.title, 
            currentTags.artist, 
            updateResult.oldRating,
            updateResult.newRating
        ])

    mypycommons.file.writeToFile(filepath=summaryFilepath, content=tagUpdatesTable.get_string())

# ------------------------------- Main script procedure --------------------------------------------
#
if __name__ == "__main__":
    logger.info("Performing full backup (checkpoint) of all music library audio files tags")
    tagsBackupFilepath = mlu.tags.backup.backupMusicLibraryAudioTags()

    logger.info("Searching for all audio under music library root path '{}'".format(MLUSettings.musicLibraryRootDir))
    libraryAudioFiles = mlu.library.musiclib.getAllMusicLibraryAudioFilepaths()

    libraryAudioFilesCount = len(libraryAudioFiles)
    logger.info("Found {} audio files in music library root path".format(libraryAudioFilesCount))

    logger.info("Checking RATING tags for all audio files and fixing incorrect values")
    updatedAudioFilesResults = []
    erroredAudioFiles = []

    for i, songFilepath in enumerate(libraryAudioFiles):
        try:
            updateResult = mlu.ratestats.updateRatingTag(songFilepath)
            if (updateResult.wasUpdated):
                logger.info("Fixed incorrect RATING tag for file '{}'".format(songFilepath))
                updatedAudioFilesResults.append(updateResult)
        
        except:
            logger.exception("updateRatingTag operation failed: File='{}'".format(songFilepath))
            erroredAudioFiles.append(songFilepath)  

        mypycommons.display.printProgressBar(i + 1, libraryAudioFilesCount, prefix='Checking/fixing {} audio files:'.format(libraryAudioFilesCount), suffix='Complete', length=100)

    logger.info("RATING tag checking process complete")
    logger.info("{} songs had an incorrect RATING fixed successfully".format(len(updatedAudioFilesResults)))
    logger.info("{} songs files failed to have the RATING fixed".format(len(erroredAudioFiles)))

    if (not erroredAudioFiles):
        logger.info("Process completed successfully: all songs RATING tags verified")
        logger.info("Writing RATING tag updates summary file")

        summaryFilepath = _getRatingTagUpdatesSummaryFilepath()
        _writeRatingTagUpdatesSummaryFile(updatedAudioFilesResults, summaryFilepath)
        logger.info("Summary file written successfully: File='{}'".format(summaryFilepath))

    else:
        erroredAudioFilesFmt = "\n".join(erroredAudioFiles)
        logger.info("Failed to fix RATING tag for the following files:\n{}".format(erroredAudioFilesFmt))
        
        logger.info("Process completed with failures: undoing all tag changes to the music library (reverting to checkpoint)")
        mlu.tags.backup.restoreMusicLibraryAudioTagsFromBackup(tagsBackupFilepath)

        logger.info("Tags backup restored successfully: all changes were undone - run this script again to retry")

    logger.info('Script complete')