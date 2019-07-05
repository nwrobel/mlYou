'''
Created on May 5, 2019

@author: nick.admin

This module handles data processing of MPD logs in order to retreive playback-related information
for files in the music library.

Handles forming data structures from all the read-in log lines into usable info: an array of PlaybackInstance objects
instances - each instance has 4 properties:
- songFilepath
- playStartTime
- instancePlayDuration
- actualPlayDuration
'''
import re 
from datetime import datetime
import dateutil.relativedelta


import mlu.mpd.logs



# Returns a list of lines which contain playback information (filters out the non-info lines)
def GetPlaybackLogFileLines(logFileLines):
    
    playbackLogFileLines = []
    
    for line in logFileLines:
        if "player: played" in line:
            playbackLogFileLines.append(line)
        

def LogLineIsPlayback(logLine):
    return ("player: played" in logLine.text)

def LogLineIsMPDClosed(logLine):
    return ( ("client: [" in logLine.text) and ("] closed" in logLine.text) )


#------------------------------------------------------------------------------------    
def GetSongFilepathFromMPDLogLine(logLine):
    
    name = re.findall('"([^"]*)"', logLine.text)[0]
    return name

#-------------------------------

class PlaybackInstance:
    def __init__(self, songFilepath, playbackStartTime, playbackDuration):
        self.songFilepath = songFilepath
        self.playbackStartTime = playbackStartTime
        self.playbackDuration = playbackDuration
        self.songDuration = self.GetSongDuration()

        if (self.playbackDuration == 1):
            self.playbackDuration = self.songDuration

    # Use filepath to get the file properties, use the duration property
    def GetSongDuration(self):
        return ''

#---------------------------------------
    # for line in playbackLogLines:
    #     #playbackTimestamp = getTimestampFromMPDLogLine(line, currentYear)
    #     songPlayedFilePath = getSongFromMPDLogLine(line)
        
    #     try:
    #         playbackData[songPlayedFilePath].append(playbackTimestamp)
            
    #     except KeyError:
    #         playbackData[songPlayedFilePath] = []
    #         playbackData[songPlayedFilePath].append(playbackTimestamp)
        

# create MPDLogsHandler instance and use it to get the logline array
# go through each item in logline array:
#       check/identify if current line is a 'playback' line (song played, song started/resumed, etc): if so:
#           take note of the song filepath
#           take note of the timestamp of the play start
#           check the next consecutive line (logline coming right after it) to see what happened next
#             repeat this until we find a line to see if song was stopped, client exit, played another song, etc
#           based on this, calculate the play duration by taking the difference of the timestamps b/w play start
#             logline and the logline that indicates when play ended
#           Use the song filepath to lookup the actual playback duration of the audio file - calculated play duration
#             should be no longer than this - if it is, set it to same as actual play duration
#             (ex: if song play is last log line - no indication when play stopped - set duraton to song's duration)
#           Make the PlaybackInstance object from these 4 properties found
#       Have loop go to the next line - we will do the above again next time we hit the next consecutive 'playback' line
#
class MPDPlaybackInstanceCollector:
    def __init__(self, mpdLogFilepath):
        self.mpdLogPath = mpdLogFilepath

    def CollectPlaybackInstances(self):
        allPlaybackInstances = self.GetPlaybackData()
        validPlaybackInstances = FilterFalsePlaybacks(allPlaybackInstances)
        return validPlaybackInstances

    # Returns playback data based on all data found in the logs from MPDLogsHandler
    # Creates the data structure described in comment header block
    def GetPlaybackData(self):
        mpdLogHandler = mlu.mpd.logs.MPDLogsHandler(mpdLogFilepath=self.mpdLogPath)
        mpdLogLines = mpdLogHandler.GetProcessedLogLines()
        allPlaybackInstances = []

        for (index, currentLine) in enumerate(mpdLogLines):
            # If the current log line is one that indicates a song was played back,
            # get the song filepath, timestamp, and playback duration and make a PlaybackInstance object
            if (LogLineIsPlayback(currentLine)):
                songFilepath = GetSongFilepathFromMPDLogLine(currentLine)
                playbackStartTime = currentLine.timestamp

                # determine playback duration: find out when the song actually stopped by looking ahead at the
                # next log line(s) in the list (the list is ordered by time, ascending)
                # We keep checking the next lines until we find one that matches a certain line type that indicates
                # that the song's playback must have stopped
                playbackStopLogLine = None
                playbackDuration = 0
                cursorIndex = index
                while (not playbackStopLogLine):
                    cursorIndex += 1

                    # Get the next line in the list of LogLines
                    try:
                        nextLine = mpdLogLines[cursorIndex]

                        # If the line coming after the playback line indicates that another song started playing or that the MPD client
                        # was disconnected, then this means the song must have stopped playing - save this line and stop the loop
                        if (LogLineIsPlayback(nextLine) or LogLineIsMPDClosed(nextLine)):
                            playbackStopLogLine = nextLine

                    # If the list is out of bounds, we are at the end of the list (most recent item is a playback), and we have no way to know what the play duration is
                    # we assume it is the duration of the song by setting it to 1 - we still want to count this as a playback
                    # Set playback duration: we break from the loop, no need to try to find playback stop time anymore
                    except IndexError:
                        playbackDuration = 1
                        break

            # If the playback duration was not set during the except block in the loop, get it the standard way:
            if (not playbackDuration):
                # Use the playbackStopLogLine's timestamp to tell when the playback stopped
                playbackStopTime = playbackStopLogLine.timestamp
                # Get the playback duration from the difference b/w playback stop and start times (represented as a timestamp)
                playbackDuration = SubtractTimestamps(leftTimestamp=playbackStopTime, rightTimestamp=playbackStartTime)

            # Create the playbackInstance object from the values we found for this playback and add it to the list
            allPlaybackInstances.append( PlaybackInstance(songFilepath=songFilepath, playbackStartTime=playbackStartTime, playbackDuration=playbackDuration) )

        return allPlaybackInstances

   
#------------------------------------------------------------------------------------  
#  from this PlaybackInstance array, use the 2 duration properties on each item in the array to 
# compare them to each other and determine whether or not to count that instance as a "true play" or a skip
# do this in another function - filter out the ones that aren't true plays (not played long enough, etc)
#
# for the array objects remaining,  these objects will be 
# passed to another module to be displayed in the UI, cached, compared with the current file tag values,
# and then finally used to update the current tags for these song files  
def FilterFalsePlaybacks(playbackInstances):
    return playbackInstances



#------------------------------------------------------------------------------------
def SubtractTimestamps(leftTimestamp, rightTimestamp):

    leftDt = datetime.datetime.fromtimestamp(leftTimestamp)
    rightDt = datetime.datetime.fromtimestamp(rightTimestamp)
    diffDt = dateutil.relativedelta.relativedelta (leftDt, rightDt)

    return datetime.datetime.timestamp(diffDt)
    

