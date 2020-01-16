'''
mlu.tags.basic

First created: ?
Last modified: 01/16/20

This module contains the SongBasicTagsHandler class, which handles the set of "basic" tags for
a single audio file. It also contains the SongBasicTags class object, which is meant to hold
the basic tag values of the audio file when they are returned via getTags().

The following audio tags are handled by this tag handler, meaning they are read from and written
to the file and can be gotten and set:
- TITLE
- ARTIST
- ALBUM

'''

# TODO:
# modify ratestat and playstat tags to have the same structure as this, creating the MLU
# project's API for interacting with audio file tags for a single file
#
# Later we can also have classes to deal with handling collections of songs, which will use these
# classes under the hood

import mutagen

# setup logging for the module using preconfigured MLU logger
import mlu.common.logger
logger = mlu.common.logger.getMLULogger()

from mlu.tags.base import SongTagsHandler

class SongBasicTags:
    '''
    Simple container class that is used to pass around basic song tags to external code. The
    SongBasicTagsHandler returns this object type when .getTags() is called.
    '''
    def __init__(self, songFilepath, title, artist, album, duration):
        self.songFilepath = songFilepath
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration

class SongBasicTagsHandler(SongTagsHandler):
    '''
    Public class which handles the 'basic' tag values for a single audio file, allowing these tags
    to be read from the file and for new, updated tag values to be set after being validated. 
    This class also deals with tag value reading from and writing to the audio file itself.
    '''
    def __init__(self, songFilepath):
        # base tag handler class enforces that songFilepath must be set: pass songFilepath to
        # the base class to have it set there (and also here in the child class)
        super().__init__(songFilepath)

        self._title = None 
        self._artist = None 
        self._album = None
        self._duration = None

        self.readTags()

    def readTags(self):
       '''
        Reads in the current values of all basic tags, updating the class instance's fields with
        this data.
        '''
        audioFile = mutagen.File(self._songFilepath)

        # set the fields from the raw tag values and properties
        try:
            rawTitleTag = audioFile['TITLE']
            rawTitleTag = rawTitleTag[0]
            self._title = rawTitleTag

        except KeyError:
            logger.debug("No tag value found for tag name 'TITLE' for song '{}': leaving instance variable Null".format(self._songFilepath))

        try:
            rawArtistTag = audioFile['ARTIST']
            rawArtistTag = rawArtistTag[0]
            self._artist = rawArtistTag

        except KeyError:
            logger.debug("No tag value found for tag name 'ARTIST' for song '{}': leaving instance variable Null".format(self._songFilepath))

        try:
            rawAlbumTag = audioFile['ALBUM']
            rawAlbumTag = rawAlbumTag[0]
            self._album = rawAlbumTag

        except KeyError:
            logger.debug("No tag value found for tag name 'ALBUM' for song '{}': leaving instance variable Null".format(self._songFilepath))

        # audio file should always have a duration
        durationProperty = audioFile.info.length
        self._duration = durationProperty

        logger.debug("Successfully READ basic tags for audio file: Path='{}', Title='{}', Artist='{}', Album='{}', Duration='{}'".format(self._songFilepath, self._title, self._artist, self._album, self._duration))


    def writeTags(self):
        '''
        Writes the tags that are currently set (saved in this SongBasicTagsHandler instance) to the
        audio file, replacing the file's old basic tags with the current (new) values.
        '''
        audioFile = mutagen.File(self._songFilepath)

        # Write all basic tags, except for 'duration', which is an immutable property of the file
        audioFile['TITLE'] = self._title
        audioFile['ARTIST'] = self._artist
        audioFile['ALBUM'] = self._album

        audioFile.save()
        logger.debug("Successfully WROTE basic tags for audio file: Path='{}', Title='{}', Artist='{}', Album='{}'".format(self._songFilepath, self._title, self._artist, self._album))


    def getTags(self):
        '''
        Returns a SongBasicTags object, which holds the song filepath as well as the current basic 
        tag values for the song represented by this SongBasicTagsHandler instance.
        '''
        return SongBasicTags(
            songFilepath=self._songFilepath
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
                as the value if so)
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

        logger.debug("Successfully SET tag values for SongBasicTagHander instance: Path='{}', Title='{}', Artist='{}', Album='{}'".format(self._songFilepath, self._title, self._artist, self._album))


    def _validateTagValues(self, title, artist, album):
        '''
        Private method that performs validation of the given tag values, ensuring that an invalid
        value is not set.
        '''
        if (not title) or (not isinstance(title, str)):
            raise TypeError("Class attribute 'title' must be a non-empty string")

        if (not title) or (not isinstance(artist, str)):
            raise TypeError("Class attribute 'artist' must be a non-empty string")

        if (not isinstance(album, str)):
            raise TypeError("Class attribute 'album' must be a string (the empty string is also valid if no album tag exists)")