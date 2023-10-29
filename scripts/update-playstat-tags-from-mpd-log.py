import json
import logging
from prettytable import PrettyTable

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.archive

from mlu.settings import MLUSettings
import mlu.mpd.log
import mlu.mpd.plays
import mlu.tags.playstats
from mlu.tags.io import AudioFileFormatNotSupportedError, AudioFileNonExistentError
import mlu.utilities





def _getAudioFilePlaybackInstancesFromJsonFile(jsonFilepath):
    playbackInstancesList = []
    dictList = mypycommons.file.readJsonFile(jsonFilepath)

    for playbackInstancesDict in dictList:
        playbackInstancesList.append(
            mlu.tags.playstats.AudioFilePlaybackInstances(audioFilepath=playbackInstancesDict["audioFilepath"], playbackDateTimes=playbackInstancesDict["playbackDateTimes"])
        )
    return playbackInstancesList



def _savePlaybacksHistorySummaryOutputFile(filepath, audioFilePlaybackInstancesList):
    playbackList = mlu.tags.playstats.convertAudioFilePlaybackInstancesListToPlaybackList(audioFilePlaybackInstancesList)
    playbackListSorted = mlu.tags.playstats.sortPlaybackListByTime(playbackList)

    table = PrettyTable()
    table.field_names = ["AudioFilepath", "Play Time"]
    table.align["AudioFilepath"] = "l"
    table.align["Play Time"] = "r"
    table._max_width = {"AudioFilepath" : 120}

    for playback in playbackListSorted:
        audioFilepathFmt = mlu.utilities.getAudioFilepathWithoutMusicLibraryDir(playback.audioFilepath)
        table.add_row([audioFilepathFmt, playback.playbackDateTime])

    mypycommons.file.writeToFile(filepath, content=table.get_string())

def _savePlaybacksTotalsSummaryOutputFile(filepath, audioFilePlaybackInstancesList):
    playbackInstancesListSorted = mlu.tags.playstats.sortPlaybackInstancesListByAudioFile(audioFilePlaybackInstancesList)

    table = PrettyTable()
    table.field_names = ["AudioFilepath", "Play Count"]
    table.align["AudioFilepath"] = "l"
    table.align["Play Count"] = "r"
    table._max_width = {"AudioFilepath" : 120}

    totalPlays = 0
    oldestTimestamp = mypycommons.time.getTimestampFromFormattedTime("2500-01-01 00:00:00")
    newestTimestamp = mypycommons.time.getTimestampFromFormattedTime("1980-01-01 00:00:00")

    for playbackInstance in audioFilePlaybackInstancesList:
        audioFilepathFmt = mlu.utilities.getAudioFilepathWithoutMusicLibraryDir(playbackInstance.audioFilepath)
        table.add_row([audioFilepathFmt, len(playbackInstance.playbackDateTimes)])

        totalPlays += len(playbackInstance.playbackDateTimes)

        for playbackDateTime in playbackInstance.playbackDateTimes:
            playbackTimestamp = mypycommons.time.getTimestampFromFormattedTime(playbackDateTime)
            if (playbackTimestamp > newestTimestamp):
                newestTimestamp = playbackTimestamp
            if (playbackTimestamp < oldestTimestamp):
                oldestTimestamp = playbackTimestamp
    
    fileLines = []
    fileLines.append("Total plays found for all audio files: {}".format(totalPlays))
    fileLines.append("Play dates range: {} to {}\n".format(mypycommons.time.formatTimestampForDisplay(oldestTimestamp), mypycommons.time.formatTimestampForDisplay(newestTimestamp)))
    fileLines.append(table.get_string())

    mypycommons.file.writeToFile(filepath, content=fileLines)

def _savePlaybacksErrorsSummaryOutputFile(filepath, audioFileErrors, appendToFile=False):
    fileLines = []
    fileLines.append("ERRORS SUMMARY:")
    fileLines.append("The following audio file paths were not found or are invalid")
    for audioFileError in audioFileErrors:
        if (audioFileError.exceptionMessage == mlu.utilities.AudioFileError.NOT_FOUND):
            fileLines.append(audioFileError.audioFilepath)

    fileLines.append("\nThe following audio files are unsupported audio formats ('.flac', '.mp3', '.m4a', and '.opus' (ogg opus) files are supported)")
    for audioFileError in audioFileErrors:
        if (audioFileError.exceptionMessage == mlu.utilities.AudioFileError.NOT_SUPPORTED):
            fileLines.append(audioFileError.audioFilepath)

    fileLines.append("\nThe following audio files encountered other errors (listed in the table below)")
    table = PrettyTable()
    table.field_names = ["AudioFilepath", "Exception Message"]
    table.align["AudioFilepath"] = "l"
    table.align["Exception Message"] = "l"

    for audioFileError in audioFileErrors:
        if (audioFileError.exceptionMessage != mlu.utilities.AudioFileError.NOT_FOUND and audioFileError.exceptionMessage != mlu.utilities.AudioFileError.NOT_SUPPORTED):
            table.add_row([audioFileError.audioFilepath, audioFileError.exceptionMessage])
    fileLines.append(table.get_string())

    mypycommons.file.writeToFile(filepath, content=fileLines, append=appendToFile)

def _saveRunSummaryOutputFile(filepath, numSuccessfulAudioFiles, audioFileErrors):
    fileLines = []
    fileLines.append("SUMMARY:")
    fileLines.append("Playbacks were written successfully for {} audio files\n".format(numSuccessfulAudioFiles))
        
    mypycommons.file.writeToFile(filepath, content=fileLines)
    _savePlaybacksErrorsSummaryOutputFile(filepath, audioFileErrors, appendToFile=True)

if __name__ == "__main__":
    # Set up logger
    mypycommons.logger.configureLoggerWithBasicSettings(__name__, logDir=MLUSettings.logDirectory)
    mypycommons.logger.setLoggerConsoleOutputLogLevel(__name__, 'info')
    mypycommons.logger.setLoggerFileOutputLogLevel(__name__, 'info')
    logger = logging.getLogger(__name__)

    # Backup the MPD Log file
    mpdLogFilepath = MLUSettings.userConfig.mpdLogFilepath
    mpdLogArchiveFilename = '{} {}.backup.7z'.format(
        mypycommons.time.getCurrentTimestampForFilename(), 
        mypycommons.file.getFilename(mpdLogFilepath)
    ) 
    mpdLogArchiveOutFilepath = mypycommons.file.joinPaths(MLUSettings.userConfig.mpdLogBackupDirectory, mpdLogArchiveFilename)

    logger.info("Backing up MPD log file to {}".format(mpdLogArchiveOutFilepath))
    mypycommons.archive.create7zArchive(mpdLogFilepath, mpdLogArchiveOutFilepath)

    # Get the data
    logger.info("Parsing MPD log file for playback data")
    mpdLog = mlu.mpd.log.MPDLog(mpdLogFilepath)
    playbacks = mlu.mpd.plays.getPlaybacksFromMPDLogLines(mpdLog.lines)
    finalPlaybacks = mlu.tags.playstats.removeFalsePlaybacks(playbacks)

    audioFilePlaybackInstancesList = mlu.tags.playstats.convertPlaybackListToAudioFilePlaybackInstancesList(finalPlaybacks)
    audioFiles = [playbackInstance.audioFilepath for playbackInstance in audioFilePlaybackInstancesList]
    audioFileErrors = mlu.utilities.testAudioFilesForErrors(audioFiles)

    # Generate output files 
    logger.info("Writing playbacks data json output file")
    # Write the playbacks json data file - contains the playback data about to be written to tags
    playbacksOutputFilename = '{} playbacks-data.json'.format(mypycommons.time.getCurrentTimestampForFilename())
    playbacksOutputFilepath = mypycommons.file.joinPaths(_getThisScriptCacheDirectory(), playbacksOutputFilename)
    _savePlaybacksOutputFile(playbacksOutputFilepath, audioFilePlaybackInstancesList)

    finishedDataPrompt = False
    while (not finishedDataPrompt):
        # Write the "playbacks parse results" files:
        #   playbacks-history-summary.txt: lists the history of playbacks of audio files as a table, 
        #       listing path and playbackTime, sorting by playbackTime (oldest 1st)
        #
        #   playbacks-totals-summary.txt: lists the total plays found, date range of plays found, and a
        #       table with each audio file and the count of plays found, sorted by audio file
        # 
        #   errors-summary.txt: lists audio files that were 1) not found or 2) were unsupported audio or 
        #       3) had some other error reading/writing info
        #
        logger.info("Writing new 'playbacks parse results' output files")
        playbackParseResultsDir = _getNewPlaybackParseResultsDirectory()

        outputFilename = '{} playbacks-history-summary.txt'.format(mypycommons.time.getCurrentTimestampForFilename())
        outputFilepath = mypycommons.file.joinPaths(playbackParseResultsDir, outputFilename)
        _savePlaybacksHistorySummaryOutputFile(outputFilepath, audioFilePlaybackInstancesList)

        outputFilename = '{} playbacks-totals-summary.txt'.format(mypycommons.time.getCurrentTimestampForFilename())
        outputFilepath = mypycommons.file.joinPaths(playbackParseResultsDir, outputFilename)
        _savePlaybacksTotalsSummaryOutputFile(outputFilepath, audioFilePlaybackInstancesList)

        outputFilename = '{} playbacks-errors-summary.txt'.format(mypycommons.time.getCurrentTimestampForFilename())
        outputFilepath = mypycommons.file.joinPaths(playbackParseResultsDir, outputFilename)
        _savePlaybacksErrorsSummaryOutputFile(outputFilepath, audioFileErrors)

        
        print("See file '{}' for the playback data found, and the summary files in directory '{}' to verify the new playbacks".format(playbacksOutputFilepath, playbackParseResultsDir))
        response = input("Select an option:\n1) Modify the data file ('playbacks-data.json') externally and reload the changes\n2) Keep the data file as-is and write the playbacks to the audio files\nAnswer: ")

        while (response != "1" and response != "2"):
            response = input("Invalid option selected, please enter 1 or 2: ")

        if (response == "1"):
            input("Okay, go to modify the data file ('playbacks-data.json') externally press [Enter] to reload the new data file: ")
            audioFilePlaybackInstancesList = _getAudioFilePlaybackInstancesFromJsonFile(playbacksOutputFilepath)

            audioFiles = [playbackInstance.audioFilepath for playbackInstance in audioFilePlaybackInstancesList]
            audioFileErrors = mlu.utilities.testAudioFilesForErrors(audioFiles)

        elif (response == "2"):
            finishedDataPrompt = True

    logger.info("Writing playstats data to audio files")
    successfulAudioFiles = []
    audioFileErrorList = []
    for audioFilePlaybackInstances in audioFilePlaybackInstancesList:
        try:
            mlu.tags.playstats.writeTagsForAudioFilePlaybackInstances(audioFilePlaybackInstances)
            successfulAudioFiles.append(audioFilePlaybackInstances.audioFilepath)

        except AudioFileNonExistentError:
            audioFileErrorList.append(
                mlu.utilities.AudioFileError(audioFilePlaybackInstances.audioFilepath, mlu.utilities.AudioFileError.NOT_FOUND)
            )

        except AudioFileFormatNotSupportedError:
            audioFileErrorList.append(
                mlu.utilities.AudioFileError(audioFilePlaybackInstances.audioFilepath, mlu.utilities.AudioFileError.NOT_SUPPORTED)
            )

        # catch all other exceptions
        except Exception as e:
            excStr = traceback.format_exc()
            audioFileErrorList.append(
                mlu.utilities.AudioFileError(audioFilePlaybackInstances.audioFilepath, excStr)
            )

    logger.info("Writing run summary output file")
    # Write "run summary" output file
    #   lists audio files that were 1) not found, or 2) were unsupported audio, 3) reading/writing tags 
    #   failed for some other reason (exception message listed)
    outputFilename = '{} run-output-summary.txt'.format(mypycommons.time.getCurrentTimestampForFilename())
    outputFilepath = mypycommons.file.joinPaths(_getThisScriptCacheDirectory(), outputFilename)
    _saveRunSummaryOutputFile(outputFilepath, len(successfulAudioFiles), audioFileErrorList)

    response = input("Would you like to reset the MPD log file? (this is recommended to avoid accidentally re-writing the same playstats) [y/n]: ")
    while (response != "y" and response != "n"):
        response = input("Invalid option selected, please enter y or n: ")
    
    if (response == 'y'):
        logger.info("Resetting MPD log file")
        lastLinePlayback = mlu.mpd.plays.getLastPlaybackMPDLogLine(mpdLog.lines)
        mpdLog.reset(mpdLogLineToPreserve=lastLinePlayback)

    logger.info("Script complete, exiting")