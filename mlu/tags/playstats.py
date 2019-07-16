'''
mlu.tags.playstats

This module deals with reading and writing playback-related tag information on audio files.

TODO:
when reading playback tags, convert them to epoch timestamps and create them from a list from a semicolon seperated string
when writing tags, convert times to formatted strings as string seperated by semicolons
'''

from collections import OrderedDict
import mutagen
import mlu.mpd.plays

# Class representing the data structure holding the various tag values of a song for the playstats tags
# that we are dealing with - 3 tags: PLAY_COUNT, TIME_LAST_PLAYED, ALL_TIMES_PLAYED
class SongPlaystatTags:
    def __init__(self, songFilepath, playCount, timeLastPlayed, allTimesPlayed):
        self.songFilepath = songFilepath
        self.playCount = playCount
        self.timeLastPlayed = timeLastPlayed
        self.allTimesPlayed = allTimesPlayed # should be a list of epoch timestamps


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

        







