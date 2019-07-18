import mutagen

# Returns the following tag values for the given audio file, given its filepath:
#   durationSeconds
#   title
#   artist
#   album
#
class _SongBasicTags:
    """
    Class that represents the values of an audio file's "basic"/common tags.
    """
    def __init__(self, title, artist, album, durationSeconds):
        self.title = title
        self.artist = artist
        self.album = album
        self.durationSeconds = durationSeconds


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
    tags = _SongBasicTags(
        title=audioFile['TITLE'],
        artist=audioFile['ARTIST'],
        album=audioFile['ALBUM'],
        durationSeconds=audioFile.info.length
    )

    return tags