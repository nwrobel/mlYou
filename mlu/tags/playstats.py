'''
mlu.tags.playstats

This module deals with reading and writing playback-related tag information on audio files.
'''

from collections import OrderedDict
import mutagen
import mlu.mpd.playstats

# Class representing the data structure holding the various tag values of a song for the playstats tags
# that we are dealing with - 3 tags: PLAY_COUNT, TIME_LAST_PLAYED, ALL_TIMES_PLAYED
class SongPlaystatTags:
    def __init__(self, songFilepath, playCount, timeLastPlayed, allTimesPlayed):
        self.songFilepath = songFilepath
        self.playCount = playCount
        self.timeLastPlayed = timeLastPlayed
        self.allTimesPlayed = allTimesPlayed


# class PlaystatTagReader ?

def VerifySongPlaystatTags():
    pass

def GetSongCurrentPlaystatTags(songFilepath):
    audioFile = mutagen.File(songFilepath)
    
    playstatTags = SongPlaystatTags(
        songFilepath=songFilepath,
        playCount=audioFile['PLAY_COUNT'],
        timeLastPlayed=audioFile['TIME_LAST_PLAYED'],
        allTimesPlayed=audioFile['ALL_TIMES_PLAYED'] # will this give us list or CSV ???
    )

    return playstatTags

# class PlaystatTagUpdater / PlaystatTagHandler

def GetPlaybackRecordForSongFilepath(songPlaybackRecords, songFilepath):
    for playbackRecord in songPlaybackRecords:
        if (playbackRecord.songFilepath == songFilepath):
            return playbackRecord
    
    raise("ERROR: Corresponding SongPlaybackRecord object not found for given songFilepath")


def MergePlaystatTagsWithPlaybackRecord(songPlaystatTags, songPlaybackRecord):
    # Sanity check: ensure that the given tags and the playback record are for the same song
    # they must be in order to update the tags
    if (songPlaystatTags.songFilepath != songPlaybackRecord.songFilepath):
        raise("ERROR: given SongPlaystatTags and SongPlaybackRecord do not refer to the same audio file - unable to merge")

    # Calculate new tags based on the playbackRecord updates
    newPlayCount = songPlaystatTags.playCount + len(songPlaybackRecord.playbackTimes)
    newAllTimesPlayed = songPlaystatTags.allTimesPlayed + songPlaybackRecord.playbackTimes
    newTimeLastPlayed = max(newAllTimesPlayed)

    # Create a new SongPlaybackTags with the updated tag data
    updatedTags = SongPlaystatTags(
        songFilepath=songPlaystatTags.songFilepath,
        playCount=newPlayCount,
        timeLastPlayed=newTimeLastPlayed,
        allTimesPlayed=newAllTimesPlayed
    )

    return updatedTags



def GetUpdatedPlaystatTags(songPlaystatTagsList, songPlaybackRecords):
    updatedPlaystatTagsList = []

    # Go thru each of SongPlaystatsTags object (each song's current tags)
    # and find the corresponding SongPlaybackRecord for that song, so we can use it to 
    # update its tags
    # Then merge the playbackRecord with the playbackTags to perform the tag "update" - this returns
    # a new tag object with the updated data, which we add to updatedPlaystatTagsList
    for songPlaystatTags in songPlaystatTagsList:
        songPlaybackRecord = GetPlaybackRecordForSongFilepath(songPlaybackRecords, songPlaystatTags.songFilepath)
        updatedPlaystatTags = MergePlaystatTagsWithPlaybackRecord(songPlaystatTags, songPlaybackRecord)
        updatedPlaystatTagsList.append(updatedPlaystatTags)

    return updatedPlaystatTagsList



class PlaystatTagWriter:
    def __init__(self, songPlaystatTagsList):
        self.songPlaystatTagsList = songPlaystatTagsList

    def WritePlaystatTags(self):
        for songPlaystatTags in self.songPlaystatTagsList:
            audioFile = mutagen.File(songPlaystatTags.songFilepath)
            audioFile['PLAY_COUNT'] = songPlaystatTags.playCount
            audioFile['TIME_LAST_PLAYED'] = songPlaystatTags.timeLastPlayed
            audioFile['ALL_TIMES_PLAYED'] = songPlaystatTags.allTimesPlayed

            audioFile.save()

        







