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
- DURATION

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

        # Read TITLE tag
        rawTitleTag = audioFile['TITLE'][0]
        if (not rawTitleTag):
            logger.debug("Tag value 'TITLE' is empty for song '{}': tag handler instance variable will be Null".format(self._songFilepath))
            self._title = None
        else:
            self._title = rawTitleTag

        # Read ARTIST tag
        rawArtistTag = audioFile['ARTIST'][0]
        if (not rawArtistTag):
            logger.debug("Tag value 'ARTIST' is empty for song '{}': tag handler instance variable will be Null".format(self._songFilepath))
            self._artist = None
        else:
            self._artist = rawArtistTag

        # Read ALBUM tag
        rawAlbumTag = audioFile['ALBUM'][0]
        if (not rawAlbumTag):
            logger.debug("Tag value 'ALBUM' is empty for song '{}': tag handler instance variable will be Null".format(self._songFilepath))
            self._album = None
        else:
            self._album = rawAlbumTag

        # audio file should always have a duration
        durationProperty = audioFile.info.length
        self._duration = durationProperty

        logger.debug("Successfully READ basic tags for audio file: Path='{}', Title='{}', Artist='{}', Album='{}', Duration='{}'".format(self._songFilepath, self._title, self._artist, self._album, self._duration))


    def writeTags(self):
        '''
        Writes the tags that are currently set (saved in this SongBasicTagsHandler instance) to the
        audio file, replacing the file's old basic tags with the current (new) values.
        '''
        if (not self._tagsHaveBeenSet):
            raise Exception("Cannot write basic tags: tag values have not yet been set for audio file '{}': call updateTags() first before writing new tag values".format(self._songFilepath))


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


    def updateTags(self, title, artist, album):
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