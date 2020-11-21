'''
mlu.mpd.plays

Author: Nick Wrobel
First Created:  05/05/19
Last Modified:  01/27/20

This module handles data processing of MPDLogLine objects into SongPlaybackInstance objects: it creates
meaningful playback information for songs from the MPD log data given. 

These SongPlaybackInstance objects are not specific to MPD and are a general form for playback data that
can be consumed by other MLU modules. Therefore this module serves as a link between MPD and its log
data and a simple playback instance for single songs.

'''

import re 
import mlu.mpd.logs
import mlu.playback





def collectPlaybackData(mpdLogLines):
    '''
    Takes the list of MPDLogLine objects (given to the class via constructor) and creates a list
    of SongPlaybackInstance objects from them by reading each log line, determining which log lines
    indicate a song playback, and for what song and how long these playbacks ocurred. 

    Returns the list of SongPlaybackInstance objects collected from the mpd logs.
    '''
    allPlaybackInstances = []

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
    for (index, currentLine) in enumerate(self._mpdLogLines):
        # If the current log line is one that indicates a song was played back, get the data
        # required to make a PlaybackInstance from the line and then create the PlaybackInstance
        if (self._MPDLogLineIsPlaybackStarted(currentLine)):
            
            songFilepath = self._getSongFilepathFromMPDLogLine(currentLine)
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
                    nextLine = self._mpdLogLines[logLinesCursorIndex]

                    # Look for a line that comes after the playback start line that indicates the song playback ended: 
                    # - indicates another song started playing
                    # - indicates that the MPD client was disconnected/closed
                    if (self._MPDLogLineIsPlaybackStarted(nextLine) or self._MPDLogLineIsMPDClosed(nextLine)):
                        playbackStopLogLine = nextLine

                    # Use the timestamp of this playback stopped line to find the playback duration
                    # Get the playback duration from the difference b/w playback stop and start times
                    playbackStopTime = playbackStopLogLine.timestamp
                    playbackDuration = playbackStopTime - playbackStartTime

                # If the list is out of bounds, we are at the end of the list, and we have no way to know what the play duration is, so
                # leave playbackDuration at 0, which represents this ambiguity - this song playback will be preserved in the log file,
                # and we will not make a PlaybackInstance for it right now (we assume that the next round of log lines will have a stop playback indicator)
                # Also break from the loop, since no playback stop line was found
                except IndexError:
                    self.preservedAmbiguousFinalPlaybackLine = currentLine
                    break

            # Create the playbackInstance object from the values we found for this playback and add it to the list
            # (if the playback duration was found - if not, don't make a playback instance for the last playback)
            if (playbackDuration != 0):
                allPlaybackInstances.append(
                    mlu.playback.SongPlaybackInstance(
                        songFilepath=songFilepath, 
                        playbackStartTime=playbackStartTime, 
                        playbackDuration=playbackDuration
                    ) 
                )

    return allPlaybackInstances

    def _MPDLogLineIsPlaybackStarted(self, logLine):
        '''
        Checks whether or not the given MPDLogLine instance represents/means that a song playback
        was started.
        
        Returns boolean, true if it is a playback started line.
        '''
        return ("player: played" in logLine.text)

    def _MPDLogLineIsMPDClosed(self, logLine):
        '''
        Checks whether or not the given MPDLogLine instance represents/means MPD was closed and/or
        the client was disconnected, thus any playbacks were stopped.
        
        Returns boolean, true if it is a MPD closed/disconnected line.
        '''
        return ( ("client: [" in logLine.text) and ("] closed" in logLine.text) )

    def _getSongFilepathFromMPDLogLine(self, logLine):
        '''
        Parses the given MPDLogLine and returns the filepath for the audio file that was played/mentioned
        in this log line.
        '''
        name = re.findall('"([^"]*)"', logLine.text)[0]
        return name

   









