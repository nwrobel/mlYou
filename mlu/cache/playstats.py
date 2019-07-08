
# Class representing the data structure holding the various tag values of a song for the playstats tags
# that we are dealing with
class SongPlaystatTagsRecord:
    def __init__(self, songFilepath, playCount, timeLastPlayed, timesPlayed):
        self.songFilepath = songFilepath
        self.playCount = playCount
        self.timeLastPlayed = timeLastPlayed
        self.timesPlayed = timesPlayed


def WriteSongPlaybackRecordsToCache():
    pass

def WriteSongsCurrentPlaystatTagsToCache():
    pass

def WriteSongsNewPlaystatTagsToCache():
    pass


def ReadSongsNewPlaystatTagsFromCache():
    pass