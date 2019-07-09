'''
mlu.tags.playstats

This module deals with reading and writing playback-related tag information on audio files.
'''

from collections import OrderedDict

# Class representing the data structure holding the various tag values of a song for the playstats tags
# that we are dealing with - 3 tags: play_count, time_last_played, all_times_played
class SongPlaystatTags:
    def __init__(self, songFilepath, playCount, timeLastPlayed, allTimesPlayed):
        self.songFilepath = songFilepath
        self.playCount = playCount
        self.timeLastPlayed = timeLastPlayed
        self.allTimesPlayed = allTimesPlayed

    def PrepareForJSON(self):
        classDataDict = OrderedDict()
        classDataDict['songFilepath'] = self.songFilepath
        classDataDict['playCount'] = self.playCount
        classDataDict['timeLastPlayed'] = self.timeLastPlayed
        classDataDict['allTimesPlayed'] = self.allTimesPlayed

        return classDataDict
 






