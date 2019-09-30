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

TODO: update playback filtering to check if there are 2 or more playbacks of the same song within
about 0-10 min. of each other - these are most likely caused by MPD disconnect/reconnecting and shouldn't be counted
'''
import re 
import mlu.tags.basic
import mlu.common.time


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
# Class representing an instance in which a single playback of an audio file occurred - contains
# details about the playback and its time relation to the total song duration
#
# These instances will be filtered later based on whether or not the playback time is long enough
# compared with the total duration of the song - to remove "false" playbacks
#
# Objects of this type will later be converted into SongPlaybackRecords, which contain data about
# all the playback instances for a single audio file
#
class PlaybackInstance:
    def __init__(self, songFilepath, playbackStartTime, playbackDuration):
        self.songFilepath = songFilepath
        self.playbackStartTime = playbackStartTime
        self.playbackDuration = playbackDuration
        self.songDuration = self.GetSongDuration()

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
    def GetSongDuration(self):
        durationSeconds = mlu.tags.basic.getSongBasicTags(self.songFilepath).durationSeconds
        durationTimestamp = mlu.common.time.convertSecondsToTimestamp(durationSeconds)

        return durationTimestamp


        
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
# These playback instances will be filtered to get the list of playbacks to actually count
# for the playbacks remaining,  these objects will be 
# passed to another module to be displayed in the UI, cached, compared with the current file tag values,
# and then finally used to update the current tags for these song files
#
class PlaybackInstanceCollector:
    def __init__(self, mpdLogLineCollector):
        self.mpdLogLineCollector = mpdLogLineCollector

    def GetPlaybackInstances(self):
        allPlaybackInstances = self.FormPlaybackInstances()
        validPlaybackInstances = FilterFalsePlaybacks(allPlaybackInstances)
        return validPlaybackInstances

    # Returns playback data based on all data found in the logs from MPDLogsHandler
    # Creates the data structure described in comment header block
    def FormPlaybackInstances(self):
        mpdLogLines = self.mpdLogLineCollector.GetMPDLogLines()
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
                # playbackDuration = SubtractTimestamps(leftTimestamp=playbackStopTime, rightTimestamp=playbackStartTime)
                playbackDuration = playbackStopTime - playbackStartTime

            # Create the playbackInstance object from the values we found for this playback and add it to the list
            allPlaybackInstances.append( PlaybackInstance(songFilepath=songFilepath, playbackStartTime=playbackStartTime, playbackDuration=playbackDuration) )

        return allPlaybackInstances

   
#------------------------------------------------------------------------------------  
#  from this PlaybackInstance array, use the 2 duration properties on each item in the array to 
# compare them to each other and determine whether or not to count that instance as a "true play" or a skip
# do this in another function - filter out the ones that aren't true plays (not played long enough, etc)
# 
# 
# Rules for playback instance to be counted as "true" playback:
# - It takes about 30 seconds, due to latency, for a song to be skipped from MPD client, so:
# --- If song duration is at least 2 minutes, playback duration must be at least 25% of the song duration
# --- If song duration is less than 2 minutes, playback duration must be at least 50% of the song duration
#  
def FilterFalsePlaybacks(playbackInstances):

    songDurationThresholdSeconds = 120

    truePlaybackInstances = []
    songDurationThresholdTimestamp = mlu.common.time.convertSecondsToTimestamp(songDurationThresholdSeconds)

    for playbackInstance in playbackInstances:
        # If song duration is at least 2 min. long
        if (playbackInstance.songDuration >= songDurationThresholdTimestamp):
            playbackDurationThreshold = playbackInstance.songDuration * 0.25

        else:
            playbackDurationThreshold = playbackInstance.songDuration * 0.5

        if (playbackInstance.playbackDuration >= playbackDurationThreshold):
            truePlaybackInstances.append(playbackInstance)

    return truePlaybackInstances






#--------------------------------------------------------------------------------------------------
# Pass the playback instances array to a class "SongPlaybackRecordCollector" in the mlu.mpd.playstats module, where it can be compressed down into a simpler form
# that contains only 1 element for each unique song played (no duplicate song play instances are in the array)
# We call this form a SongPlaybackRecord object
#
# 
class SongPlaybackRecord:
    def __init__(self, songFilepath, playbackTimes):
        self.songFilepath = songFilepath
        self.playbackTimes = playbackTimes # should be a list of epoch timestamps


class SongPlaybackRecordCollector:
    def __init__(self, playbackInstanceCollector):
        self.playbackInstanceCollector = playbackInstanceCollector
        self.playbackInstances = []
        self.songPlaybackRecords = [] # ???????????????????????????? do we need this?

    def GetSongPlaybackRecords(self):
        self.playbackInstances = self.playbackInstanceCollector.GetPlaybackInstances()

        # Get a list of all the unique song filepaths by taking the songFilepath property from each object in the playbackInstances array
        allSongFilepaths = list((playback.songFilepath for playback in self.playbackInstances))
        uniqueSongFilepaths = set(allSongFilepaths) # cast this list to a set, elminiating duplicate song filepaths

        # Go thru each song filepath in this unique list:
        #   For each one, get all the playbackInstances this song has (must be at least 1)
        #   Combine these instances into one SongPlaybackRecord by setting the songFilepath and combining the playbackTimes into an array
        #   Add the new SongPlaybackRecord to the master list of these records
        # Return this list of records, so it can be used by the top-level script
        for uniqueSongFilepath in uniqueSongFilepaths:
            playbacksMatchingCurrentSong = self.GetPlaybackInstancesForSongFilepath(uniqueSongFilepath)
            songPlaybackRecord = self.MergePlaybackInstancesIntoSongPlaybackRecord(playbacksMatchingCurrentSong)
            self.songPlaybackRecords.append(songPlaybackRecord)

        return self.songPlaybackRecords


    def GetPlaybackInstancesForSongFilepath(self, songFilepath):
        matchingPlaybackInstances = []

        for playbackInstance in self.playbackInstances:
            if (playbackInstance.songFilepath == songFilepath):
                matchingPlaybackInstances.append(playbackInstance)

        return matchingPlaybackInstances


    def MergePlaybackInstancesIntoSongPlaybackRecord(self, songPlaybackInstances):
        # Get the song filepath - all of the playbackInstances should have the same song filepath, so we can just use the first playbackinstance element
        songFilepath = songPlaybackInstances[0].songFilepath
        songPlaybackTimes = list((playback.playbackStartTime for playback in songPlaybackInstances))

        return ( SongPlaybackRecord(songFilepath=songFilepath, playbackTimes=songPlaybackTimes) )


    def GetAllSongFilepaths(self):
        paths = (songPlaybackRecord.songFilepath for songPlaybackRecord in self.songPlaybackRecords)
        return paths

