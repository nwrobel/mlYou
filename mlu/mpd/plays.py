
import fnmatch
import re

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.time

from mlu.settings import MLUSettings
from mlu.tags.playstats import Playback

def getPlaybacksFromMPDLogLines(mpdLogLines):
    '''
    '''
    # Filter junk entries from the log lines, then delete the old original list of unfiltered log lines
    # this will save memory for large log files
    linesWithJunkRemoved = _filterJunkMPDLogLines(mpdLogLines)

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
    atLastLogLine = False
    for (index, currentLine) in enumerate(linesWithJunkRemoved):
        # If the current log line is one that indicates a song was played back, get the info from the line
        if (_mpdLogLineIsPlaybackStarted(currentLine)):
            
            audioFilepath = _getSongFilepathFromMPDLogLine(currentLine)
            playbackStartTime = currentLine.epochTimestamp

            # determine playback duration: find out when the song actually stopped by looking ahead at the
            # next log line in the list (the list is ordered by time, least to most recent)
            # This next line indicates when the song playback ended
            try:
                nextLine = linesWithJunkRemoved[index + 1]

                # Get the playback duration from the difference b/w playback stop and start times
                playbackStopTime = nextLine.epochTimestamp
                playbackDuration = playbackStopTime - playbackStartTime

            # If the list is out of bounds, we are at the end of the list, and we have no way to know what the play duration is,
            # so we don't add this song to the list of playbacks - this song playback line will be preserved in the log file
            # and we will not make a Playback for it right now (the next round of log lines should have a stop playback indicator)
            except IndexError:
                atLastLogLine = True

            # Create the playbackInstance object from the values we found for this playback and add it to the list
            # (if the playback duration was found - if not, don't make a playback instance for the last playback)
            if (not atLastLogLine):
                playbackDateTime = mypycommons.time.formatTimestampForDisplay(playbackStartTime)
                playbackInstance = Playback(audioFilepath, playbackDateTime, playbackDuration)
                playbackList.append(playbackInstance)

    return playbackList

def getLastPlaybackMPDLogLine(mpdLogLines):
    linesWithJunkRemoved = _filterJunkMPDLogLines(mpdLogLines)
    lastLine = linesWithJunkRemoved[-1]

    if (_mpdLogLineIsPlaybackStarted(lastLine)):
        return lastLine
    else:
        return None

def _filterJunkMPDLogLines(mpdLogLines):
    linesWithJunkRemoved = [logLine for logLine in mpdLogLines if (not _mpdLogLineIsJunk(logLine))]
    return linesWithJunkRemoved

def _mpdLogLineIsJunk(mpdLogLine):
    if (_mpdLogLineIsPlaybackStarted(mpdLogLine) or _mpdLogLineIsClientClosedOrOpen(mpdLogLine)):
        return False
    else:
        return True    

def _mpdLogLineIsPlaybackStarted(mpdLogLine):
    '''
    '''
    if (fnmatch.fnmatchcase(mpdLogLine.text, "*player: played \"*\"")):
        return True
    else:
        return False

def _mpdLogLineIsClientClosedOrOpen(mpdLogLine):
    '''
    '''
    if (fnmatch.fnmatchcase(mpdLogLine.text, "*client: * opened from*") or
        fnmatch.fnmatchcase(mpdLogLine.text, "*client: * closed")):
        return True
    else:
        return False

def _getSongFilepathFromMPDLogLine(mpdLogLine):
    '''
    Parses the given MPDLogLine and returns the filepath for the audio file that was played/mentioned
    in this log line.
    '''
    partialPath = re.findall('"([^"]*)"', mpdLogLine.text)[0]
    fullPath = mypycommons.file.joinPaths(MLUSettings.userConfig.audioLibraryRootDirectory, partialPath)
    return fullPath