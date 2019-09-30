'''
mlu.tags.ratestats

Module containing functionality for the music rating system of the music library. Handles reading 
and setting the 'VOTES' and 'RATING' tags on songs. 
'''

import mutagen

import mlu.tags.common

# Class representing the data structure holding the various tag values of a song for the playstats tags
# that we are dealing with - 3 tags: PLAY_COUNT, TIME_LAST_PLAYED, ALL_TIMES_PLAYED
class SongRatestatTags:
    def __init__(self, songFilepath, votes, rating):
        self.songFilepath = songFilepath
        self.votes = votes # list of numbers (int), each representing a vote
        self.rating = rating # single float number for the avg vote value

        # Throw exceptions is the wrong data types are passed in
        if (not isinstance(self.songFilepath, str)):
            raise TypeError("ERROR: SongRatestatTags - parameter 'songFilepath' must be a string")

        if ( (not self.votes) or (not isinstance(self.votes, list)) ):
            raise TypeError("ERROR: SongRatestatTags - parameter 'votes' must be a list of integers")

        for vote in self.votes:
            self.validateVote(vote)

        if ( (not isinstance(self.rating, int)) and (not isinstance(self.rating, float)) ):
            raise TypeError("ERROR: SongRatestatTags - parameter 'rating' must an integer or float numeric value")        

    def updateRating(self):
        newAvgRating = sum(self.votes) / len(self.votes)
        self.rating = newAvgRating

    def addVote(self, vote):
        self.validateVote(vote)
        self.votes.append(vote)

    def validateVote(self, vote):
        if (not isinstance(vote, int)):
            raise TypeError("ERROR: SongRatestatTags - each value in parameter 'votes' must be type integer")

        if (vote < 1 or vote > 10):
            raise TypeError("ERROR: SongRatestatTags - each value in parameter 'votes' must be an integer between (or equal to) 1 and 10")



def readSongRatestatTags(songFilepath):
    audioFile = mutagen.File(songFilepath)
    votesList = mlu.tags.common.formatAudioTagStringToValuesList(audioFile['VOTES'], valuesAsInt=True)
    ratingFloat = float(audioFile['RATING'])

    ratestatTags = SongRatestatTags(
        songFilepath=songFilepath,
        votes=votesList,
        rating=ratingFloat  
    ) 
    return ratestatTags

def writeSongRatestatTags(songRatestatTags):
    ratingRoundedStr = str(round(songRatestatTags.rating, 2))
    votesStr = mlu.tags.common.formatValuesListToAudioTagString(songRatestatTags.votes)

    audioFile = mutagen.File(songRatestatTags.songFilepath)
    audioFile['VOTES'] = votesStr
    audioFile['RATING'] = ratingRoundedStr
    audioFile.save()
    

def addVoteAndUpdateSongRatestatTags(songFilepath, newVote):
    existingSongRatestatTags = readSongRatestatTags(songFilepath)
    
    newSongRatestatTags = existingSongRatestatTags
    newSongRatestatTags.addVote(newVote)
    newSongRatestatTags.updateRating()

    writeSongRatestatTags(newSongRatestatTags)
    


def updateAvgRatingForAllLibrarySongs():
    pass



