from typing import List
from datetime import datetime, timedelta

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.time
import mlu.tags.io
from com.nwrobel.mypycommons.utils import stringIsNullOrEmpty, listIsNullOrEmpty

class Playback:
    ''' 
    '''
    def __init__(self, audioFilepath: str, dateTime: datetime, duration: timedelta):
        if (stringIsNullOrEmpty(audioFilepath)):
            raise ValueError("audioFilepath empty or not passed")
        if (dateTime is None):
            raise ValueError("dateTime not passed")
  
        self.audioFilepath = audioFilepath
        self.dateTime = dateTime
        self.duration = duration

    def __lt__(self, other):
        ''' 
        Used to define how to compare two Playback objects.
        Needed in order to sort objects of this class.
        ''' 
        if not isinstance(other, Playback):
            raise ValueError("Cannot compare equality between Playback and {} type object".format(str(type(other))))
        else:
            check1 = (self.audioFilepath < other.audioFilepath)
            check2 = (self.dateTime < other.dateTime)
            
            return (check1 or check2) 

    # def __hash__(self):
    #     ''' 
    #     Used to define how to hash the data of this class for uniqueness representation.
    #     Needed in order to create set objects of this class.
    #     ''' 
    #     return hash(self.value)

    # def getDictForJsonFileOutput(self):
    #     return { 
    #         'audioFilepath': self.audioFilepath, 
    #         'playbackDateTime': mypycommons.time.formatDatetimeForDisplay(self.playbackDateTime)
    #     }

class AudioFilePlaybackList:
    ''' 
    '''
    # def __init__(self, audioFilepath: str, dateTimes: List[datetime]) -> None:
    #     self.audioFilepath = audioFilepath

    #     # Sort the playback times, with oldest first
    #     playbackDateTimes.sort()
    #     self.dateTimes = dateTimes
    def __init__(self, playbacks: List[Playback]) -> None:
        if (listIsNullOrEmpty(playbacks)):
            raise ValueError("playbacks empty or not passed")

        # validate
        uniqueAudioFiles = getUniqueAudioFilesFromPlaybacks(playbacks)
        if (len(uniqueAudioFiles) > 1):
            raise ValueError("playbacks list contains playbacks for more than 1 audio file")

        self.audioFilepath = uniqueAudioFiles[0]
        self.playbacks = playbacks

        self.playbacks.sort()

    def getPlaybacksTotal(self) -> int:
        return len(self.playbacks)

    def getPlaybacksDateTimes(self) -> List[datetime]:
        return [x.dateTime for x in self.playbacks]

    def getDictForJsonDataFile(self) -> str:
        playbackTimesFmt = [mypycommons.time.formatDatetimeForDisplay(playback.dateTime) for playback in self.playbacks]
        jsonDict = {
            'audioFilepath': self.audioFilepath,
            'playbacks': []
        }

        for playback in self.playbacks:
            if (playback.duration is not None):
                playbackDuration = str(playback.duration)
            else:
                playbackDuration = None
            playbackDict = {
                'dateTime': mypycommons.time.formatDatetimeForDisplay(playback.dateTime),
                'playbackDuration': playbackDuration
            }
            jsonDict['playbacks'].append(playbackDict)

        return jsonDict

def getUniqueAudioFilesFromPlaybacks(playbacks: List[Playback]) -> List[str]:
    ''' 
    '''
    audioFilePaths = sorted(set([playback.audioFilepath for playback in playbacks]))
    return audioFilePaths

def getAudioFileDuration(audioFilepath: str) -> timedelta:
    ''' 
    '''
    handler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
    properties = handler.getProperties()

    return properties.duration