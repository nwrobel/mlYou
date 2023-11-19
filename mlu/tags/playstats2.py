from typing import List, Optional, Tuple
from datetime import timedelta, datetime
from prettytable import PrettyTable
import math 

from com.nwrobel import mypycommons
from com.nwrobel.mypycommons.logger import CommonLogger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.archive
import com.nwrobel.mypycommons.time

import mlu.tags.io
import mlu.tags.common
import mlu.utilities
import mlu.tags.playstats.common 
from mlu.tags.playstats.common import Playback, AudioFilePlaybackList
from mlu.mpd.plays import MpdPlaybackProvider
from mlu.settings import MLUSettings

class PlaystatTags:
    def __init__(self, audioFilepath: str):
        self.audioFilepath = audioFilepath
        self.playCount = 0
        self.dateLastPlayed = None
        self.dateAllPlays = []
        self._handler = mlu.tags.io.AudioFileMetadataHandler(self.audioFilepath)

        self._loadTags()

    def _loadTags(self):
        currentTags = self._handler.getTags()

        # Get values needed
        if (currentTags.playCount):
            self.playCount = int(currentTags.playCount)
        
        if (currentTags.dateLastPlayed):
            self.dateLastPlayed = mypycommons.time.getDateTimeFromFormattedTime(currentTags.dateLastPlayed)
        
        if (currentTags.dateAllPlays):
            currentDateAllPlaysList = mlu.tags.common.formatAudioTagToValuesList(currentTags.dateAllPlays)
            self.dateAllPlays = [mypycommons.time.getDateTimeFromFormattedTime(x) for x in currentDateAllPlaysList]

    def saveTags(self):
        '''
        Write current class values to file, formatted 
        '''
        playCountFmt = str(self.playCount)
        dateLastPlayedFmt = mypycommons.time.formatDatetimeForDisplay(self.dateLastPlayed)

        dateAllPlaysFmtList = [mypycommons.time.formatDatetimeForDisplay(x) for x in self.dateAllPlays]
        dateAllPlaysFmt = mlu.tags.common.formatValuesListToAudioTag(dateAllPlaysFmtList)

        currentTags = self._handler.getTags()
        currentTags.playCount = playCountFmt
        currentTags.dateLastPlayed = dateLastPlayedFmt
        currentTags.dateAllPlays = dateAllPlaysFmt

        self._handler.setTags(currentTags)

class PlaystatTagUpdaterForMpd:
    ''' 
    '''
    def __init__(self, mluSettings: MLUSettings, commonLogger: mypycommons.logger.CommonLogger) -> None:
        if (mluSettings is None):
            raise TypeError("mluSettings not passed")
        if (commonLogger is None):
            raise TypeError("commonLogger not passed")

        self._settings = mluSettings
        self._processOutputDir = self._getProcessOutputDir()
        self._logger = commonLogger.getLogger()

        playbackProvider = MpdPlaybackProvider(mluSettings, commonLogger)
        self._playbacks = playbackProvider.getPlaybacks()
        self._uniqueAudioFiles = mlu.tags.playstats.common.getUniqueAudioFilesFromPlaybacks(self._playbacks)

    def processMpdLogFile(self) -> None:
        ''' 
        '''
        self._logger.info("Testing all found audio files for validity")
        audioFileErrors = mlu.utilities.testAudioFilesForErrors(self._uniqueAudioFiles)

        if (audioFileErrors):
            audioFileErrorLogText = ''
            for audioFileError in audioFileErrors:
                audioFileErrorLogText += "{} ({})\n".format(audioFileError.audioFilepath, audioFileError.exceptionMessage)

            self._logger.error("The following audio files failed validity check:\n{}".format(audioFileErrorLogText))

        self._logger.info("Parsing MPD log file for playback data")
        finalPlaybacks, excludedPlaybacks = self._filterPlaybacks()

        playbackListsFinal = self._convertPlaybacksToAudioFilePlaybackLists(finalPlaybacks)
        playbackListsExcluded = self._convertPlaybacksToAudioFilePlaybackLists(excludedPlaybacks)

        outputDir = self._getNewOutputFilesDir()
        self._logger.info("Writing playbacks data json output files to new dir: {}".format(outputDir))
        self._savePlaybacksOutputFile(finalPlaybackLists, outputDir, 'playbacks.data.json')
        self._savePlaybacksOutputFile(excludedPlaybackLists, outputDir, 'playbacks-excluded.data.json')


    def updatePlaystatTags(self, dataDirName: str) -> None:
        dataDir = mypycommons.file.joinPaths(self._processOutputDir, dataDirName)

        self._logger.info("Loading data file from dir {}".format(dataDir))
        audioFilePlaybackLists = self._loadPlaybacksOutputFile(dataDir, 'playbacks.data.json')

        self._logger.info("Setting playstat tags for {} audio files".format(len(audioFilePlaybackLists)))
        for audioFilePlaybackList in audioFilePlaybackLists:
            self._updatePlaystatTagsForAudioFilePlaybackList(audioFilePlaybackList)

        self._archiveMpdLogFile()
        self._resetMpdLogFile()

        self._logger.info("Writing summary output files for tags written to data dir: {}".format(dataDir))
        self._saveHistorySummaryOutputFile(audioFilePlaybackLists, dataDir)
        self._saveTotalsSummaryOutputFile(audioFilePlaybackLists, dataDir)


    def _archiveMpdLogFile(self) -> None:
        mpdLogArchiveFilename = '[{}] {}.archive.7z'.format(
            mypycommons.time.getCurrentTimestampForFilename(), 
            mypycommons.file.getFilename(self._settings.userConfig.mpdConfig.logFilepath)
        ) 
        mpdLogArchiveOutFilepath = mypycommons.file.joinPaths(self._settings.userConfig.mpdConfig.logArchiveDir, mpdLogArchiveFilename)

        self._logger.info("Archiving MPD log file to: {}".format(mpdLogArchiveOutFilepath))
        mypycommons.archive.create7zArchive(self._settings.userConfig.mpdConfig.logFilepath, mpdLogArchiveOutFilepath)

    def _resetMpdLogFile(self) -> None:
        self._logger.info("Clearing MPD log file: {}".format(self._settings.userConfig.mpdConfig.logFilepath))
        mypycommons.file.clearFileContents(self._settings.userConfig.mpdConfig.logFilepath)

    def _updatePlaystatTagsForAudioFilePlaybackList(self, audioFilePlaybackList: AudioFilePlaybackList) -> None:
        '''
        Alter PLAY_COUNT, DATE_LAST_PLAYED, DATE_ALL_PLAYS
        '''
        playstatTags = PlaystatTags(audioFilePlaybackList.audioFilepath)

        # Set new values
        newPlayCount = playstatTags.playCount + audioFilePlaybackList.getPlaybacksTotal()
        playstatTags.playCount = newPlayCount

        # Last played
        audioFilePlaybackList.playbacks.sort(key=lambda x: x.dateTime)
        dateLastPlayedMpd = audioFilePlaybackList.getPlaybacksDateTimes()[-1] 

        if (not playstatTags.dateLastPlayed):
            playstatTags.dateLastPlayed = dateLastPlayedMpd
        else:
            # If the current date last played is before our latest one from MPD, set our latest
            if (dateLastPlayedMpd > playstatTags.dateLastPlayed):
                playstatTags.dateLastPlayed = dateLastPlayedMpd
            
        # All plays
        newDateAllPlaysList = playstatTags.dateAllPlays
        for playbackDateTime in audioFilePlaybackList.getPlaybacksDateTimes():
            newDateAllPlaysList.append(playbackDateTime)

        newDateAllPlaysList.sort()
        playstatTags.dateAllPlays = newDateAllPlaysList

        self._logger.info("Setting playstat tags for audio file, values: {}, PlayCountAdded={}, NewPlayCount={}, NewDateLastPlayed={}".format(
            audioFilePlaybackList.audioFilepath,
            audioFilePlaybackList.getPlaybacksTotal(),
            playstatTags.playCount,
            mypycommons.time.formatDatetimeForDisplay(playstatTags.dateLastPlayed)
        ))

        playstatTags.saveTags()

    def _saveHistorySummaryOutputFile(self, playbackLists: List[AudioFilePlaybackList], outputDir) -> None:
        # History file: ordered by playback time
        # title, artist, album, playback time, duration played

        playbacks = self._convertAudioFilePlaybackListsToPlaybacks(playbackLists)
        playbacks.sort(key=lambda x: x.dateTime)

        outputFilename = 'summary-playback-history.txt'
        outputFilepath = mypycommons.file.joinPaths(outputDir, outputFilename)

        table = PrettyTable()
        table.field_names = ["Track Title", "Artist", "Album", "Date Played", "Playback Duration"]
        table.align["Track Title"] = "l"
        table.align["Artist"] = "l"
        table.align["Album"] = "l"
        table.align["Date Played"] = "r"
        table.align["Playback Duration"] = "r"
        table._max_width = {
            "Track Title" : 120,
            "Artist": 120,
            "Album": 120
        }

        for playback in playbacks:
            basicTags = self._getAudioFileBasicTags(playback.audioFilepath)
            table.add_row([
                basicTags['title'],
                basicTags['artist'],
                basicTags['album'], 
                mypycommons.time.formatDatetimeForDisplay(playback.dateTime),
                self._getPlaybackDurationFmt(playback.audioFilepath, playback.duration)
            ])

        mypycommons.file.writeToFile(outputFilepath, table.get_string())

    def _getPlaybackDurationFmt(self, audioFilepath: str, playbackDuration: timedelta):
        totalDuration = mlu.tags.playstats.common.getAudioFileDuration(audioFilepath)
        percentOfAudioPlayed = (playbackDuration.total_seconds() / totalDuration.total_seconds()) * 100
        percentFmt = "{:0.0f}".format(percentOfAudioPlayed)

        playbackDuration = timedelta(seconds=math.ceil(playbackDuration.total_seconds()))
        #minutes, seconds = divmod(playbackDuration.seconds, 60)
        #playbackDurationFmt = "{}:{}".format(minutes, seconds)

        return "{} ({}%)".format(str(playbackDuration), percentFmt)



    def _saveTotalsSummaryOutputFile(self, playbackLists: List[AudioFilePlaybackList], outputDir) -> None:
        # Totals file: ordered by play count
        # title, artist, album, play count, times played

        # Sort audio files by play count
        playbackLists.sort(key=lambda x: x.getPlaybacksTotal())

        outputFilename = 'summary-playback-totals.txt'
        outputFilepath = mypycommons.file.joinPaths(outputDir, outputFilename)

        table = PrettyTable()
        table.field_names = ["Track Title", "Artist", "Album", "Play Count", "Dates Played"]
        table.align["Track Title"] = "l"
        table.align["Artist"] = "l"
        table.align["Album"] = "l"
        table.align["Play Count"] = "r"
        table.align["Dates Played"] = "l"
        table._max_width = {
            "Track Title" : 120,
            "Artist": 120,
            "Album": 120
        }

        for audioFilePlaybackList in playbackLists:
            basicTags = self._getAudioFileBasicTags(audioFilePlaybackList.audioFilepath)
            playbackDateTimes = audioFilePlaybackList.getPlaybacksDateTimes()
            playbackDatesFmt = [mypycommons.time.formatDatetimeForDisplay(x) for x in playbackDateTimes]

            table.add_row([
                basicTags['title'],
                basicTags['artist'],
                basicTags['album'], 
                audioFilePlaybackList.getPlaybacksTotal(),
                ", ".join(playbackDatesFmt)
            ])

        mypycommons.file.writeToFile(outputFilepath, table.get_string())

#---------------------------





    def _filterPlaybacks(self) -> Tuple[List[Playback], List[Playback]]:
        '''
        Remove any playbacks in which less than 20% of the song was played.
        '''
        filteredPlaybacks = []
        excludedPlaybacks = []

        for audioFile in self._uniqueAudioFiles:
            thisFileDuration = mlu.tags.playstats.common.getAudioFileDuration(audioFile)
            thisFilePlaybacks = self._getPlaybacksForAudioFile(self._playbacks, audioFile)

            for playback in thisFilePlaybacks:
                percentOfAudioPlayed = (playback.duration.total_seconds() / thisFileDuration.total_seconds()) * 100

                if (percentOfAudioPlayed >= 20):
                    filteredPlaybacks.append(playback)
                else:
                    excludedPlaybacks.append(playback)

        return (filteredPlaybacks, excludedPlaybacks)

    def _getAudioFileBasicTags(self, audioFilepath: str) -> dict:
        handler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
        tags = handler.getTags()

        return {
            'title': tags.title,
            'artist': tags.artist,
            'album': tags.album
        }

    def _convertPlaybacksToAudioFilePlaybackLists(self, playbacks: List[Playback]) -> List[AudioFilePlaybackList]:
        '''
        '''
        audioFilePlaybackLists = []

        for audioFile in self._uniqueAudioFiles:
            thisFilePlaybacks = self._getPlaybacksForAudioFile(playbacks, audioFile)
            if (thisFilePlaybacks):
                audioFilePlaybackLists.append(AudioFilePlaybackList(thisFilePlaybacks))

        return audioFilePlaybackLists

    def _convertAudioFilePlaybackListsToPlaybacks(self, playbackLists: List[AudioFilePlaybackList]) -> List[Playback]:
        '''
        '''
        allPlaybacks = []

        for playbackList in playbackLists:
            for playback in playbackList.playbacks:
                allPlaybacks.append(playback)

        return allPlaybacks

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

    def _getNewOutputFilesDir(self) -> str:
        dirName = '[{}] playback-data-output'.format(mypycommons.time.getCurrentTimestampForFilename())
        dirFilepath = mypycommons.file.joinPaths(self._processOutputDir, dirName)

        if (not mypycommons.file.pathExists(dirFilepath)):
            mypycommons.file.createDirectory(dirFilepath)

        return dirFilepath


    def _savePlaybacksOutputFile(self, audioFilePlaybackLists: List[AudioFilePlaybackList], outputDir: str, outputFilename: str) -> None:
        ''' 
        '''
        outputFilepath = mypycommons.file.joinPaths(outputDir, outputFilename)

        dictList = []
        for playbackList in audioFilePlaybackLists:
            dictList.append(playbackList.getDictForJsonDataFile())

        mypycommons.file.writeJsonFile(outputFilepath, dictList)


    def _loadPlaybacksOutputFile(self, outputDir: str, outputFilename: str) -> List[AudioFilePlaybackList]:
        ''' 
        '''
        outputFilepath = mypycommons.file.joinPaths(outputDir, outputFilename)

        json = mypycommons.file.readJsonFile(outputFilepath)
        audioFilePlaybackLists = []

        for item in json:
            playbacks = []
            playbacksJson = item['playbacks']
            for playbackJson in playbacksJson:
                dateTime = mypycommons.time.getDateTimeFromFormattedTime(playbackJson['dateTime'])
                timeD = mypycommons.time.getTimedeltaFromFormattedDuration(playbackJson['playbackDuration'])
                playbacks.append(
                    Playback(item['audioFilepath'], dateTime, timeD)
                )
            
            audioFilePlaybackLists.append(AudioFilePlaybackList(playbacks))

        return audioFilePlaybackLists

    # def _getLatestPlaybackDataFile(self) -> str:
    #     dataFilepaths = mypycommons.file.getFilesByExtension(self._processOutputDir, '.')
    #     dirFilepath = mypycommons.file.joinPaths(self._processOutputDir, dirName)

    #     if (not mypycommons.file.pathExists(dirFilepath)):
    #         mypycommons.file.createDirectory(dirFilepath)

    #     return dirFilepath  





    