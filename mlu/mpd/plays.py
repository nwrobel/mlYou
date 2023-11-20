from typing import List, Optional

import fnmatch
import re

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.time

from mlu.mpd.log import MpdLogProvider, MpdLogLine
from mlu.tags.playstats.common import Playback
from mlu.settings import MLUSettings

class MpdPlaybackProvider:
    ''' 
    '''
    def __init__(self, mluSettings: MLUSettings, commonLogger: mypycommons.logger.CommonLogger) -> None:
        if (not mluSettings):
            raise TypeError("mluSettings not passed")
        if (commonLogger is None):
            raise TypeError("CommonLogger not passed")
        
        self._audioLibraryRootDir = mluSettings.userConfig.audioLibraryRootDir
        self._logger = commonLogger.getLogger()
        self._mpdLogProvider = MpdLogProvider(mluSettings, commonLogger)
        self._mpdLogLines = None

    def getPlaybacks(self) -> List[Playback]:
        '''
        '''
        self._mpdLogLines = self._mpdLogProvider.getLines()
        linesWithJunkRemoved = self._getJunkFilteredMpdLogLines()

        playbackList = []
        # go through each item in logline array:
        #       check/identify if current line is a 'playback' line (song played, song started/resumed, etc): if so:
        #           take note of the song filepath
        #           take note of the timestamp of the play start
        #           check the next consecutive line (logline coming right after it) to see what happened next
        #             repeat this until we find a line to see if song was stopped, client exit, played another song, etc
        #           based on this, calculate the play duration by taking the difference of the timestamps b/w play start
        #             logline and the logline that indicates when play ended
        # Have loop go to the next line - we will do the above again next time we hit the next consecutive 'playback' line

        # Go through each line in the list of log lines
        for (index, currentLine) in enumerate(linesWithJunkRemoved):
            # If the current log line is one that indicates a song was played back, get the info from the line
            if (self._mpdLogLineIsPlaybackStarted(currentLine)):
                
                audioFilepath = self._getFilepathFromMpdLogLine(currentLine)
                playbackStartTime = currentLine.dateTime

                # determine playback duration: find out when the song actually stopped by looking ahead at the
                # next log line in the list (the list is ordered by time, least to most recent)
                # This next line indicates when the song playback ended
                try:
                    nextLine = linesWithJunkRemoved[index + 1]

                    # Get the playback duration from the difference b/w playback stop and start times
                    playbackStopTime = nextLine.dateTime
                    playbackTimedelta = playbackStopTime - playbackStartTime

                # If the list is out of bounds, we are at the end of the list, and we have no real way to know what the play duration is,
                # To handle this, we just will set timedelta to 0 (count this as a play)
                except IndexError:
                    self._logger.warning("Last playback line in log reached, unable to determine exact play duration for final 'played' line")
                    playbackTimedelta = None

                playbackInstance = Playback(audioFilepath, playbackStartTime, playbackTimedelta)
                playbackList.append(playbackInstance)

        return playbackList

    def getLastPlaybackMpdLogLine(self) -> Optional[MpdLogLine]:
        ''' 
        '''
        linesWithJunkRemoved = self._getJunkFilteredMpdLogLines()
        lastLine = linesWithJunkRemoved[-1]

        if (self._mpdLogLineIsPlaybackStarted(lastLine)):
            return lastLine
        else:
            return None

    def _getJunkFilteredMpdLogLines(self) -> List[MpdLogLine]:
        ''' 
        '''
        linesWithJunkRemoved = [logLine for logLine in self._mpdLogLines if (not self._mpdLogLineIsJunk(logLine))]
        return linesWithJunkRemoved

    def _mpdLogLineIsJunk(self, mpdLogLine: MpdLogLine) -> bool:
        ''' 
        '''
        if (self._mpdLogLineIsPlaybackStarted(mpdLogLine) or self._mpdLogLineIsClientClosedOrOpen(mpdLogLine)):
            return False
        else:
            return True    

    def _mpdLogLineIsPlaybackStarted(self, mpdLogLine: MpdLogLine) -> bool:
        '''
        '''
        if (fnmatch.fnmatchcase(mpdLogLine.text, "*player: played \"*\"")):
            return True
        else:
            return False

    def _mpdLogLineIsClientClosedOrOpen(self, mpdLogLine: MpdLogLine) -> bool:
        '''
        '''
        if (fnmatch.fnmatchcase(mpdLogLine.text, "*client: * opened from*") or
            fnmatch.fnmatchcase(mpdLogLine.text, "*client: * closed")):
            return True
        else:
            return False

    def _getFilepathFromMpdLogLine(self, mpdLogLine: MpdLogLine) -> str:
        '''
        Parses the given MPDLogLine and returns the filepath for the audio file that was played/mentioned
        in this log line.
        '''
        partialPath = re.findall('"([^"]*)"', mpdLogLine.text)[0]
        fullPath = mypycommons.file.joinPaths(self._audioLibraryRootDir, partialPath)
        return fullPath