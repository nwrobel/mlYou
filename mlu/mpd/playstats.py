'''
Created on May 5, 2019

@author: nick.admin

This module handles data processing of MPD logs in order to retreive playback-related information
for files in the music library.

Handles forming data structures from all the read-in log lines into usable info: an array of playback
instances - each instance has 3 properties:
- songFilepath
- playStartTime
- instancePlayDuration
- actualPlayDuration
'''
import re 
from datetime import datetime



# Returns a list of lines which contain playback information (filters out the non-info lines)
def GetPlaybackLogFileLines(logFileLines):
    
    playbackLogFileLines = []
    
    for line in logFileLines:
        if "player: played" in line:
            playbackLogFileLines.append(line)
        

# Returns playback data based on all data found in the logs from MPDLogsHandler
# Creates the data structure described in comment header block
def GetPlaybackData():
    
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
    #           Make the DetailedPlaybackInstance object from these 4 properties found
    #       Have loop go to the next line - we will do the above again next time we hit the next consecutive 'playback' line


    # THEN,
    # from this DetailedPlaybackInstance array, use the 2 duration properties on each item in the array to 
    # compare them to each other and determine whether or not to count that instance as a "true play" or a skip
    # do this in another function - filter out the ones that aren't true plays (not played long enough, etc)
    #
    # for the array objects remaining, make a PlaybackInstance object from the DetailedPlaybackInstance object
    # by dropping the two unneeded properties - actual and calculated play duration - these objects will be 
    # passed to another module to be displayed in the UI, cached, compared with the current file tag values,
    # and then finally used to update the current tags for these song files

    for line in playbackLogLines:
        #playbackTimestamp = getTimestampFromMPDLogLine(line, currentYear)
        songPlayedFilePath = getSongFromMPDLogLine(line)
        
        try:
            playbackData[songPlayedFilePath].append(playbackTimestamp)
            
        except KeyError:
            playbackData[songPlayedFilePath] = []
            playbackData[songPlayedFilePath].append(playbackTimestamp)
        


    
#------------------------------------------------------------------------------------    


#------------------------------------------------------------------------------------    
def getSongFromMPDLogLine(line):
    
    name = re.findall('"([^"]*)"', line)[0]
    return name

#------------------------------------------------------------------------------------

    

