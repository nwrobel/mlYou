'''
mlu.tags.playstats

This module deals with reading and writing playback-related tag information on audio files.


'''
# TODO:
# when reading playback tags, convert them to epoch timestamps and create them from a list from a semicolon seperated string
# when writing tags, convert times to formatted strings as string seperated by semicolons

import mutagen

# setup logging for the module using preconfigured MLU logger
import mlu.common.logger
logger = mlu.common.logger.getMLULogger()

from mlu.tags.base import SongTagsHandler

# Class representing the data structure holding the various tag values of a song for the playstats tags
# that we are dealing with - 3 tags: PLAY_COUNT, TIME_LAST_PLAYED, ALL_TIMES_PLAYED
class SongPlaystatTags:
    def __init__(self, songFilepath, playCount, timeLastPlayed, allTimesPlayed):
        self.songFilepath = songFilepath
        self.playCount = playCount
        self.timeLastPlayed = timeLastPlayed
        self.allTimesPlayed = allTimesPlayed # should be a list of epoch timestamps



class SongPlaystatTagsHandler(SongTagsHandler):
    '''
    Public class which handles the 'playstat' tag values for a single audio file, allowing these tags
    to be read from the file and for new, updated tag values to be set after being validated. 
    This class also deals with tag value reading from and writing to the audio file itself.
    '''
    def __init__(self, songFilepath):
        # base tag handler class enforces that songFilepath must be set: pass songFilepath to
        # the base class to have it set there (and also here in the child class)
        super().__init__(songFilepath)

        self._playCount = None 
        self._timeLastPlayed = None 
        self._allTimesPlayed = None

        self.readTags()

    def readTags(self):
        '''
        Reads in the current values of all playstat tags, updating the class instance's fields with
        this data.
        '''
        audioFile = mutagen.File(self._songFilepath)

        # Read PLAY_COUNT tag 
        rawPlayCountTag = audioFile['PLAY_COUNT'][0]
        if (not rawPlayCountTag):
            logger.debug("Tag value 'PLAY_COUNT' is empty for song '{}': tag handler instance variable will be Null".format(self._songFilepath))
            self._playCount = None
        else:
            self._playCount =  int(rawPlayCountTag)

        # Read TIME_LAST_PLAYED tag
        rawTimeLastPlayedTag = audioFile['TIME_LAST_PLAYED'][0]
        if (not rawTimeLastPlayedTag):
            logger.debug("Tag value 'TIME_LAST_PLAYED' is empty for song '{}': tag handler instance variable will be Null".format(self._songFilepath))
            self._timeLastPlayed = None
        else:
            self._timeLastPlayed = mlu.common.time.getTimestampFromFormattedTime(rawTimeLastPlayedTag)

        # Read the ALL_TIMES_PLAYED tag
        rawAllTimesPlayedTag = audioFile['ALL_TIMES_PLAYED'][0]
        if (not rawAllTimesPlayedTag):
            logger.debug("Tag value 'ALL_TIMES_PLAYED' is empty for song '{}': tag handler instance variable will be Null".format(self._songFilepath))
            self._allTimesPlayed = None
        else:
            allTimesPlayedFormattedTimes = mlu.tags.common.formatAudioTagToValuesList(rawAllTimesPlayedTag)
            self._allTimesPlayed = [mlu.common.time.getTimestampFromFormattedTime(formattedTime) for formattedTime in allTimesPlayedFormattedTimes]


        logger.debug("Successfully READ playstat tags for audio file: Path='{}', PlayCount='{}', TimeLastPlayed='{}', AllTimesPlayed='{}'".format(self._songFilepath, self._playCount, self._timeLastPlayed, self._allTimesPlayed))


    def writeTags(self):
        '''
        Writes the tags that are currently set (saved in this instance) to the
        audio file, replacing the file's old basic tags with the current (new) values.
        '''
        if (not self._tagsHaveBeenSet):
            raise Exception("Cannot write playstat tags: tag values have not yet been set for audio file '{}': call setTags() first before writing new tag values".format(self._songFilepath))


        audioFile = mutagen.File(self._songFilepath)

        # Write PLAY_COUNT tag
        rawPlayCountTag = str(self._playCount)
        audioFile['PLAY_COUNT'] = rawPlayCountTag

        # Write TIME_LAST_PLAYED tag
        rawTimeLastPlayedTag = mlu.common.time.formatTimestampForDisplay(self._timeLastPlayed)
        audioFile['TIME_LAST_PLAYED'] = rawTimeLastPlayedTag

        # Write ALL_TIMES_PLAYED tag
        formattedTimestamps = [mlu.common.time.formatTimestampForDisplay(timestamp) for timestamp in self._allTimesPlayed]
        rawAllTimesPlayedTag = mlu.tags.common.formatValuesListToAudioTag(formattedTimestamps)
        audioFile['ALL_TIMES_PLAYED'] = rawAllTimesPlayedTag

        audioFile.save()
        logger.debug("Successfully WROTE playstat tags for audio file: Path='{}', PlayCount='{}', TimeLastPlayed='{}', AllTimesPlayed='{}'".format(self._songFilepath, self._playCount, self._timeLastPlayed, self._allTimesPlayed))


    def getTags(self):
        '''

        '''
        return SongPlaystatTags(
            songFilepath=self._songFilepath,
            playCount=self._playCount,
            timeLastPlayed=self._timeLastPlayed,
            allTimesPlayed=self._allTimesPlayed        
        )

    def updateTags(self, newPlayCount, newTimeLastPlayed, newAllTimesPlayed):
        '''

        '''
        # check for validity of input values and then set the tags to the given values 
        # this will throw an exception if any of these given tag values are invalid
        self._validateTagValues(newPlayCount, newTimeLastPlayed, newAllTimesPlayed)

        self._playCount = newPlayCount
        self._timeLastPlayed = newTimeLastPlayed
        self._allTimesPlayed = newAllTimesPlayed

        self._tagsHaveBeenSet = True
        logger.debug("Successfully SET playstat tags for audio file: Path='{}', PlayCount='{}', TimeLastPlayed='{}', AllTimesPlayed='{}'".format(self._songFilepath, self._playCount, self._timeLastPlayed, self._allTimesPlayed))


    def _validateTagValues(self, playCount, timeLastPlayed, allTimesPlayed):
        '''
        Private method that performs validation of the given tag values, ensuring that an invalid
        value is not set.
        '''
        if (not isinstance(playCount, int) or (playCount <= 0)):
            raise ValueError("Class attribute 'playCount' must be a positive non-zero integer")

        if (not isinstance(timeLastPlayed, int) or (timeLastPlayed <= 0)):
            raise ValueError("Class attribute 'timeLastPlayed' must be a valid epoch timestamp: a positive non-zero integer")

        if (not allTimesPlayed) or (not isinstance(allTimesPlayed, list)):
            raise ValueError("Class attribute 'allTimesPlayed' must be a non-empty list containing epoch timestamps")



# ============================================================================================
# OLD CODE
# TODO: integrate this code into this module and/or add to a new module

# class PlaystatTagReader ?

def FindSongsWithWrongPlaystatTags(expectedSongsPlaystatTags):
    incorrectTaggedSongs = []

    for expectedSongPlaystatTags in expectedSongsPlaystatTags:
        actualSongPlaystatTags = GetSongCurrentPlaystatTags(expectedSongPlaystatTags.songFilepath)

        playcountDifferent = (expectedSongPlaystatTags.playCount != actualSongPlaystatTags.playCount)
        timeLastPlayedDifferent = (expectedSongPlaystatTags.timeLastPlayed != actualSongPlaystatTags.timeLastPlayed)
        allTimesPlayedDifferent = (expectedSongPlaystatTags.allTimesPlayed != actualSongPlaystatTags.allTimesPlayed)

        if (playcountDifferent or timeLastPlayedDifferent or allTimesPlayedDifferent):
            incorrectTaggedSongs.append(expectedSongPlaystatTags.songFilepath)

    return incorrectTaggedSongs


def ReadCurrentPlaystatTagsFromSongs(songFilepaths):
    songsPlaystatTags = []

    for songFilepath in songFilepaths:
        songsPlaystatTags.append( GetSongCurrentPlaystatTags(songFilepath) )

    return songsPlaystatTags


def GetSongCurrentPlaystatTags(songFilepath):
    audioFile = mutagen.File(songFilepath)
    songPlaystatTags = SongPlaystatTags(
        songFilepath=songFilepath,
        playCount=audioFile['PLAY_COUNT'],
        timeLastPlayed=audioFile['TIME_LAST_PLAYED'],
        allTimesPlayed=audioFile['ALL_TIMES_PLAYED'] # will this give us list or CSV ??? - may need to add function to fix this value to SongPlaystatTags class 
    ) 

    return songPlaystatTags   


#--------------------------------------------------------------------------------
# Class that calculates a new, updated set of SongPlaystatTags after the current ones are updated
# with the playback data. The current playstat tags for all the songs and the playback records
# for them are given to this class, and it returns a new set of the song's tags as a result, which
# can then be used to write to the audio files to complete the tag updates.
#
class SongPlaystatTagsUpdateResolver:
    def __init__(self, songPlaybackRecords, songsPlaystatTags):
        self.songPlaybackRecords = songPlaybackRecords
        self.songsPlaystatTags = songsPlaystatTags

    def GetUpdatedPlaystatTags(self):
        updatedPlaystatTagsList = []

        # Go thru each SongPlaystatsTags object (each song's current tags)
        # and find the corresponding SongPlaybackRecord for that song, so we can use it to 
        # update its tags
        # Then merge the playbackRecord with the playbackTags to perform the tag "update" - this returns
        # a new tag object with the updated data, which we add to updatedPlaystatTagsList
        for songPlaystatTags in self.songsPlaystatTags:
            songPlaybackRecord = self.GetPlaybackRecordForSong(songPlaystatTags.songFilepath)
            updatedPlaystatTags = self.MergePlaystatTagsWithPlaybackRecord(songPlaystatTags, songPlaybackRecord)
            updatedPlaystatTagsList.append(updatedPlaystatTags)

        return updatedPlaystatTagsList

    def GetPlaybackRecordForSong(self, songFilepath):
        for playbackRecord in self.songPlaybackRecords:
            if (playbackRecord.songFilepath == songFilepath):
                return playbackRecord
        
        raise("ERROR: Corresponding SongPlaybackRecord object not found for given songFilepath")

    def MergePlaystatTagsWithPlaybackRecord(self, songPlaystatTags, songPlaybackRecord):
        # Sanity check: ensure that the given tags and the playback record are for the same song
        if (songPlaystatTags.songFilepath != songPlaybackRecord.songFilepath):
            raise("ERROR: given SongPlaystatTags and SongPlaybackRecord do not refer to the same audio file - unable to merge")

        # Calculate new tags based on the playbackRecord updates
        newPlayCount = songPlaystatTags.playCount + len(songPlaybackRecord.playbackTimes)
        newAllTimesPlayed = songPlaystatTags.allTimesPlayed + songPlaybackRecord.playbackTimes # Add two list() objects in python by using "+"
        newTimeLastPlayed = max(newAllTimesPlayed)

        # Create a new SongPlaybackTags with the updated tag data
        updatedTags = SongPlaystatTags(
            songFilepath=songPlaystatTags.songFilepath,
            playCount=newPlayCount,
            timeLastPlayed=newTimeLastPlayed,
            allTimesPlayed=newAllTimesPlayed
        )

        return updatedTags









def WritePlaystatTagsToSongs(songsPlaystatTags):
    for songPlaystatTags in songsPlaystatTags:
        audioFile = mutagen.File(songPlaystatTags.songFilepath)
        audioFile['PLAY_COUNT'] = songPlaystatTags.playCount
        audioFile['TIME_LAST_PLAYED'] = songPlaystatTags.timeLastPlayed
        audioFile['ALL_TIMES_PLAYED'] = songPlaystatTags.allTimesPlayed # FIX - - put semicolons b/w instead of commas

        audioFile.save()



        







