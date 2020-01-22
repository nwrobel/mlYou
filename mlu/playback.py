'''
mlu.playbacks

First Created: 01/16/20
Last Modified: 01/22/20

Module that deals with handling song playback instances and determining the playback tag values
(playstat tags) that should be written to the played songs accordingly. 

This includes logic for: 
- determining if a play should be counted based on playback duration 
- calculations for time last played, first played, all times played, and play count tag values
- defining playback instance and playback records classes
- merging playback instances containing multiple play instances of the same song into playback 
list records containing multiple records of plays for a single song

'''

import mlu.tags.basic
import mlu.common.time


class PlaybackInstance:
    '''
    Class representing an instance in which a single playback of an audio file occurred - contains
    details about the playback (start time, and for how long it was played) as well as the song's 
    actual duration

    These instances will be filtered later based on whether or not the playback time is long enough
    compared with the total duration of the song - to remove "false" playbacks

    Objects of this type will later be converted into SongPlaybackRecords, which contain data about
    all the playback instances for a single audio file
    '''
    def __init__(self, songFilepath, playbackStartTime, playbackDuration):
        self.songFilepath = songFilepath
        self.playbackStartTime = playbackStartTime
        self.playbackDuration = playbackDuration
        self.songDuration = self._getSongDuration()

        # If we pass '1' as the playback duration, this special value indicates that the exact playback duration is unknown,
        # so we just set it to the song duration
        if (self.playbackDuration == 1):
            self.playbackDuration = self.songDuration

        # Throw exceptions if the playback duration is wrong
        if (self.playbackDuration > self.songDuration):
            raise("ERROR: calculated playback duration is greater than the song's total duration, playback instance: " + self.songFilepath)

        if (self.playbackDuration <= 0):
            raise("ERROR: calculated playback duration is less than 0, playback instance: " + self.songFilepath)

    # Use filepath to get the audio file's common tags, one of which is the duration
    def _getSongDuration(self):
        songBasicTagsHandler = mlu.tags.basic.SongBasicTagsHandler(self.songFilepath)
        songBasicTags = songBasicTagsHandler.getTags()

        durationTimestamp = mlu.common.time.convertSecondsToTimestamp(songBasicTags.duration)
        return durationTimestamp


class PlaybackInstanceQualityFilter:
    '''
    Rules for playback instance to be counted as "true" playback:
    - It takes about 30 seconds, due to latency, for a song to be skipped from MPD client, so:
    --- If song duration is at least 2 minutes, playback duration must be at least 25% of the song duration
    --- If song duration is less than 2 minutes, playback duration must be at least 50% of the song duration
    '''
    def __init__(self, playbackInstances):
        self._playbackInstances = playbackInstances

    def filterFalsePlaybacks(self):
        songDurationThresholdSeconds = 120

        truePlaybackInstances = []
        songDurationThresholdTimestamp = mlu.common.time.convertSecondsToTimestamp(songDurationThresholdSeconds)

        for playbackInstance in self._playbackInstances:
            # If song duration is 2 minutes or longer, 25% of the song must have been played to count it
            # If it's less than 2 minutes, 50% of the song must have been played
            if (playbackInstance.songDuration >= songDurationThresholdTimestamp):
                playbackDurationThreshold = playbackInstance.songDuration * 0.25

            else:
                playbackDurationThreshold = playbackInstance.songDuration * 0.5

            # If the playback duration is at least this amount, add it to the true playbackInstances
            if (playbackInstance.playbackDuration >= playbackDurationThreshold):
                truePlaybackInstances.append(playbackInstance)

        return truePlaybackInstances



class SongPlaybackRecord:
    def __init__(self, songFilepath, playbackTimes):
        self.songFilepath = songFilepath
        self.playbackTimes = playbackTimes # should be a list of epoch timestamps


class SongPlaybackRecordCollector:
    '''
    Class that can take a list of playback instances, which can contain multiple different playback 
    times for a single song, and compress them down into a list of simpler objects form, so that the
    list contains only 1 element for each unique song played (no duplicate song play instances are 
    in the array). We call this simpler object form a SongPlaybackRecord object: this object can
    be readily used by the tag module as tag values.
    '''

    def __init__(self, playbackInstances):
        self._playbackInstances = playbackInstances

    def collectSongPlaybackRecords(self):
        '''
        '''
        # Get a list of all the unique song filepaths by taking the songFilepath property from each object in the playbackInstances array
         # cast this list to a set, eliminating duplicate song filepaths
        allSongFilepaths = list((playbackInstance.songFilepath for playbackInstance in self._playbackInstances))
        uniqueSongFilepaths = set(allSongFilepaths)

        songPlaybackRecords = []
        # Go thru each song filepath in this unique list:
        #   For each one, get all the playbackInstances this song has (must be at least 1)
        #   Combine these instances into one SongPlaybackRecord by setting the songFilepath and combining the playbackTimes into an array
        #   Add the new SongPlaybackRecord to the master list of these records
        # Return this list of records, so it can be used by the top-level script
        for songFilepath in uniqueSongFilepaths:
            playbacksForCurrentSong = self._getPlaybackInstancesForSong(songFilepath)
            songPlaybackRecord = self._mergePlaybackInstancesToSongPlaybackRecord(playbacksForCurrentSong)
            
            songPlaybackRecords.append(songPlaybackRecord)

        return songPlaybackRecords


    def _getPlaybackInstancesForSong(self, songFilepath):
        '''
        '''
        matchingPlaybackInstances = []

        for playbackInstance in self._playbackInstances:
            if (playbackInstance.songFilepath == songFilepath):
                matchingPlaybackInstances.append(playbackInstance)

        return matchingPlaybackInstances


    def _mergePlaybackInstancesToSongPlaybackRecord(self, songPlaybackInstances):
        '''
        '''
        # Get the song filepath: all of the playbackInstances should have the same song filepath, 
        # so we can just use the first playbackinstance element
        songFilepath = songPlaybackInstances[0].songFilepath
        songPlaybackTimes = list((playback.playbackStartTime for playback in songPlaybackInstances))

        return ( 
            SongPlaybackRecord(
                songFilepath=songFilepath, 
                playbackTimes=songPlaybackTimes) 
        )