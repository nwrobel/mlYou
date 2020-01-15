# TODO:
# finish this class by implementing the methods promised by the base class
# then modify ratestat and playstat tags to have the same structure as this, creating the MLU
# project's API for interacting with audio file tags for a single file
#
# Later we can also have classes to deal with handling collections of songs, which will use these
# classes under the hood

import mutagen

from mlu.tags.base import SongTagsHandler

class SongBasicTagsHandler(SongTagsHandler):

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
        pass

    def getTags(self):
        pass

    def setTags(self, title, artist, album):
        # check for validity of input values and then set the tags to the given values 
        _validateTagValues(title, artist, album)


    def _validateTagValues(self, title, artist, album):
        pass 