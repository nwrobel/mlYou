from typing import List, Optional, Tuple
from datetime import timedelta, datetime

from com.nwrobel import mypycommons
from com.nwrobel.mypycommons.logger import CommonLogger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.archive
import com.nwrobel.mypycommons.time

import mlu.tags.io
import mlu.utilities
import mlu.tags.playstats.common 
from mlu.tags.playstats.common import Playback, AudioFilePlaybackList
from mlu.mpd.plays import MpdPlaybackProvider
from mlu.settings import MLUSettings

class PlaystatTagUpdaterForMpd:
    ''' 
    '''
    def __init__(self, mpdPlaybackProvider: MpdPlaybackProvider, mluSettings: MLUSettings, commonLogger: CommonLogger) -> None:
        if (mpdPlaybackProvider is None):
            raise TypeError("mpdPlaybackProvider not passed")
        if (mluSettings is None):
            raise TypeError("mluSettings not passed")
        if (commonLogger is None):
            raise TypeError("commonLogger not passed")

        self._playbacks = mpdPlaybackProvider.getPlaybacks()
        self._uniqueAudioFiles = mlu.tags.playstats.common.getUniqueAudioFilesFromPlaybacks(self._playbacks)
        self._settings = mluSettings
        self._processOutputDir = self._getProcessOutputDir()
        self._logger = commonLogger.getLogger()

    def processMpdLogFile(self) -> None:
        ''' 
        '''
        self._logger.info("Testing all found audio files for validity")
        audioFileErrors = mlu.utilities.testAudioFilesForErrors(self._uniqueAudioFiles)

        self._logger.info("Parsing MPD log file for playback data")
        finalPlaybacks, excludedPlaybacks = self._filterPlaybacks()

        playbackListsFinal = self._convertPlaybacksToAudioFilePlaybackLists(finalPlaybacks)
        playbackListsExcluded = self._convertPlaybacksToAudioFilePlaybackLists(excludedPlaybacks)

        self._logger.info("Writing playbacks data json output files")
        filenameTimestamp = mypycommons.time.getCurrentTimestampForFilename()
        self._savePlaybacksOutputFile(playbackListsFinal, filenameTimestamp)
        self._savePlaybacksExcludesFile(playbackListsExcluded, filenameTimestamp)

    def writeSummaryFiles(self) -> None:
        ''' 
        '''

        logger.info("Writing summary files ")
        summaryDir = self._getNewSummaryFileDir()

        outputFilename = '{} playbacks-history-summary.txt'.format(mypycommons.time.getCurrentTimestampForFilename())
        outputFilepath = mypycommons.file.joinPaths(playbackParseResultsDir, outputFilename)
        _savePlaybacksHistorySummaryOutputFile(outputFilepath, audioFilePlaybackInstancesList)

        outputFilename = '{} playbacks-totals-summary.txt'.format(mypycommons.time.getCurrentTimestampForFilename())
        outputFilepath = mypycommons.file.joinPaths(playbackParseResultsDir, outputFilename)
        _savePlaybacksTotalsSummaryOutputFile(outputFilepath, audioFilePlaybackInstancesList)

        outputFilename = '{} playbacks-errors-summary.txt'.format(mypycommons.time.getCurrentTimestampForFilename())
        outputFilepath = mypycommons.file.joinPaths(playbackParseResultsDir, outputFilename)
        _savePlaybacksErrorsSummaryOutputFile(outputFilepath, audioFileErrors)


    def _filterPlaybacks(self) -> Tuple[List[Playback], List[Playback]]:
        '''
        Remove any playbacks in which less than 20% of the song was played.
        '''
        filteredPlaybacks = []
        excludedPlaybacks = []

        for audioFile in self._uniqueAudioFiles:
            thisFileDuration = self._getAudioFileDuration(audioFile)
            thisFilePlaybacks = self._getPlaybacksForAudioFile(self._playbacks, audioFile)

            for playback in thisFilePlaybacks:
                percentOfAudioPlayed = (playback.duration.total_seconds() / thisFileDuration.total_seconds()) * 100

                if (percentOfAudioPlayed >= 20):
                    filteredPlaybacks.append(playback)
                else:
                    excludedPlaybacks.append(playback)

        return (filteredPlaybacks, excludedPlaybacks)

    def _getAudioFileDuration(self, audioFilepath: str) -> timedelta:
        ''' 
        '''
        handler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
        properties = handler.getProperties()

        return properties.duration

    def _convertPlaybacksToAudioFilePlaybackLists(self, playbacks: List[Playback]) -> List[AudioFilePlaybackList]:
        '''
        '''
        audioFilePlaybackLists = []

        for audioFile in self._uniqueAudioFiles:
            thisFilePlaybacks = self._getPlaybacksForAudioFile(playbacks, audioFile)
            if (thisFilePlaybacks):
                audioFilePlaybackLists.append(AudioFilePlaybackList(thisFilePlaybacks))

        return audioFilePlaybackLists

    def _getPlaybacksForAudioFile(self, allPlaybacks: List[Playback], audioFilepath: str) -> List[Playback]:
        ''' 
        '''        
        return [playback for playback in allPlaybacks if (playback.audioFilepath == audioFilepath)]

    def _getProcessOutputDir(self) -> str:
        ''' 
        '''
        dirName = "update-playstat-tags-from-mpd-log"
        scriptCacheDir = mypycommons.file.joinPaths(self._settings.cacheDir, dirName)

        if (not mypycommons.file.pathExists(scriptCacheDir)):
            mypycommons.file.createDirectory(scriptCacheDir)

        return scriptCacheDir

    def _getNewSummaryFileDir(self) -> str:
        dirName = '[{}] playback-data-summary'.format(mypycommons.time.getCurrentTimestampForFilename())
        dirFilepath = mypycommons.file.joinPaths(self._processOutputDir, dirName)

        if (not mypycommons.file.pathExists(dirFilepath)):
            mypycommons.file.createDirectory(dirFilepath)

        return dirFilepath

    def _getLatestPlaybackDataFile(self) -> str:
        dataFilepaths = mypycommons.file.getFilesByExtension(self._processOutputDir, '.')
        dirFilepath = mypycommons.file.joinPaths(self._processOutputDir, dirName)

        if (not mypycommons.file.pathExists(dirFilepath)):
            mypycommons.file.createDirectory(dirFilepath)

        return dirFilepath  

    def _savePlaybacksOutputFile(self, audioFilePlaybackLists: List[AudioFilePlaybackList], filenameTimestamp: str) -> None:
        ''' 
        '''
        outputFilename = '[{}] playbacks-data.json'.format(filenameTimestamp)
        outputFilepath = mypycommons.file.joinPaths(self._processCacheDir, outputFilename)

        dictList = []
        for playbackList in audioFilePlaybackLists:
            dictList.append(playbackList.getDictForJsonDataFile())

        mypycommons.file.writeJsonFile(outputFilepath, dictList)

    def _savePlaybacksExcludesFile(self, audioFilePlaybackLists: List[AudioFilePlaybackList], filenameTimestamp: str) -> None:
        ''' 
        '''
        outputFilename = '[{}] playbacks-excluded.json'.format(filenameTimestamp)
        outputFilepath = mypycommons.file.joinPaths(self._processCacheDir, outputFilename)

        dictList = []
        for playbackList in audioFilePlaybackLists:
            dictList.append(playbackList.getDictForJsonExcludesFile())

        mypycommons.file.writeJsonFile(outputFilepath, dictList)

    def _archiveMpdLogFile(self) -> None:
        ''' 
        '''
        mpdLogArchiveFilename = '[{}] {}.archive.7z'.format(
            mypycommons.time.getCurrentTimestampForFilename(), 
            mypycommons.file.getFilename(self.settings.userConfig.mpdLogFilepath)
        ) 
        mpdLogArchiveOutFilepath = mypycommons.file.joinPaths(MLUSettings.userConfig.mpdLogBackupDirectory, mpdLogArchiveFilename)

        logger.info("Archiving MPD log file: {}".format(mpdLogArchiveOutFilepath))
        mypycommons.archive.create7zArchive(mpdLogFilepath, mpdLogArchiveOutFilepath)











# def convertAudioFilePlaybackInstancesListToPlaybackList(audioFilePlaybackInstancesList):
#     playbackList = []
#     for playbackInstance in audioFilePlaybackInstancesList:
#         for playbackDateTime in playbackInstance.playbackDateTimes:
#             playbackList.append(
#                 Playback(playbackInstance.audioFilepath, playbackDateTime)
#             )
#     return playbackList

# def sortPlaybackListByTime(playbackList):
#     playbackList.sort(key=lambda playback: playback.playbackDateTime)
#     return playbackList

# def sortPlaybackInstancesListByAudioFile(audioFilePlaybackInstancesList):
#     audioFilePlaybackInstancesList.sort(key=lambda playbackInstance: playbackInstance.audioFilepath)
#     return audioFilePlaybackInstancesList

# def writeTagsForAudioFilePlaybackInstances(audioFilePlaybackInstances):
#     '''
#     Alter PLAY_COUNT, DATE_LAST_PLAYED, DATE_ALL_PLAYS
#     '''
#     handler = AudioFileMetadataHandler(audioFilePlaybackInstances.audioFilepath)
#     currentTags = handler.getTags()

#     # Get values needed
#     if (currentTags.playCount):
#         currentPlayCount = int(currentTags.playCount)
#     else:
#         currentPlayCount = 0
    
#     if (currentTags.dateLastPlayed):
#         currentDateLastPlayed = currentTags.dateLastPlayed
#     else:
#         currentDateLastPlayed = ""
    
#     if (currentTags.dateAllPlays):
#         currentDateAllPlaysList = mlu.tags.common.formatAudioTagValueToValuesList(currentTags.dateAllPlays)
#     else:
#         currentDateAllPlaysList = []

#     # Set new values
#     newPlayCount = currentPlayCount + len(audioFilePlaybackInstances.playbackDateTimes)
#     # get last play time in the list (list is sorted already)
#     newDateLastPlayed = audioFilePlaybackInstances.playbackDateTimes[-1] 
 
#     newDateAllPlaysList = currentDateAllPlaysList
#     for playbackDateTime in audioFilePlaybackInstances.playbackDateTimes:
#         newDateAllPlaysList.append(playbackDateTime)
#     newDateAllPlaysList.sort()

#     # Check if the original last played tag value is newer than the last played value from the new playbackInstance
#     # If it is, keep the last played tag what it currently is set as
#     if (currentDateLastPlayed):
#         currentLastPlayedTimestamp = mypycommons.time.getTimestampFromFormattedTime(currentDateLastPlayed)
#         newLastPlayedTimestamp = mypycommons.time.getTimestampFromFormattedTime(newDateLastPlayed)
#         if (currentLastPlayedTimestamp > newLastPlayedTimestamp):
#             newDateLastPlayed = currentDateLastPlayed

#     # Set new values on the tags
#     currentTags.playCount = str(newPlayCount)
#     currentTags.dateLastPlayed = newDateLastPlayed
#     currentTags.dateAllPlays = mlu.tags.common.formatValuesListToAudioTagValue(newDateAllPlaysList)

#     handler.setTags(currentTags)
    
# def writeTagsForNewPlayback(audioFilepath, playbackDateTime):
#     '''
#     '''
#     playbackInstances = AudioFilePlaybackInstances(audioFilepath, [playbackDateTime])
#     writeTagsForAudioFilePlaybackInstances(playbackInstances)


    