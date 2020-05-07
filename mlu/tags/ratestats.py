'''
mlu.tags.ratestats

First created: ?
Last modified: 01/17/20

Module containing functionality for the music rating system of the music library.

'''

# setup logging for the module using preconfigured MLU logger
import mlu.common.logger
logger = mlu.common.logger.getMLULogger()

import mlu.tags.io
import mlu.tags.common
import mlu.common.file 
import mlu.common.time
import mlu.library.playlist

class AudioFileVoteData:
    def __init__(self, filepath, votes):
        self.filepath = filepath
        self.votes = votes


def updateRatestatTagsFromVoteData(audioFileVoteData):
    '''
    '''
    logger.debug("Updating ratestat tags with new votes: File={}, NewVotes={}".format(audioFileVoteData.filepath, audioFileVoteData.votes))

    tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFileVoteData.filepath)
    currentTags = tagHandler.getTags()

    votesCurrent = mlu.tags.common.formatAudioTagToValuesList(currentTags.votes, valuesAsInt=True) 
    votesUpdated = votesCurrent + audioFileVoteData.votes
    votesUpdatedTagValue = mlu.tags.common.formatValuesListToAudioTag(votesUpdated)

    newTags = currentTags
    newTags.votes = votesUpdatedTagValue
    newTags.rating = _calculateRatingTagValue(votesUpdated)
    tagHandler.setTags(newTags)

    logger.info("Updated ratestat tags to the following values: File={}, Votes={}, Rating={}".format(audioFileVoteData.filepath, newTags.votes, newTags.rating))


def updateRatingTag(audioFilepath):
    '''
    '''
    tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFileVoteData.filepath)
    currentTags = tagHandler.getTags()

    votesCurrent = mlu.tags.common.formatAudioTagToValuesList(currentTags.votes, valuesAsInt=True) 
    ratingCurrent = currentTags.rating
    ratingUpdated = _calculateRatingTagValue(votesCurrent)

    if (ratingCurrent != ratingUpdated):
        newTags = currentTags
        newTags.rating = ratingUpdated
        tagHandler.setTags(newTags)

        logger.info("Rating tag updated with new value: File={}, OldRating={}, NewRating={}".format(audioFilepath, ratingCurrent, ratingUpdated))

    else:
        logger.info("Rating tag not updated, no change needed: File={}".format(audioFilepath))


def getAudioFileVoteDataFromRatePlaylists(playlistsDir):
    '''
    '''
    audioFileVoteDataList = []

    for currentVoteValue in range(1, 11):
        currentVoteValuePlaylistName = "{}.m3u8".format(currentVoteValue)
        currentVoteValuePlaylistPath =  mlu.common.file.JoinPaths(playlistsDir, currentVoteValuePlaylistName)

        logger.info("Reading songs with vote value {} from playlist {}".format(currentVoteValue, currentVoteValuePlaylistPath))
        playlistSongs = mlu.library.playlist.getAllPlaylistLines(currentVoteValuePlaylistPath)
        logger.info("Found {} songs in vote value {} playlist: loading them into the data structure".format(len(playlistSongs), currentVoteValue))

        for songFilepath in playlistSongs:
            logger.debug("Adding new vote (value {}) for song '{}'".format(currentVoteValue, songFilepath))

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
    archiveFilename = "[{}] Archived vote playlists.gz".format(mlu.common.time.getCurrentFormattedTime())
    archiveFilePath = mlu.common.file.JoinPaths(archiveDir, archiveFilename)
    playlistFilepaths = _getVotePlaylistFilepaths(playlistsDir)    

    mlu.common.file.compressFileToArchive(inputFilePath=playlistFilepaths, archiveOutFilePath=archiveFilePath)
    logger.info("Vote playlists successfully compressed into archive file '{}'".format(archiveFilePath))


def resetVotePlaylists(playlistsDir):
    '''
    '''
    playlistFilepaths = _getVotePlaylistFilepaths(playlistsDir)    

    for votePlaylist in playlistFilepaths:
        mlu.common.file.clearFileContents(filePath=votePlaylist)

    logger.info("Vote playlists reset successfully")


def _getVotePlaylistFilepaths(playlistsDir):
    playlistFilepaths = []
    for currentVoteValue in range(1, 11):
        currentVoteValuePlaylistName = "{}.m3u8".format(currentVoteValue)
        currentVoteValuePlaylistPath =  mlu.common.file.JoinPaths(playlistsDir, currentVoteValuePlaylistName)
        playlistFilepaths.append(currentVoteValuePlaylistPath)

    return playlistFilepaths


def _calculateRatingTagValue(votes):
    if (votes):
        rating = sum(votes) / len(votes)
        rating = float(rating)
        ratingTagValue = '{0:.2f}'.format(round(rating, 2))

    else:
        ratingTagValue = ''

    return ratingTagValue