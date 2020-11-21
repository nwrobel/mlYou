'''
mlu.tags.ratestats

Module containing functionality for the music rating system of the music library.

'''
import numpy as np

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

logger = mypycommons.logger.getSharedLogger()

import mlu.tags.io
import mlu.tags.common
import mlu.library.playlist

class AudioFileVoteData:
    def __init__(self, filepath, votes):
        self.filepath = filepath
        self.votes = votes

class UpdateRatingTagResult:
    def __init__(self, audioFilepath, wasUpdated, oldRating, newRating):
        self.audioFilepath = audioFilepath,
        self.wasUpdated = wasUpdated
        self.oldRating = oldRating
        self.newRating = newRating


def updateRatestatTagsFromVoteData(audioFileVoteData):
    '''
    Updates the ratestat tags for an audio file, given an AudioFileVoteData object containing the
    new votes to be added.
    '''
    logger.debug("Updating ratestat tags with new votes: File={}, NewVotes={}".format(audioFileVoteData.filepath, audioFileVoteData.votes))

    tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFileVoteData.filepath)
    currentTags = tagHandler.getTags()

    votesCurrent = mlu.tags.common.formatAudioTagToValuesList(currentTags.votes, valuesAs='float') 
    votesUpdated = votesCurrent + audioFileVoteData.votes
    votesUpdatedTagValue = mlu.tags.common.formatValuesListToAudioTag(votesUpdated)

    newTags = currentTags
    newTags.votes = votesUpdatedTagValue
    newTags.rating = _calculateRatingTagValue(votesUpdated)
    tagHandler.setTags(newTags)

    logger.info("Updated ratestat tags to the following values: File={}, Votes={}, Rating={}".format(audioFileVoteData.filepath, newTags.votes, newTags.rating))


def updateRatingTag(audioFilepath):
    '''
    If needed, updates the rating tag value for an audio file by calculating the average of all the existing
    vote values in the file's 'votes' tag. Returns true if an update was needed and performed (rating
    corrected).
    '''
    tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFilepath)
    currentTags = tagHandler.getTags()

    votesCurrent = mlu.tags.common.formatAudioTagToValuesList(currentTags.votes, valuesAs='float') 
    ratingCurrent = currentTags.rating
    ratingUpdated = _calculateRatingTagValue(votesCurrent)

    wasUpdated = False
    if (ratingCurrent != ratingUpdated):
        newTags = currentTags
        newTags.rating = ratingUpdated
        tagHandler.setTags(newTags)

        logger.info("Rating tag updated with new value: File={}, OldRating={}, NewRating={}".format(audioFilepath, ratingCurrent, ratingUpdated))
        wasUpdated = True

    else:
        logger.debug("Rating tag not updated, no change needed: File={}".format(audioFilepath))

    return UpdateRatingTagResult (
        audioFilepath=audioFilepath,
        wasUpdated=wasUpdated,
        oldRating=ratingCurrent,
        newRating=ratingUpdated
    )

def getAudioFileVoteDataFromRatePlaylists(votePlaylistsDir):
    '''
    '''
    audioFileVoteDataList = []
    votePlaylists = _getVotePlaylistFilepaths(votePlaylistsDir)

    for currentVotePlaylistFilepath in votePlaylists:
        currentVoteValue = float(mypycommons.file.GetFileBaseName(currentVotePlaylistFilepath))

        logger.info("Reading songs with vote value {} from playlist {}".format(currentVoteValue, currentVotePlaylistFilepath))
        playlistSongs = mlu.library.playlist.getAllPlaylistLines(currentVotePlaylistFilepath)
        logger.info("Found {} songs in vote value {} playlist: loading them into the data structure".format(len(playlistSongs), currentVoteValue))

        for songFilepath in playlistSongs:
            logger.debug("Adding to data structure: new vote (value {}) for song '{}'".format(currentVoteValue, songFilepath))

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
    logger.info("Vote data loaded from playlists: found {} unique songs that were voted on".format(allVotedSongsCount))

    return audioFileVoteDataList

def archiveVotePlaylists(playlistsDir, archiveDir):
    '''
    '''
    timeForFilename = (mypycommons.time.getCurrentFormattedTime()).replace(':', '_')
    archiveFilename = "[{}] Archived vote playlists batch.7z".format(timeForFilename)

    archiveFilePath = mypycommons.file.JoinPaths(archiveDir, archiveFilename)
    playlistFilepaths = _getVotePlaylistFilepaths(playlistsDir)    

    mypycommons.file.create7zArchive(inputFilePath=playlistFilepaths, archiveOutFilePath=archiveFilePath)
    logger.info("Vote playlists successfully compressed into archive file '{}'".format(archiveFilePath))


def resetVotePlaylists(votePlaylistsSourceDir, votePlaylistsTempDir):
    '''
    '''
    processedVotePlaylistsFilepaths = _getVotePlaylistFilepaths(votePlaylistsTempDir)    
    processedVotePlaylistsLineCounts = {}

    for votePlaylist in processedVotePlaylistsFilepaths:
        votePlaylistName = mypycommons.file.GetFilename(votePlaylist)
        lineCount = mypycommons.file.getTextFileLineCount(votePlaylist)
        processedVotePlaylistsLineCounts[votePlaylistName] = lineCount

    sourceVotePlaylistsFilepaths = _getVotePlaylistFilepaths(votePlaylistsSourceDir) 

    # Remove from the start of each of the original vote playlists the number of lines that were 
    # processed in the playlists from the temp dir earlier - essentially we remove the lines that
    # have been processed already, leaving behind any new playlist lines that may have been created
    # in the time between when the playlists were first copied to temp and now  
    for votePlaylist in sourceVotePlaylistsFilepaths:
        votePlaylistName = mypycommons.file.GetFilename(votePlaylist)
        removeFirstNLines = processedVotePlaylistsLineCounts[votePlaylistName]
        mypycommons.file.removeFirstNLinesFromTextFile(votePlaylist, removeFirstNLines)

    logger.info("Vote playlists reset successfully")

def copyVotePlaylistsToTemp(votePlaylistsSourceDir, votePlaylistsTempDir):
    sourceVotePlaylists = _getVotePlaylistFilepaths(votePlaylistsSourceDir)
    mypycommons.file.CopyFilesToDirectory(sourceVotePlaylists, votePlaylistsTempDir)

def _getVotePlaylistFilepaths(playlistsDir):
    playlistFilepaths = []
    possibleVoteValues = np.linspace(0.5,10,20)
    for currentVoteValue in possibleVoteValues:
        currentVoteValuePlaylistName = "{}.m3u".format(str(currentVoteValue))
        currentVoteValuePlaylistPath =  mypycommons.file.JoinPaths(playlistsDir, currentVoteValuePlaylistName)
        playlistFilepaths.append(currentVoteValuePlaylistPath)

    return playlistFilepaths

def _calculateRatingTagValue(votes):
    if (votes):
        rating = sum(votes) / len(votes)
        rating = float(rating)
        ratingTagValue = '{0:.1f}'.format(round(rating, 2))

    else:
        ratingTagValue = ''

    return ratingTagValue