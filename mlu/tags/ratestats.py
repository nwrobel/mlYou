'''
mlu.tags.ratestats

Module containing functionality for the music rating system of the music library. Handles reading 
and setting the 'VOTES' and 'RATING' tags on songs. 
'''

import mutagen

# setup logging for the module using preconfigured MLU logger
import mlu.common.logger
logger = mlu.common.logger.getMLULogger()

import mlu.tags.common

class VoteValueOutOfRange(Exception):
    pass

class SongRatestatTagsHandler:
    '''
    Private class which handles the 'ratestat' tag values for a single audio file and allows
    new, updated values to be calculated. This class also deals with tag value reading from and writing
    to the audio file itself.
    '''
    def __init__(self, songFilepath):
        self.songFilepath = songFilepath
        self.votes = None # list of numbers (int), each representing a vote
        self.rating = None # single float number for the avg vote value
        self.needsRatingUpdate = None # bool as to whether or not this audio file needs its rating tag updated

        # Throw exceptions is the wrong data type is passed in
        if (not isinstance(self.songFilepath, str)):
            raise TypeError("ERROR: SongRatestatTagsHandler - parameter 'songFilepath' must be a string")

        # read in the tag values to populate the fields
        self._readRatestatTags()

    def _readRatestatTags(self):
        '''
        Reads in the current values of all ratestat tags, updating the class instance's fields with
        this data.
        '''
        audioFile = mutagen.File(self.songFilepath)

        try:
            rawVotesTag = audioFile['VOTES']
        except KeyError:
            rawVotesTag = ''

        try:
            rawRatingTag = audioFile['RATING']
        except KeyError:
            rawRatingTag = '0.00'

        try:
            rawNeedRatingUpdateTag = audioFile['NEEDS_RATING_UPDATE']
        except KeyError:
            rawNeedRatingUpdateTag = '0'

        self.votes = mlu.tags.common.formatAudioTagStringToValuesList(rawVotesTag, valuesAsInt=True)
        self.rating = float(rawRatingTag)
        self.needsRatingUpdate = (int(rawNeedRatingUpdateTag) == 1)

        logger.debug("SongRatestatTagsHandler successfully READ ratestat tags for audio file: Path='{}', Votes='{}', Rating='{}', NeedsRatingUpdate='{}'".format(self.songFilepath, self.votes, self.rating, self.needsRatingUpdate))

    def writeRatestatTags(self):
        votesStr = mlu.tags.common.formatValuesListToAudioTagString(self.votes)
        ratingStr = str(round(self.rating, 2)) # round to 2 decimal points

        if (self.needsRatingUpdate):
            needsRatingUpdateStr = '1'
        else:
            needsRatingUpdateStr = '0'

        audioFile = mutagen.File(self.songFilepath)
        audioFile['VOTES'] = votesStr
        audioFile['RATING'] = ratingStr
        audioFile['NEEDS_RATING_UPDATE'] = needsRatingUpdateStr
        audioFile.save()

        logger.debug("SongRatestatTagsHandler successfully WROTE ratestat tags for audio file: Path='{}', Votes='{}', Rating='{}', NeedsRatingUpdate='{}'".format(self.songFilepath, votesStr, ratingStr, needsRatingUpdateStr))
        
    def updateRating(self):
        newAvgRating = sum(self.votes) / len(self.votes)
        self.rating = newAvgRating
        self.needsRatingUpdate = False

    def addVote(self, vote):
        self._validateVote(vote)
        self.votes.append(vote)

    def _validateVote(self, vote):
        if (not isinstance(vote, int)):
            raise TypeError("ERROR: SongRatestatTagsHandler - each value in parameter 'votes' must be type integer")

        if (vote < 1 or vote > 10):
            raise VoteValueOutOfRange("ERROR: SongRatestatTagsHandler - each value in parameter 'votes' must be an integer between (or equal to) 1 and 10")
   

def updateSongRatestatTags(songFilepath, newVote=0):
    songRatestatTagsHandler = SongRatestatTagsHandler(songFilepath)

    if (newVote != 0):
        songRatestatTagsHandler.addVote(newVote)
    songRatestatTagsHandler.updateRating()
    
    songRatestatTagsHandler.writeRatestatTags()