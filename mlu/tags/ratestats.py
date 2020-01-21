'''
mlu.tags.ratestats

First created: ?
Last modified: 01/17/20

Module containing functionality for the music rating system of the music library. Handles reading 
and setting the following tags for audio files:
- VOTES
- RATING
- NEEDS_RATING_UPDATE

'''

# TODO: 
# Test to see what happens when an audio file has no tag of name set at all: Does this make a KeyError,
# or will it be a null value?

import mutagen

# setup logging for the module using preconfigured MLU logger
import mlu.common.logger
logger = mlu.common.logger.getMLULogger()

from mlu.tags.base import SongTagsHandler

class SongRatestatTags:
    '''
    Simple container class that is used to pass around ratestat song tags to external code. The
    SongRatestatTagsHandler returns this object type when .getTags() is called.
    '''
    def __init__(self, songFilepath, votes, rating, needsRatingUpdate):
        self.songFilepath = songFilepath
        self.votes = votes
        self.rating = rating
        self.needsRatingUpdate = needsRatingUpdate


class SongRatestatTagsHandler(SongTagsHandler):
    '''
    Public class which handles the 'ratestat' tag values for a single audio file and allows
    new, updated values to be calculated. This class also deals with tag value reading from and writing
    to the audio file itself.
    '''
    def __init__(self, songFilepath):
        # base tag handler class enforces that songFilepath must be set: pass songFilepath to
        # the base class to have it set there (and also here in the child class)
        super().__init__(songFilepath)

        self._votes = None # list of numbers (int), each representing a vote
        self._rating = None # single float number for the avg vote value
        self._needsRatingUpdate = None # bool as to whether or not this audio file needs its rating tag updated

        # read in the tag values to populate the fields
        self.readTags()


    def readTags(self):
        '''
        Reads in the current values of all ratestat tags, updating the class instance's fields with
        this data.
        '''
        audioFile = mutagen.File(self._songFilepath)

        # Read VOTES tag
        rawVotesTag = audioFile['VOTES'][0]
        if (not rawVotesTag):
            logger.debug("Tag value 'VOTES' is empty for song '{}': tag handler will use value '[]'".format(self._songFilepath))
            self._votes = []
        else:
            self._votes = mlu.tags.common.formatAudioTagToValuesList(rawVotesTag, valuesAsInt=True)
        
        # Read RATING tag
        rawRatingTag = audioFile['RATING'][0]
        if (not rawRatingTag):
            logger.debug("Tag value 'RATING' is empty for song '{}': tag handler will use value '0'".format(self._songFilepath))
            self._rating = 0
        else:
            self._rating = float(rawRatingTag)

        # Read NEEDS_RATING_UPDATE tag
        rawNeedRatingUpdateTag = audioFile['NEEDS_RATING_UPDATE'][0]
        if (rawNeedRatingUpdateTag):
            logger.debug("Tag value 'NEEDS_RATING_UPDATE' is empty for song '{}': tag handler will use value 'False'".format(self._songFilepath))
            self._needsRatingUpdate = False
        else:
            self._needsRatingUpdate = (int(rawNeedRatingUpdateTag) == 1)

        logger.debug("Successfully READ ratestat tags for audio file: Path='{}', Votes='{}', Rating='{}', NeedsRatingUpdate='{}'".format(self._songFilepath, self._votes, self._rating, self._needsRatingUpdate))


    def writeTags(self):

        if (not self._tagsHaveBeenSet):
            raise Exception("Cannot write ratestat tags: tag values have not yet been set for audio file '{}': call setTags() first before writing new tag values".format(self._songFilepath))

        audioFile = mutagen.File(self._songFilepath)

        # Write VOTES tag
        # Form the tag value string (seperated by ;) from the votes list
        rawVotesTag = mlu.tags.common.formatValuesListToAudioTag(self._votes)
        audioFile['VOTES'] = rawVotesTag

        # Write the RATING tag
        # round rating float value to 2 decimal points and always show 2 decimal places
        rawRatingTag = '{0:.2f}'.format(round(self._rating, 2)) 
        audioFile['RATING'] = rawRatingTag

        # Write the NEEDS_RATING_UPDATE tag
        # NeedsRatingUpdate flag should not be set: if it is, tags need to be updated (exception)
        # If it's not set, good: the tag value for this flag will be 0
        if (self._needsRatingUpdate):
            raise Exception("Cannot write ratestat tags to audio file: 'needsRatingUpdate' instance variable is true despite tags having been set")
        else:
            rawNeedRatingUpdateTag = '0'
        audioFile['NEEDS_RATING_UPDATE'] = rawNeedRatingUpdateTag

        audioFile.save()
        logger.debug("Successfully WROTE ratestat tags for audio file: Path='{}', Votes='{}', Rating='{}', NeedsRatingUpdate='{}'".format(self._songFilepath, self._votes, self._rating, self._needsRatingUpdate))


    def getTags(self):
        '''
        Returns a SongRatestatTags object, which holds the song filepath as well as the current basic 
        tag values for the song represented by this SongBasicTagsHandler instance.
        '''
        return SongRatestatTags(
            songFilepath=self._songFilepath,
            votes=self._votes,
            rating=self._rating,
            needsRatingUpdate=self._needsRatingUpdate
        )


    def updateTags(self, newVote=None):
        '''
        Allows the ratestat tags to be updated for this song. This only updates the current values
        saved in this handler instance: the changes are not written to the file until calling writeTags().

        The only changes allowed to the public through this method are the addition of a vote value.
        Validation of the given vote performed and an exception will be thrown if it fails this 
        validation checking.

        Calling updateTags() with a newVote value will add that vote to the votes tag, update the 
        rating tag with the newly computed avg. vote value, and set the needsRatingUpdate tag to 0.

        Calling updateTags() alone with no vote value will do the same, except no vote will be added
        to the votes tag. Rating and needsRatingUpdate tag will still be updated, however.
 
        Params:
            newVote: (int) the new vote to add to the ratestat tags - omit this parameter to update
                tags only without adding a new vote
        '''
        if (newVote is not None):
            self._updateVotes(newVote)
            
        self._updateRating()

        self._tagsHaveBeenSet = True
        logger.debug("Successfully UPDATED tag values for SongRatestatTagsHandler instance: Path='{}', Title='{}', Artist='{}', Album='{}'".format(self._songFilepath, self._votes, self._rating, self._needsRatingUpdate))


    def _updateVotes(self, newVote):
        self._validateTagValues(newVote)
        self._votes.append(newVote)

    def _updateRating(self):
        if (self._votes):
            newAvgRating = sum(self._votes) / len(self._votes)
        else:
            newAvgRating = 0
        
        self._rating = newAvgRating
        self._needsRatingUpdate = False


    def _validateTagValues(self, newVote):
        if (not isinstance(newVote, int)):
            raise TypeError("Each vote item in class attribute 'votes' must be type integer")

        if (newVote < 1 or newVote > 10):
            raise ValueError("Each vote item in class attribute 'votes' must be an integer value ranging from 1 to 10 (inclusive)")