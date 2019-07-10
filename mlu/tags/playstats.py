'''
mlu.tags.playstats

This module deals with reading and writing playback-related tag information on audio files.
'''

from collections import OrderedDict
import mutagen


# Class representing the data structure holding the various tag values of a song for the playstats tags
# that we are dealing with - 3 tags: PLAY_COUNT, TIME_LAST_PLAYED, ALL_TIMES_PLAYED
class SongPlaystatTags:
    def __init__(self, songFilepath, playCount, timeLastPlayed, allTimesPlayed):
        self.songFilepath = songFilepath
        self.playCount = playCount
        self.timeLastPlayed = timeLastPlayed
        self.allTimesPlayed = allTimesPlayed

    

def GetSongCurrentPlaystatTags(songFilepath):
    audioFile = mutagen.File(songFilepath)
    
    playstatTags = SongPlaystatTags(
        songFilepath=songFilepath,
        playCount=audioFile['PLAY_COUNT'],
        timeLastPlayed=audioFile['TIME_LAST_PLAYED'],
        allTimesPlayed=audioFile['ALL_TIMES_PLAYED']
    )

    return playstatTags


def MergePlaystatTagsWithPlaybackRecord(songPlaystatTags, songPlaybackRecord):
    # Sanity check: ensure that the given tags and the playback record are for the same song
    # they must be in order to update the tags
    if (songPlaystatTags.songFilepath != songPlaybackRecord.songFilepath):
        raise("ERROR: given SongPlaystatTags and SongPlaybackRecord do not refer to the same audio file - unable to merge")







