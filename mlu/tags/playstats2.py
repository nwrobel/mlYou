from typing import List, Optional

from com.nwrobel import mypycommons
from com.nwrobel.mypycommons.logger import CommonLogger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.archive
import com.nwrobel.mypycommons.time

import mlu.tags.io
from mlu.mpd.plays import MpdPlaybackProvider
from mlu.settings import MLUSettings

class Playback:
    def __init__(self, audioFilepath, playbackDateTime, playbackDurationSeconds=None):
        self.audioFilepath = audioFilepath
        self.playbackDateTime = playbackDateTime
        self.playbackDurationSeconds = playbackDurationSeconds

    def getDictForJsonFileOutput(self):
        return { 
            'audioFilepath': self.audioFilepath, 
            'playbackDateTime': self.playbackDateTime
        }

class AudioFilePlaybackList:
    def __init__(self, audioFilepath: str, playbackDateTimes: List[str]) -> None:
        self.audioFilepath = audioFilepath

        # Sort the playback times, with oldest first
        playbackDateTimes.sort()
        self.playbackDateTimes = playbackDateTimes

    def getDictForJsonFileOutput(self):
        return {
            'audioFilepath': self.audioFilepath,
            'playbackDateTimes': self.playbackDateTimes
        }

class AudioFileDuration:
    def __init__(self, audioFilepath: str, duration: float) -> None:
        self.audioFilepath = audioFilepath
        self.duration = duration

class PlaystatTagUpdaterForMpd:
    def __init__(self, mpdPlaybackProvider: MpdPlaybackProvider, mluSettings: MLUSettings, commonLogger: CommonLogger) -> None:
        if (mpdPlaybackProvider is None):
            raise TypeError("mpdPlaybackProvider not passed")
        if (mluSettings is None):
            raise TypeError("mluSettings not passed")
        if (commonLogger is None):
            raise TypeError("commonLogger not passed")

        self._playbacks = mpdPlaybackProvider.getPlaybacks()
        self._settings = mluSettings
        self._processCacheDir = self._getProcessCacheDir()
        self._logger = commonLogger.getLogger()

    def processMpdLogFile(self) -> None:
        # Get the data
        self._logger.info("Parsing MPD log file for playback data")
        finalPlaybacks = self._getFilteredPlaybacks()
        playbackInstancesLists = self._convertPlaybacksToAudioFilePlaybackLists(finalPlaybacks)

        audioFiles = [playbackInstancesList.audioFilepath for playbackInstancesList in playbackInstancesLists]
        audioFileErrors = mlu.utilities.testAudioFilesForErrors(audioFiles)

        # Write the playbacks json data file - contains the playback data about to be written to tags
        self._logger.info("Writing playbacks data json output file")
        playbacksOutputFilename = '{} playbacks-data.json'.format(mypycommons.time.getCurrentTimestampForFilename())
        playbacksOutputFilepath = mypycommons.file.joinPaths(self._processCacheDir, playbacksOutputFilename)
        self._savePlaybacksOutputFile(playbacksOutputFilepath, playbackInstancesLists)

    def _getFilteredPlaybacks(self) -> List[Playback]:
        '''
        Remove any playbacks in which less than 20% of the song was played.
        '''
        filteredPlaybackList = []

        # Optimization added:
        # Keep a list of dicts for audioFile durations, to avoid looking up the duration for the same audio file twice
        audioFileDurationList = []

        for playback in self._playbacks:
            thisAudioFileDuration = [
                duration for audioFileDuration in audioFileDurationList if (playback.audioFilepath == audioFileDuration.audioFilepath)
            ]
            
            audioFileDuration = None
            if (thisAudioFileDuration):
                audioFileDuration = thisAudioFileDuration[0].duration
            else:
                audioFileDuration = self._getAudioFileDuration(playback.audioFilepath)
                audioFileDurationList.append(AudioFileDuration(playback.audioFilepath, audioFileDuration))
            
            # If the audio file duration was not found (had an exception), add it to list of kept playbacks anyway
            # The error will be made clear later when attempting to write tags to it  
            if (audioFileDuration):
                percentOfAudioPlayed = 0
                if (playback.playbackDurationSeconds >= audioFileDuration):
                    percentOfAudioPlayed = 100
                else:
                    percentOfAudioPlayed = (playback.playbackDurationSeconds / audioFileDuration) * 100

                if (percentOfAudioPlayed >= 20):
                    filteredPlaybackList.append(playback)
            
            else:
                filteredPlaybackList.append(playback)

        return filteredPlaybackList

    def _getAudioFileDuration(self, audioFilepath: str) -> Optional[float]:
        try:
            handler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
            properties = handler.getProperties()

            return properties.duration

        except (AudioFileFormatNotSupportedError, AudioFileNonExistentError):
            return None

    def _convertPlaybacksToAudioFilePlaybackLists(self, playbacks: List[Playback]) -> List[AudioFilePlaybackList]:
        '''
        '''
        audioFilePlaybackLists = []

        uniqueAudioFiles = set([playback.audioFilepath for playback in playbacks])
        for audioFile in uniqueAudioFiles:
            thisFilePlaybacks = self._getPlaybacksForAudioFile(playbacks, audioFile)
            playbackTimes = [playback.playbackDateTime for playback in thisFilePlaybacks]
            audioFilePlaybackLists.append(AudioFilePlaybackList(audioFile, playbackTimes))

        return audioFilePlaybackLists

    def _getPlaybacksForAudioFile(self, allPlaybacks: List[Playback], audioFilepath: str) -> List[Playback]:
        return [playback for playback in allPlaybacks if (playback.audioFilepath == audioFilepath)]

    def _getProcessCacheDir(self) -> str:
        dirName = "update-playstat-tags-from-mpd-log"
        scriptCacheDir = mypycommons.file.joinPaths(self._settings.cacheDir, dirName)

        if (not mypycommons.file.pathExists(scriptCacheDir)):
            mypycommons.file.createDirectory(scriptCacheDir)

        return scriptCacheDir

    def _savePlaybacksOutputFile(self, filepath: str, audioFilePlaybackLists: List[AudioFilePlaybackList]) -> None:
        dictList = []
        for playbackList in audioFilePlaybackLists:
            dictList.append(playbackList.getDictForJsonFileOutput())

        mypycommons.file.writeJsonFile(filepath, dictList)

    def _archiveMpdLogFile(self) -> None:
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


    