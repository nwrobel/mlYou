'''
mlu.playbacks

Author: Nick Wrobel
First Created:  01/16/20
Last Modified:  01/22/20

Module that deals with handling song playback instances and determining the playback tag values
(playstat tags) that should be written to the played songs accordingly. 

This includes logic for: 
- determining if a play should be counted based on playback duration 
- calculations for time last played, first played, all times played, and play count tag values
- defining playback instance and playback records classes
- merging playback instances containing multiple play instances of the same song into playback 
list records containing multiple records of plays for a single song

'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

import mlu.tags.io
import mlu.tags.common

class AudioFilePlaybackData:
    def __init__(self, audioFilepath, playbackInstances):
        self.audioFilepath = audioFilepath
        self.playbackInstances = playbackInstances

class AudioFilePlaybackInstance:
    def __init__(self, playTimeStart, playTimeDuration):
        self.playTimeStart = playTimeStart
        self.playTimeDuration = playTimeDuration

def updateAudioFilePlaystatTagsFromPlaybackData(audioFilePlaybackData):
    # Filter false playbacks from each playback in the list of playbacks for this audio file
    truePlaybackInstances = _filterFalsePlaybacks(audioFilePlaybackData.audioFilepath, audioFilePlaybackData.playbackInstances)
    audioFilePlaybackData.playbackInstances = truePlaybackInstances

    tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFilePlaybackData.audioFilepath)
    currentTags = tagHandler.getTags()
    newTags = currentTags

    currentPlayTimes = mlu.tags.common.formatAudioTagToValuesList(currentTags.dateAllPlays)
    addedPlayTimes = [playbackInstance.playTimeStart for playbackInstance in audioFilePlaybackData.playbackInstances]
    newPlayTimes = currentPlayTimes + addedPlayTimes
    newTags.dateAllPlays = mlu.tags.common.formatValuesListToAudioTag(newPlayTimes)

    newTags.dateLastPlayed = max(newPlayTimes)

    numAddedPlays = len(audioFilePlaybackData.playbackInstances)
    newTags.playCount = str(int(currentTags.playCount) + numAddedPlays)
    tagHandler.setTags(newTags)

# TODO: update playback filtering to check if there are 2 or more playbacks of the same song within
# about 0-10 min. of each other - these are most likely caused by MPD disconnect/reconnecting and shouldn't be counted
'''
Rules for playback instance to be counted as "true" playback:
- It takes about 30 seconds, due to latency, for a song to be skipped from MPD client, so:
--- If song duration is at least 2 minutes, playback duration must be at least 25% of the song duration
--- If song duration is less than 2 minutes, playback duration must be at least 50% of the song duration
'''
def _filterFalsePlaybacks(audioFilepath, audioFilePlaybackInstances):
    '''
    Filters the list of SongPlaybackInstance objects, given in the constructor, by removing any
    playback instances that are 'invalid' or should not count due to playback duration. This
    returns a new list of 'true' SongPlaybackInstance objects.
    '''
    songDurationThresholdSeconds = 120
    songDurationThresholdTimestamp = mypycommons.time.convertSecondsToTimestamp(songDurationThresholdSeconds)

    audioFileDuration = mlu.tags.io.getAudioFileDurationAsTimestamp(audioFilepath)
    truePlaybackInstances = []

    for playbackInstance in audioFilePlaybackInstances.playbackInstances:
        # If song duration is 2 minutes or longer, 25% of the song must have been played to count it
        # If it's less than 2 minutes, 50% of the song must have been played
        if (audioFileDuration >= songDurationThresholdTimestamp):
            playbackDurationThreshold = audioFileDuration * 0.25
        else:
            playbackDurationThreshold = audioFileDuration * 0.5

    # If the playback duration is at least this amount, add it to the true playbackInstances
    if (playbackInstance.playTimeDuration >= playbackDurationThreshold):
        truePlaybackInstances.append(playbackInstance)

    return truePlaybackInstances
