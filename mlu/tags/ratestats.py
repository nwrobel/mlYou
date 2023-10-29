'''
Module that handles ratestat tags (votes, rating) updates.
''' 

import numpy as np
from prettytable import PrettyTable
from typing import List

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.archive
import com.nwrobel.mypycommons.time

import mlu.tags.io
import mlu.tags.common
import mlu.library.playlist
from mlu.settings import MLUSettings

class AudioFileVoteData:
    ''' 
    Data entity class representing the votes for an audio file.
    ''' 
    def __init__(self, filepath, votes):
        self.filepath = filepath
        self.votes = votes

class RatestatTagsUpdater:
    def __init__(self, mluSettings: MLUSettings, commonLogger: mypycommons.logger.CommonLogger):
        if (mluSettings is None):
            raise TypeError("MLUSettings not passed to RatestatTagsUpdater")
        if (commonLogger is None):
            raise TypeError("CommonLogger not passed to RatestatTagsUpdater")

        self.settings = mluSettings
        self.logger = commonLogger.getLogger()
        self.summaryFilepath = self._getSummaryFilepath()

    def processVotePlaylists(self):
        ''' 
        Process the vote playlists directory by using the vote data within to update ratestat
        (votes and rating) tags for the voted on audio files.
        ''' 
        self.logger.info("Copying vote playlist files to project temp dir")
        self._copyVotePlaylistsToTemp()

        self.logger.info("Loading audio file votes data from all vote playlists")
        audioFileVoteDataList = self._getAudioFileVoteDataFromVotePlaylists()

        self.logger.info("Vote playlists data loaded successfully")
        self.logger.info("Writing new ratestats tag data to audio files")

        erroredAudioFilepaths = []
        for audioFileVoteData in audioFileVoteDataList:
            try:
                self._updateRatestatTagsFromVoteData(audioFileVoteData)
            except:
                self.logger.exception("updateRatestatTagsFromVoteData operation failed: File='{}', NewVotes={}".format(audioFileVoteData.filepath, audioFileVoteData.votes))
                erroredAudioFilepaths.append(audioFileVoteData.filepath)

        self.logger.info("Votes processing complete")
        self.logger.info("{} audio files were processed".format(len(audioFileVoteDataList)))
        self.logger.info("{} audio files failed update".format(len(erroredAudioFilepaths)))

        if (not erroredAudioFilepaths):
            self.logger.info("Process completed successfully: all ratestat tags updated with new votes")

        else:
            erroredAudioFilepathsFmt = "\n".join(erroredAudioFilepaths)
            self.logger.info("Failed to update ratestat tag values with new votes for the following files:\n{}".format(erroredAudioFilepathsFmt))
            self.logger.info("Process completed with failures: - these must be fixed manually")

        self.logger.info("Writing ratestat tag updates summary file")
        self._writeSummaryFile(audioFileVoteDataList)
        self.logger.info("Summary file written successfully: File='{}'".format(self.summaryFilepath))

        self.logger.info('Archiving the processed vote playlists')
        self._archiveVotePlaylists()

        self.logger.info('Resetting source vote playlist files')
        self._resetVotePlaylists()

    def _copyVotePlaylistsToTemp(self):
        '''
        Copies the input vote playlists to the project's temp dir
        '''
        sourceVotePlaylists = self._getVotePlaylistFilepaths(self.settings.userConfig.votePlaylistsDir)
        for playlistFile in sourceVotePlaylists:
            mypycommons.file.copyToDirectory(playlistFile, self.settings.tempDir)

    def _getVotePlaylistFilepaths(self, votePlaylistsSrcDir):
        '''
        Returns list of filepaths of the vote playlists
        '''
        playlistFilepaths = []
        possibleVoteValues = self._getPossibleVoteValues()
        for currentVoteValue in possibleVoteValues:
            # Fix to allow use of either m3u or m3u8 extension
            currentVoteValuePlaylistPath = self._getVotePlaylistFilepath(votePlaylistsSrcDir, currentVoteValue)
            playlistFilepaths.append(currentVoteValuePlaylistPath)

        return playlistFilepaths

    def _getVotePlaylistFilepath(self, votePlaylistsSrcDir, currentVoteValue):      
        playlistName = "{}.m3u".format(str(currentVoteValue))
        playlistFilepath =  mypycommons.file.joinPaths(votePlaylistsSrcDir, playlistName)

        if (not mypycommons.file.pathExists(playlistFilepath)):
            playlistName = "{}.m3u8".format(str(currentVoteValue))
            playlistFilepath =  mypycommons.file.joinPaths(votePlaylistsSrcDir, playlistName)

        return playlistFilepath

    def _getPossibleVoteValues(self) -> List[float]:
        '''
        Returns the list of possible vote values: 0.5 to 10, with a step of .5
        '''
        return np.linspace(0.5,10,20)

    def _getAudioFileVoteDataFromVotePlaylists(self) -> List[AudioFileVoteData]:
        '''
        Get the AudioFileVoteData list from the vote playlists (loading the votes for files)
        '''
        audioFileVoteDataList = []
        votePlaylists = self._getVotePlaylistFilepaths(self.settings.tempDir)

        for currentVotePlaylistFilepath in votePlaylists:
            currentVoteValue = float(mypycommons.file.getFileBaseName(currentVotePlaylistFilepath))

            playlistSongs = mlu.library.playlist.getAllPlaylistLines(currentVotePlaylistFilepath)
            self.logger.info("Found {} songs in vote value {} playlist: loading...".format(len(playlistSongs), currentVoteValue))

            for songFilepath in playlistSongs:
                self.logger.debug("Adding to data structure: new vote (value {}) for song '{}'".format(currentVoteValue, songFilepath))

                # Find the current song in the existing vote data, if it's there, and add the vote
                # to the existing vote data object
                currentSongVoteData = [voteData for voteData in audioFileVoteDataList if (voteData.filepath == songFilepath)]
                
                if (currentSongVoteData):
                    currentSongVoteData = currentSongVoteData[0]
                    currentSongVoteData.votes.append(currentVoteValue)
                
                # If there's not an object made for this song, create one with the vote data and 
                # add it to the vote data list
                else:
                    currentSongVoteData = AudioFileVoteData(filepath=songFilepath, votes=[currentVoteValue])
                    audioFileVoteDataList.append(currentSongVoteData)

        allVotedSongsCount = len(audioFileVoteDataList)
        self.logger.info("Vote data loaded from playlists: found {} unique songs that were voted on".format(allVotedSongsCount))

        return audioFileVoteDataList

    def _updateRatestatTagsFromVoteData(self, audioFileVoteData: AudioFileVoteData):
        '''
        Updates the ratestat tags for an audio file, given an AudioFileVoteData object containing the
        new votes to be added.
        '''
        tagHandler = mlu.tags.io.AudioFileMetadataHandler(audioFileVoteData.filepath)
        currentTags = tagHandler.getTags()

        votesCurrent = mlu.tags.common.formatAudioTagToValuesList(currentTags.votes, valuesAsType=float) 
        votesUpdated = votesCurrent + audioFileVoteData.votes
        votesUpdatedTagValue = mlu.tags.common.formatValuesListToAudioTag(votesUpdated)

        newTags = currentTags
        newTags.votes = votesUpdatedTagValue
        newTags.rating = self._calculateRatingTagValue(votesUpdated)
        tagHandler.setTags(newTags)

        self.logger.info("Updated ratestat tags to the following values: File={}, AllVotes={}, NewRating={}".format(audioFileVoteData.filepath, newTags.votes, newTags.rating))

    def _calculateRatingTagValue(self, currentVotes: List[float]) -> str:
        if (currentVotes):
            rating = sum(currentVotes) / len(currentVotes)
            rating = float(rating)
            ratingTagValue = '{0:.1f}'.format(round(rating, 2))
        else:
            ratingTagValue = ''

        return ratingTagValue

    def _writeSummaryFile(self, audioFileVoteDataList: List[AudioFileVoteData]):
        '''
        Writes out a log file containing a table in pretty format with the ratestat tags updates.
        '''
        tagUpdatesTable = PrettyTable()
        tagUpdatesTable.field_names = ["Title", "Artist", "Votes Added", "New Rating", "New Votes List"]
        tagUpdatesTable.align["Title"] = "l"
        tagUpdatesTable.align["Artist"] = "l"
        tagUpdatesTable.align["Votes Added"] = "r"
        tagUpdatesTable.align["New Rating"] = "r"
        tagUpdatesTable.align["New Votes List"] = "r"

        for audioFileVotesData in audioFileVoteDataList:
            tagHandler = mlu.tags.io.AudioFileMetadataHandler(audioFileVotesData.filepath)
            currentTags = tagHandler.getTags()

            votesAdded = mlu.tags.common.formatValuesListToAudioTag(audioFileVotesData.votes)

            tagUpdatesTable.add_row([
                currentTags.title, 
                currentTags.artist, 
                votesAdded,
                currentTags.rating,
                currentTags.votes
            ])

        mypycommons.file.writeToFile(filepath=self.summaryFilepath, content=tagUpdatesTable.get_string())

    def _getSummaryFilepath(self) -> str:
        '''
        Returns the filepath for the ratestat tags updates summary log file
        '''
        backupFilename = "[{}] RatestatTagsUpdater_tag-updates-summary.txt".format(
            mypycommons.time.getCurrentTimestampForFilename()
        )
        filepath = mypycommons.file.joinPaths(self.settings.logDir, backupFilename)
        return filepath

    def _archiveVotePlaylists(self):
        '''
        Create 7z archive of processed vote playlists
        '''
        archiveFilename = "[{}] Archived vote playlists batch.7z".format(
            mypycommons.time.getCurrentTimestampForFilename()
        )

        archiveFilePath = mypycommons.file.joinPaths(self.settings.userConfig.votePlaylistsArchiveDir, archiveFilename)
        playlistFilepaths = self._getVotePlaylistFilepaths(self.settings.tempDir)    

        mypycommons.archive.create7zArchive(inputFilePath=playlistFilepaths, archiveOutFilePath=archiveFilePath)
        self.logger.info("Vote playlists successfully compressed into archive file '{}'".format(archiveFilePath))

    def _resetVotePlaylists(self):
        '''
        Resets the source vote playlist files by removing the playlist entries that were already
        processed
        '''
        sourceVotePlaylistsFilepaths = self._getVotePlaylistFilepaths(self.settings.userConfig.votePlaylistsDir) 
  
        for votePlaylist in sourceVotePlaylistsFilepaths:
            mypycommons.file.clearFileContents(votePlaylist)


