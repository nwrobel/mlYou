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

        # Write TITLE tag
        rawTitleTag = self._title
        audioFile['TITLE'] = rawTitleTag

        # Write ARTIST tag
        rawArtistTag = self._artist
        audioFile['ARTIST'] = rawArtistTag

        # Write ALBUM tag
        if (self._album is None):
            rawAlbumTag = ''
        else:
            rawAlbumTag = self._album
        audioFile['ALBUM'] = rawAlbumTag

        audioFile.save()
        logger.debug("Successfully WROTE basic tags for audio file: Path='{}', Title='{}', Artist='{}', Album='{}'".format(self._songFilepath, self._title, self._artist, self._album))


    def getTags(self):
        '''
        Returns a SongBasicTags object, which holds the song filepath as well as the current basic 
        tag values for the song represented by this SongBasicTagsHandler instance.
        '''
        return SongBasicTags(
            songFilepath=self._songFilepath,
            title=self._title,
            artist=self._artist,
            album=self._album,
            duration=self._duration
        )


    def setTags(self, title, artist, album):
        '''
        Allows the tag values saved in this SongBasicTagsHandler instance to be changed/set.
        Validation on the given values for each tag is performed and an exception will be thrown
        if any tag values fail this validation checking.

        Params:
            title: the new desired song title tag value (must be set)
            artist: the new desired song artist tag value (must be set)
            album: the new desired song album tag value (can be empty/unset, pass the empty string
                as the value if so to indicate no album tag)
        '''
        # check for validity of input values and then set the tags to the given values 
        # this will throw an exception if any of these given tag values are invalid
        self._validateTagValues(title, artist, album)

        self._title = title
        self._artist = artist

        if (album):
            self._album = album
        else:
            self._album = None

        self._tagsHaveBeenSet = True
        logger.debug("Successfully SET tag values for SongBasicTagHander instance: Path='{}', Title='{}', Artist='{}', Album='{}'".format(self._songFilepath, self._title, self._artist, self._album))


    def _validateTagValues(self, title, artist, album):
        '''
        Private method that performs validation of the given tag values, ensuring that an invalid
        value is not set.
        '''
        if (not title) or (not isinstance(title, str)):
            raise ValueError("Class attribute 'title' must be a non-empty string")

        if (not title) or (not isinstance(artist, str)):
            raise ValueError("Class attribute 'artist' must be a non-empty string")

        if (not isinstance(album, str)):
            raise ValueError("Class attribute 'album' must be a string (the empty string is also valid if no album tag exists)")




        







