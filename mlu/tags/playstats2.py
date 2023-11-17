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
import mlu.utilities
import mlu.tags.playstats.common 
from mlu.tags.playstats.common import Playback, AudioFilePlaybackList
from mlu.mpd.plays import MpdPlaybackProvider
from mlu.settings import MLUSettings

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

        self._writeOutputFiles(finalPlaybacks, playbackListsFinal, playbackListsExcluded)

    def _writeOutputFiles(self, finalPlaybacks: List[Playback], finalPlaybackLists: List[AudioFilePlaybackList], excludedPlaybackLists: List[AudioFilePlaybackList]) -> None:
        outputDir = self._getNewOutputFilesDir()

        self._logger.info("Writing playbacks data json output files")
        self._savePlaybacksOutputFile(finalPlaybackLists, outputDir)
        self._savePlaybacksExcludesOutputFile(excludedPlaybackLists, outputDir)

        self._logger.info("Writing summary output files")
        self._saveHistorySummaryOutputFile(finalPlaybacks, outputDir)
        self._saveTotalsSummaryOutputFile(finalPlaybackLists, outputDir)


    def _saveHistorySummaryOutputFile(self, playbacks: List[Playback], outputDir) -> None:
        # History file: ordered by playback time
        # title, artist, album, playback time, duration played

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


    def _savePlaybacksOutputFile(self, audioFilePlaybackLists: List[AudioFilePlaybackList], outputDir: str) -> None:
        ''' 
        '''
        outputFilename = 'playbacks.data.json'
        outputFilepath = mypycommons.file.joinPaths(outputDir, outputFilename)

        dictList = []
        for playbackList in audioFilePlaybackLists:
            dictList.append(playbackList.getDictForJsonDataFile())

        mypycommons.file.writeJsonFile(outputFilepath, dictList)

    def _savePlaybacksExcludesOutputFile(self, audioFilePlaybackLists: List[AudioFilePlaybackList], outputDir: str) -> None:
        ''' 
        '''
        outputFilename = 'playbacks-excluded.data.json'
        outputFilepath = mypycommons.file.joinPaths(outputDir, outputFilename)

        dictList = []
        for playbackList in audioFilePlaybackLists:
            dictList.append(playbackList.getDictForJsonExcludesFile())

        mypycommons.file.writeJsonFile(outputFilepath, dictList)

    # def _getLatestPlaybackDataFile(self) -> str:
    #     dataFilepaths = mypycommons.file.getFilesByExtension(self._processOutputDir, '.')
    #     dirFilepath = mypycommons.file.joinPaths(self._processOutputDir, dirName)

    #     if (not mypycommons.file.pathExists(dirFilepath)):
    #         mypycommons.file.createDirectory(dirFilepath)

    #     return dirFilepath  

    # def _archiveMpdLogFile(self) -> None:
    #     ''' 
    #     '''
    #     mpdLogArchiveFilename = '[{}] {}.archive.7z'.format(
    #         mypycommons.time.getCurrentTimestampForFilename(), 
    #         mypycommons.file.getFilename(self.settings.userConfig.mpdLogFilepath)
    #     ) 
    #     mpdLogArchiveOutFilepath = mypycommons.file.joinPaths(MLUSettings.userConfig.mpdLogBackupDirectory, mpdLogArchiveFilename)

    #     logger.info("Archiving MPD log file: {}".format(mpdLogArchiveOutFilepath))
    #     mypycommons.archive.create7zArchive(mpdLogFilepath, mpdLogArchiveOutFilepath)



    