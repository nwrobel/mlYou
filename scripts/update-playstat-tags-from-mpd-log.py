'''
update-playstat-tags-from-mpd-log.py

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
import mlu.mpd.logs
import mlu.mpd.plays
import mlu.playstats


def _getPlaystatTagUpdatesPreviewFilepath():
    '''
    '''
    backupFilename = "[{}] update-playstat-tags-from-mpd-log_preview-changes.txt".format(
        mypycommons.time.getCurrentTimestampForFilename()
    )
    filepath = mypycommons.file.JoinPaths(MLUSettings.logDir, backupFilename)

    return filepath

def _writePlaystatTagUpdatesPreviewFile(audioFilePlaybackDataList, logFilepath):
    '''
    '''
    tagUpdatesTable = PrettyTable()
    tagUpdatesTable.field_names = ["Title", "Artist", "Plays Added", "Added Play Times"]
    tagUpdatesTable.align["Title"] = "l"
    tagUpdatesTable.align["Artist"] = "l"
    tagUpdatesTable.align["Plays Added"] = "r"
    tagUpdatesTable.align["Added Play Times"] = "r"

    for audioFilePlaybackData in audioFilePlaybackDataList:
        tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFilePlaybackData.audioFilepath)
        currentTags = tagHandler.getTags()

        tagUpdatesTable.add_row([
            currentTags.title, 
            currentTags.artist, 
            len(audioFilePlaybackData.playbackInstances),
            [playbackInstance.playTimeStart for playbackInstance in audioFilePlaybackData.playbackInstances],
        ])

    mypycommons.file.writeToFile(filepath=logFilepath, content=tagUpdatesTable.get_string())

def _getPlaystatTagUpdatesSummaryFilepath():
    '''
    Returns the filepath for the playstat tags updates summary log file.
    '''
    backupFilename = "[{}] update-playstat-tags-from-mpd-log_updates-summary.txt".format(
        mypycommons.time.getCurrentTimestampForFilename()
    )
    filepath = mypycommons.file.JoinPaths(MLUSettings.logDir, backupFilename)

    return filepath

def _writePlaystatTagUpdatesSummaryFile(audioFilePlaybackDataList, summaryFilepath):
    '''
    Writes out a log file containing a table in pretty format with the playstat tags updates.
    '''
    tagUpdatesTable = PrettyTable()
    tagUpdatesTable.field_names = ["Title", "Artist", "Playcount Increase", "Added Play Times", "New Playcount", "New Last Play Time", "New All Play Times"]
    tagUpdatesTable.align["Title"] = "l"
    tagUpdatesTable.align["Artist"] = "l"
    tagUpdatesTable.align["Playcount Increase"] = "r"
    tagUpdatesTable.align["Added Play Times"] = "r"
    tagUpdatesTable.align["New Playcount"] = "r"
    tagUpdatesTable.align["New Last Play Time"] = "r"
    tagUpdatesTable.align["New All Play Times"] = "r"

    for audioFilePlaybackData in audioFilePlaybackDataList:
        tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFilePlaybackData.audioFilepath)
        currentTags = tagHandler.getTags()

        tagUpdatesTable.add_row([
            currentTags.title, 
            currentTags.artist, 
            len(audioFilePlaybackData.playbackInstances),
            [playbackInstance.playTimeStart for playbackInstance in audioFilePlaybackData.playbackInstances],
            currentTags.playCount,
            currentTags.dateLastPlayed,
            currentTags.dateAllPlays
        ])

    mypycommons.file.writeToFile(filepath=summaryFilepath, content=tagUpdatesTable.get_string())

# ------------------------------- Main script procedure --------------------------------------------
#
if __name__ == "__main__":

    #logger.info("Performing full backup (checkpoint) of all music library audio files tags")
    #tagsBackupFilepath = mlu.tags.backup.backupMusicLibraryAudioTags()

    logger.info("Copying MPD log file at '{}' to ~cache temp dir".format(MLUSettings.mpdLogFilepath))
    mypycommons.file.CopyFilesToDirectory(MLUSettings.mpdLogFilepath, MLUSettings.tempDir)
    tempMpdLogFilepath = mypycommons.file.JoinPaths(
        MLUSettings.tempDir, 
        mypycommons.file.GetFilename(MLUSettings.mpdLogFilepath)
    )

    mpdLogLines = mlu.mpd.logs.collectMPDLogLinesFromLogFile(tempMpdLogFilepath)

    collectResults = mlu.mpd.plays.collectAudioFilePlaybackDataFromMPDLogLines(mpdLogLines)
    audioFilePlaybackDataList = collectResults['playbackDataList']
    preserveLastLogLine = collectResults['preserveLastLogLine']

    previewFilepath = _getPlaystatTagUpdatesPreviewFilepath()
    _writePlaystatTagUpdatesPreviewFile(audioFilePlaybackDataList, previewFilepath)
    logger.info("Changes preview file written successfully: File='{}'".format(previewFilepath))

    updatedAudioFiles = []
    failedAudioFiles = []
    for audioFilePlaybackData in audioFilePlaybackDataList:
        try:
            mlu.playstats.updateAudioFilePlaystatTagsFromPlaybackData(audioFilePlaybackData)

            logger.info("Updated playstats tags from audioFilePlaybackData for audio file '{}'".format(audioFilePlaybackData.audioFilepath))
            updatedAudioFiles.append(audioFilePlaybackData.audioFilepath)

        except:
            logger.exception("Failed to update playstats tags from audioFilePlaybackData: File='{}'".format(audioFilePlaybackData.audioFilepath))
            failedAudioFiles.append(audioFilePlaybackData.audioFilepath)
    
    logger.info("Playstats tags update process complete")
    logger.info("{} audio files had playstats tags updated successfully".format(len(updatedAudioFiles)))
    logger.info("{} audio files failed to have playstats tags updated".format(len(failedAudioFiles)))

    if (not failedAudioFiles):
        logger.info("Process completed successfully without errors")
        logger.info("Writing playstats tags updates summary file")

        summaryFilepath = _getPlaystatTagUpdatesSummaryFilepath()
        _writePlaystatTagUpdatesSummaryFile(audioFilePlaybackDataList, summaryFilepath)
        logger.info("Summary file written successfully: File='{}'".format(summaryFilepath))

        logger.info("Resetting MPD log file, now that it has been parsed and the data was used")
        mlu.mpd.logs.resetMPDLog(mpdLogFilepath=MLUSettings.mpdLogFilepath, tempMpdLogFilepath=tempMpdLogFilepath, preserveLastLogLine=preserveLastLogLine)

    else:
        failedAudioFilesFmt = "\n".join(failedAudioFiles)
        logger.info("Failed to update playstats tags for the following files:\n{}".format(failedAudioFilesFmt))
        
        logger.info("Process completed with failures: undoing all tag changes to the music library (reverting to checkpoint)")
        #mlu.tags.backup.restoreMusicLibraryAudioTagsFromBackup(tagsBackupFilepath)

        logger.info("Tags backup restored successfully: all changes were undone - run this script again to retry")

    logger.info('Script complete')