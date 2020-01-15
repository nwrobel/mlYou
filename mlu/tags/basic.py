import mutagen

# Returns the following tag values for the given audio file, given its filepath:
#   durationSeconds
#   title
#   artist
#   album
#

class SingleSongBasicTagsHandler:
    '''
    Private class which handles the 'basic' tag values for a single audio file and allows
    new, updated values to be set. This class also deals with tag value reading from and writing
    to the audio file itself.
    '''
    def __init__(self, songFilepath):
        self.songFilepath = songFilepath
        self.title = None 
        self.artist = None 
        self.album = None
        self.durationSeconds = None

        # Throw exceptions is the wrong data type is passed in
        if (not isinstance(self.songFilepath, str)):
            raise TypeError("Constructor parameter 'songFilepath' must be a string")

        # read in the tag values to populate the fields
        self._readBasicTags()

    def _readBasicTags(self):
        '''
        Reads in the current values of all basic tags, updating the class instance's fields with
        this data.
        '''
        audioFile = mutagen.File(self.songFilepath)

        try:
            rawTitleTag = audioFile['TITLE']
            rawTitleTag = rawTitleTag[0]
        except KeyError:
            rawTitleTag = ''

        try:
            rawArtistTag = audioFile['ARTIST']
            rawArtistTag = rawArtistTag[0]
        except KeyError:
            rawArtistTag = ''

        try:
            rawAlbumTag = audioFile['ALBUM']
            rawAlbumTag = rawAlbumTag[0]
        except KeyError:
            rawAlbumTag = ''

        try:
            durationProperty = audioFile.info.length
        except:
            logger.exception("Unable to set basic tag 'duration' ")

        self.title = rawTitleTag
        self.artist = rawArtistTag
        self.album = rawAlbumTag

        logger.debug("Successfully READ basic tags for audio file: Path='{}', Title='{}', Artist='{}', Album='{}'".format(self.songFilepath, self.title, self.artist, self.album))


def getSongBasicTags(songFilepath):
    """
    Retrieves the tag values of the given audio filepath for several standard, common tags. Returns
    a SongBasicTags object, containing the audio's values for tags: title, artist, album, duration.

    Args:
        songFilepath: the absolute filepath of the song/audio file

    Returns:
        SongBasicTags object holding the basic tags' values for the song
    """
    audioFile = mutagen.File(songFilepath)
    tags = SongBasicTags(
        title=audioFile['TITLE'],
        artist=audioFile['ARTIST'],
        album=audioFile['ALBUM'],
        durationSeconds=audioFile.info.length
    )

    return tags