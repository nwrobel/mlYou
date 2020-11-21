'''
mlu.mpd.plays

'''
import re

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.misc

from mlu.settings import MLUSettings
import mlu.playstats

def _filterJunkMPDLogLines(mpdLogLines):
    linesWithJunkRemoved = [logLine for logLine in mpdLogLines if (not _mpdLogLineIsJunk(logLine))]
    return linesWithJunkRemoved
        

def collectAudioFilePlaybackDataFromMPDLogLines(mpdLogLines):
    '''
    '''
    # Filter junk entries from the log lines, then delete the old original list of unfiltered log lines
    # this will save memory for large log files
    linesWithJunkRemoved = _filterJunkMPDLogLines(mpdLogLines)
    del mpdLogLines

    audioFilePlaybackDataList = []
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
    preserveLastLogLine = False
    for (index, currentLine) in enumerate(linesWithJunkRemoved):
        # If the current log line is one that indicates a song was played back, get the info from the line
        if (_mpdLogLineIsPlaybackStarted(currentLine)):
            
            audioFilepath = _getSongFilepathFromMPDLogLine(currentLine)
            playbackStartTime = currentLine.timestamp

            # determine playback duration: find out when the song actually stopped by looking ahead at the
            # next log line(s) in the list (the list is ordered by time, least to most recent)
            # We keep checking the next lines until we find a line type that indicates that the song's 
            # playback must have stopped
            playbackStopLogLine = None
            playbackDuration = 0
            logLinesCursorIndex = index
            while (not playbackStopLogLine):
                logLinesCursorIndex += 1

                # Get the next line in the list of LogLines
                try:
                    nextLine = linesWithJunkRemoved[logLinesCursorIndex]

                    # Look for a line that comes after the playback start line that indicates the song playback ended: 
                    # - indicates another song started playing
                    # - indicates that the MPD client was disconnected/closed
                    if (_mpdLogLineIsPlaybackStarted(nextLine) or _mpdLogLineIsException(nextLine) or _mpdLogLineIsClosedOrOpen(nextLine)):
                        playbackStopLogLine = nextLine

                        # Use the timestamp of this playback stopped line to find the playback duration
                        # Get the playback duration from the difference b/w playback stop and start times
                        playbackStopTime = playbackStopLogLine.timestamp
                        playbackDuration = playbackStopTime - playbackStartTime

                # If the list is out of bounds, we are at the end of the list, and we have no way to know what the play duration is, so
                # leave playbackDuration at 0, which represents this ambiguity - this song playback line will be preserved in the log file,
                # and we will not make a PlaybackInstance for it right now (we assume that the next round of log lines will have a stop playback indicator)
                # Also break from the loop, since no playback stop line was found
                except IndexError:
                    preserveLastLogLine = True
                    break

            # Create the playbackInstance object from the values we found for this playback and add it to the list
            # (if the playback duration was found - if not, don't make a playback instance for the last playback)
            if (not preserveLastLogLine):
                playbackInstance = mlu.playstats.AudioFilePlaybackInstance(
                    playTimeStart=playbackStartTime, 
                    playTimeDuration=playbackDuration
                )

                thisAudioFilePlaybackData = [playbackData for playbackData in audioFilePlaybackDataList if (playbackData.audioFilepath == audioFilepath)]
                if (thisAudioFilePlaybackData):
                    thisAudioFilePlaybackData[0].playbackInstances.append(playbackInstance)
                else:
                    thisAudioFilePlaybackData = mlu.playstats.AudioFilePlaybackData(
                        audioFilepath=audioFilepath,
                        playbackInstances=[playbackInstance]
                    )
                    audioFilePlaybackDataList.append(thisAudioFilePlaybackData)

    return {
        'playbackDataList': audioFilePlaybackDataList,
        'preserveLastLogLine': preserveLastLogLine
    }

def _mpdLogLineIsJunk(logLine):
    if (
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="exception: Failed to register ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="zinc mpd: exception: Failed to register ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="inotify: Failed to open directory ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="zinc mpd: inotify: Failed to open directory ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="update: updating ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="zinc mpd: update: updating ")
    ):
        return True
    else:
        return False    

def _mpdLogLineIsPlaybackStarted(logLine):
    '''
    '''
    if (
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="player: played ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="zinc mpd: player: played ")
    ):
        return True
    else:
        return False

# TODO: allow machine host name to be passed (replace "zinc mpd" with "<hostname> mpd")
def _mpdLogLineIsException(logLine):
    '''
    Checks whether or not the given MPDLogLine instance represents/means that an exception occured
    with MPD - this indicates, with a preceding playback line, that playback stopped here
    
    Returns boolean, true if it is a playback started line.
    '''
    if (
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="errno: ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="exception: ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="zinc mpd: errno: ") or
        mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="zinc mpd: exception: ")
    ):
        return True
    else:
        return False

def _mpdLogLineIsClosedOrOpen(logLine):
    '''
    '''
    if (
        (
            mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="client: ") or
            mypycommons.misc.stringStartsWith(inputString=logLine.text, startsWith="zinc mpd: client: ")
        ) and
        (
            "closed" in logLine.text or
            "opened" in logLine.text
        )
    ):
        return True
    else:
        return False

def _getSongFilepathFromMPDLogLine(logLine):
    '''
    Parses the given MPDLogLine and returns the filepath for the audio file that was played/mentioned
    in this log line.
    '''
    partialPath = re.findall('"([^"]*)"', logLine.text)[0]
    fullPath = mypycommons.file.JoinPaths(MLUSettings.musicLibraryRootDir, partialPath)
    return fullPath
   









