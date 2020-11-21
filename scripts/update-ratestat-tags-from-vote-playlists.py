'''
update-ratestat-tags-from-vote-playlists.py

This script uses the votes playlists (1-10) to add the new votes to and update the ratestat tags of 
audio files in the music library. 

'''

# import external Python modules
from prettytable import PrettyTable

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.settings import MLUSettings

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

mypycommons.logger.initSharedLogger(logDir=MLUSettings.logDir)
logger = mypycommons.logger.getSharedLogger()

# import project-related modules
import mlu.tags.backup
import mlu.ratestats

# --------------------------------------- Helper functions -----------------------------------------
#
def _getRatestatTagUpdatesSummaryFilepath():
    '''
    Returns the filepath for the ratestat tags updates summary log file.
    '''
    backupFilename = "[{}] update-ratestat-tags-from-vote-playlists_tag-updates-summary.txt".format(
        mypycommons.time.getCurrentTimestampForFilename()
    )
    filepath = mypycommons.file.JoinPaths(MLUSettings.logDir, backupFilename)

    return filepath

def _writeRatestatTagUpdatesSummaryFile(audioFileVoteDataList, summaryFilepath):
    '''
    Writes out a log file containing a table in pretty format with the ratestat tags updates.

    Params:
        audioFileVoteDataList: list of AudioFileVoteData objects, the new votes data
        summaryFilepath: path of the log output file to be written
    '''
    tagUpdatesTable = PrettyTable()
    tagUpdatesTable.field_names = ["Title", "Artist", "Votes Added", "New Rating", "New Votes List"]
    tagUpdatesTable.align["Title"] = "l"
    tagUpdatesTable.align["Artist"] = "l"
    tagUpdatesTable.align["Votes Added"] = "r"
    tagUpdatesTable.align["New Rating"] = "r"
    tagUpdatesTable.align["New Votes List"] = "r"

    for audioFileVotesData in audioFileVoteDataList:
        tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFileVotesData.filepath)
        currentTags = tagHandler.getTags()

        votesAdded = mlu.tags.common.formatValuesListToAudioTag(audioFileVotesData.votes)

        tagUpdatesTable.add_row([
            currentTags.title, 
            currentTags.artist, 
            votesAdded,
            currentTags.rating,
            currentTags.votes
        ])

    mypycommons.file.writeToFile(filepath=summaryFilepath, content=tagUpdatesTable.get_string())

# ------------------------------- Main script procedure --------------------------------------------
#
if __name__ == "__main__":

    logger.info("Performing full backup (checkpoint) of all music library audio files tags")
    tagsBackupFilepath = mlu.tags.backup.backupMusicLibraryAudioTags()

    logger.info("Copying vote playlist files to temp location in ~cache")
    mlu.ratestats.copyVotePlaylistsToTemp(votePlaylistsSourceDir=MLUSettings.votePlaylistsDir, votePlaylistsTempDir=MLUSettings.tempDir)

    logger.info("Loading audio file votes data from all vote playlists")
    audioFileVoteDataList = mlu.ratestats.getAudioFileVoteDataFromRatePlaylists(votePlaylistsDir=MLUSettings.tempDir)

    logger.info("Vote playlists data loaded successfully")
    logger.info("Writing new ratestats tag data to audio files")

    erroredAudioFilepaths = []
    for audioFileVoteData in audioFileVoteDataList:
        try:
            mlu.ratestats.updateRatestatTagsFromVoteData(audioFileVoteData)
        except:
            logger.exception("updateRatestatTagsFromVoteData operation failed: File='{}'".format(audioFileVoteData.filepath))
            erroredAudioFilepaths.append(audioFileVoteData.filepath)

    logger.info("Votes processing complete")
    logger.info("{} audio files were processed".format(len(audioFileVoteDataList)))
    logger.info("{} audio files failed update".format(len(erroredAudioFilepaths)))

    if (not erroredAudioFilepaths):
        logger.info("Process completed successfully: all ratestat tags updated with new votes")
        logger.info("Writing ratestat tag updates summary file")

        summaryFilepath = _getRatestatTagUpdatesSummaryFilepath()
        _writeRatestatTagUpdatesSummaryFile(audioFileVoteDataList, summaryFilepath)
        logger.info("Summary file written successfully: File='{}'".format(summaryFilepath))

        logger.info('Archiving the old vote playlists which were just processed')
        mlu.ratestats.archiveVotePlaylists(playlistsDir=MLUSettings.tempDir, archiveDir=MLUSettings.votePlaylistsArchiveDir)

        logger.info('Emptying already counted votes from vote playlists')
        mlu.ratestats.resetVotePlaylists(votePlaylistsSourceDir=MLUSettings.votePlaylistsDir, votePlaylistsTempDir=MLUSettings.tempDir)

    else:
        erroredAudioFilepathsFmt = "\n".join(erroredAudioFilepaths)
        logger.info("Failed to update ratestat tag values with new votes for the following files:\n{}".format(erroredAudioFilepathsFmt))
        
        logger.info("Process completed with failures: undoing all tag changes to the music library (reverting to checkpoint)")
        mlu.tags.backup.restoreMusicLibraryAudioTagsFromBackup(tagsBackupFilepath)

        logger.info("Tags backup restored successfully: all changes were undone - run this script again to retry")

    mypycommons.file.DeleteDirectory(MLUSettings.tempDir)
    logger.info('Script complete')