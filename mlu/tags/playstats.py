from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.time

from mlu.tags.io import AudioFileMetadataHandler, AudioFileFormatNotSupportedError, AudioFileNonExistentError
import mlu.tags.common

class Playback:
    def __init__(self, audioFilepath, playbackDateTime, playbackDurationSeconds=None):
        self.audioFilepath = audioFilepath
        self.playbackDateTime = playbackDateTime
        self.playbackDurationSeconds = playbackDurationSeconds

    def getDictForJsonFileOutput(self):
        return { 
            'audioFilepath': self.audioFilepath, 
            'playbackDateTime': self.playbackDateTime
        }

class AudioFilePlaybackInstances:
    def __init__(self, audioFilepath, playbackDateTimes):
        self.audioFilepath = audioFilepath

        # Sort the playback times, with oldest first
        playbackDateTimes.sort()
        self.playbackDateTimes = playbackDateTimes

    def getDictForJsonFileOutput(self):
        return {
            'audioFilepath': self.audioFilepath,
            'playbackDateTimes': self.playbackDateTimes
        }

class AudioFileDuration:
    def __init__(self, audioFilepath, duration):
        self.audioFilepath = audioFilepath
        self.duration = duration

def removeFalsePlaybacks(playbackList):
    '''
    Remove any playbacks in which less than 20% of the song was played.
    '''
    filteredPlaybackList = []

    # Optimization added:
    # Keep a list of dicts for audioFile durations, to avoid looking up the duration for the same audio file twice
    audioFileDurationList = []

    for playback in playbackList:
        thisAudioFileDuration = [
            audioFileDuration for audioFileDuration in audioFileDurationList if (playback.audioFilepath == audioFileDuration.audioFilepath)
        ]
        
        audioFileDuration = None
        if (thisAudioFileDuration):
            audioFileDuration = thisAudioFileDuration[0].duration
        else:
            audioFileDuration = _getAudioFileDuration(playback.audioFilepath)
            audioFileDurationList.append(AudioFileDuration(playback.audioFilepath, audioFileDuration))
        
        # If the audio file duration was not found (had an exception), add it to list of kept playbacks anyway
        # The error will be made clear later when attempting to write tags to it  
        if (audioFileDuration):
            percentOfAudioPlayed = 0
            if (playback.playbackDurationSeconds >= audioFileDuration):
                percentOfAudioPlayed = 100
            else:
                percentOfAudioPlayed = (playback.playbackDurationSeconds / audioFileDuration) * 100

            if (percentOfAudioPlayed >= 20):
                filteredPlaybackList.append(playback)
        
        else:
            filteredPlaybackList.append(playback)

    return filteredPlaybackList

def convertPlaybackListToAudioFilePlaybackInstancesList(playbackList):
    '''
    '''
    audioFilePlaybackInstancesList = []
    # filteredPlaybackList = _removeFalsePlaybacks(playbackList)

    for playback in playbackList:
        thisAudioFile = playback.audioFilepath
        thisAudioFilePlaybackInstances = [
            audioFilePlaybackInstances for audioFilePlaybackInstances in audioFilePlaybackInstancesList if (audioFilePlaybackInstances.audioFilepath == thisAudioFile)
        ]

        if (thisAudioFilePlaybackInstances):

            thisAudioFilePlaybackInstances[0].playbackDateTimes.append(playback.playbackDateTime)
        else:
            audioFilePlaybackInstancesList.append(
                AudioFilePlaybackInstances(thisAudioFile, [playback.playbackDateTime])
            )

    return audioFilePlaybackInstancesList

def convertAudioFilePlaybackInstancesListToPlaybackList(audioFilePlaybackInstancesList):
    playbackList = []
    for playbackInstance in audioFilePlaybackInstancesList:
        for playbackDateTime in playbackInstance.playbackDateTimes:
            playbackList.append(
                Playback(playbackInstance.audioFilepath, playbackDateTime)
            )
    return playbackList

def sortPlaybackListByTime(playbackList):
    playbackList.sort(key=lambda playback: playback.playbackDateTime)
    return playbackList

def sortPlaybackInstancesListByAudioFile(audioFilePlaybackInstancesList):
    audioFilePlaybackInstancesList.sort(key=lambda playbackInstance: playbackInstance.audioFilepath)
    return audioFilePlaybackInstancesList

def writeTagsForAudioFilePlaybackInstances(audioFilePlaybackInstances):
    '''
    Alter PLAY_COUNT, DATE_LAST_PLAYED, DATE_ALL_PLAYS
    '''
    handler = AudioFileMetadataHandler(audioFilePlaybackInstances.audioFilepath)
    currentTags = handler.getTags()

    # Get values needed
    if (currentTags.playCount):
        currentPlayCount = int(currentTags.playCount)
    else:
        currentPlayCount = 0
    
    if (currentTags.dateLastPlayed):
        currentDateLastPlayed = currentTags.dateLastPlayed
    else:
        currentDateLastPlayed = ""
    
    if (currentTags.dateAllPlays):
        currentDateAllPlaysList = mlu.tags.common.formatAudioTagValueToValuesList(currentTags.dateAllPlays)
    else:
        currentDateAllPlaysList = []

    # Set new values
    newPlayCount = currentPlayCount + len(audioFilePlaybackInstances.playbackDateTimes)
    # get last play time in the list (list is sorted already)
    newDateLastPlayed = audioFilePlaybackInstances.playbackDateTimes[-1] 
 
    newDateAllPlaysList = currentDateAllPlaysList
    for playbackDateTime in audioFilePlaybackInstances.playbackDateTimes:
        newDateAllPlaysList.append(playbackDateTime)
    newDateAllPlaysList.sort()

    # Check if the original last played tag value is newer than the last played value from the new playbackInstance
    # If it is, keep the last played tag what it currently is set as
    if (currentDateLastPlayed):
        currentLastPlayedTimestamp = mypycommons.time.getTimestampFromFormattedTime(currentDateLastPlayed)
        newLastPlayedTimestamp = mypycommons.time.getTimestampFromFormattedTime(newDateLastPlayed)
        if (currentLastPlayedTimestamp > newLastPlayedTimestamp):
            newDateLastPlayed = currentDateLastPlayed

    # Set new values on the tags
    currentTags.playCount = str(newPlayCount)
    currentTags.dateLastPlayed = newDateLastPlayed
    currentTags.dateAllPlays = mlu.tags.common.formatValuesListToAudioTagValue(newDateAllPlaysList)

    handler.setTags(currentTags)
    
def writeTagsForNewPlayback(audioFilepath, playbackDateTime):
    '''
    '''
    playbackInstances = AudioFilePlaybackInstances(audioFilepath, [playbackDateTime])
    writeTagsForAudioFilePlaybackInstances(playbackInstances)

def _getAudioFileDuration(audioFilepath):
    try:
        handler = AudioFileMetadataHandler(audioFilepath)
        properties = handler.getProperties()
        return properties.duration

    except (AudioFileFormatNotSupportedError, AudioFileNonExistentError):
        return None
    