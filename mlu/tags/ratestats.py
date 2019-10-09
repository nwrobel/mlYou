'''
mlu.tags.ratestats

Module containing functionality for the music rating system of the music library. Handles reading 
and setting the 'VOTES' and 'RATING' tags on songs. 
'''

import mutagen

# setup logging for this script using MLU preconfigured logger
import mlu.common.logger
logger = mlu.common.logger.getMLULogger()

import mlu.tags.common
import mlu.library.musiclib

class VoteValueOutOfRange(Exception):
    pass

class _SongRatestatTags:
    '''
    Private class which represents the values of the "rating" tags for a single audio file and allows
    new, updated values to be calculated. This class does not deal with reading from or writing
    to the file itself.
    '''
    def __init__(self, songFilepath, votes, rating):
        self.songFilepath = songFilepath
        self.votes = votes # list of numbers (int), each representing a vote
        self.rating = rating # single float number for the avg vote value

        # Throw exceptions is the wrong data types are passed in
        if (not isinstance(self.songFilepath, str)):
            raise TypeError("ERROR: _SongRatestatTags - parameter 'songFilepath' must be a string")

        if ( (not self.votes) or (not isinstance(self.votes, list)) ):
            raise TypeError("ERROR: _SongRatestatTags - parameter 'votes' must be a list of integers")

        for vote in self.votes:
            self.validateVote(vote)

        if ( (not isinstance(self.rating, int)) and (not isinstance(self.rating, float)) ):
            raise TypeError("ERROR: _SongRatestatTags - parameter 'rating' must an integer or float numeric value")        

    def updateRating(self):
        newAvgRating = sum(self.votes) / len(self.votes)
        self.rating = newAvgRating

    def addVote(self, vote):
        self.validateVote(vote)
        self.votes.append(vote)

    def validateVote(self, vote):
        if (not isinstance(vote, int)):
            raise TypeError("ERROR: _SongRatestatTags - each value in parameter 'votes' must be type integer")

        if (vote < 1 or vote > 10):
            raise VoteValueOutOfRange("ERROR: _SongRatestatTags - each value in parameter 'votes' must be an integer between (or equal to) 1 and 10")


def _readSongRatestatTags(songFilepath):
    audioFile = mutagen.File(songFilepath)
    votesList = mlu.tags.common.formatAudioTagStringToValuesList(audioFile['VOTES'], valuesAsInt=True)
    ratingFloat = float(audioFile['RATING'])

    ratestatTags = _SongRatestatTags(
        songFilepath=songFilepath,
        votes=votesList,
        rating=ratingFloat  
    ) 

    logger.debug("Ratestat tags read successfully from audio file: Name={}, Votes={}, Rating={}".format(ratestatTags.songFilepath, ratestatTags.votes, ratestatTags.rating))
    return ratestatTags

def _writeSongRatestatTags(songRatestatTags):
    ratingRoundedStr = str(round(songRatestatTags.rating, 2))
    votesStr = mlu.tags.common.formatValuesListToAudioTagString(songRatestatTags.votes)

    audioFile = mutagen.File(songRatestatTags.songFilepath)
    audioFile['VOTES'] = votesStr
    audioFile['RATING'] = ratingRoundedStr
    audioFile.save()

    logger.debug("Ratestat tags written to audio file successfully: Name={}, Votes={}, Rating={}".format(songRatestatTags.songFilepath, votesStr, ratingRoundedStr))
    

def updateSongRatestatTags(songFilepath, newVote=0):
    ratestatTags = _readSongRatestatTags(songFilepath)
    
    if (newVote != 0):
        ratestatTags.addVote(newVote)

    ratestatTags.updateRating()
    _writeSongRatestatTags(ratestatTags)
    

def updateAvgRatingForAllLibrarySongs(libraryRootPath):
    logger.info("Searching for all audio under music library root path {}".format(libraryRootPath))
    librarySongs = mlu.library.musiclib.getAllSongFilepathsInLibrary(libraryRootPath)
    logger.info("Found {} audio files in music library root path".format(len(librarySongs)))

    logger.info("Finding audio files that need rating tag updated")
    songsNeedRatingUpdate = []
    for songFilepath in librarySongs:
        audioFile = mutagen.File(songFilepath)
        needsRatingUpdate = int(audioFile['NEEDS_RATING_UPDATE'])

        if (needsRatingUpdate == 1):
            logger.info("Found file flagged for rating update: {}".format(songFilepath))
            songsNeedRatingUpdate.append(songFilepath)

    
    logger.info("Found {} audio files that need rating tag updated...performing updates now".format(len(songsNeedRatingUpdate)))
    for songFilepath in songsNeedRatingUpdate:
        updateSongRatestatTags(songFilepath)

    logger.info("Rating tag update process completed successfully")




