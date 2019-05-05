'''
Created on May 5, 2019

@author: nick.admin

This module handles data processing of MPD logs in order to retreive playback-related information
for files in the music library.
'''
import re 
from datetime import datetime



# Returns a list of lines which contain playback information (filters out the non-info lines)
def GetPlaybackLogFileLines(logFileLines):
    
    playbackLogFileLines = []
    
    for line in logFileLines:
        if "player: played" in line:
            playbackLogFileLines.append(line)
        

# Returns playback data based on all data found in the logs
# Playback data is a dictorary mapping song paths to lists containing the timestamps of when that
# song was played
def GetPlaybackData():
    
    playbackData = {}
    
    allLogLines = mlu.mpd.logs.GetAllLogLines()
    playbackLogLines = GetPlaybackLogFileLines(allLogLines)

    for line in playbackLogLines:
        playbackTimestamp = getTimestampFromMPDLogLine(line, currentYear)
        songPlayedFilePath = getSongFromMPDLogLine(line)
        
        try:
            playbackData[songPlayedFilePath].append(playbackTimestamp)
            
        except KeyError:
            playbackData[songPlayedFilePath] = []
            playbackData[songPlayedFilePath].append(playbackTimestamp)
        


    
#------------------------------------------------------------------------------------    
def getTimestampFromMPDLogLine(line, currentYear):
    
    parts = line.split(" ")
    time = parts[0] + " " + parts[1] + " " +  currentYear + " " + parts[2]
    print(time)
    datetime = datetime2.strptime(time, "%b %d %Y %H:%M")
    epochTime = datetime.timestamp()
    print(epochTime)
    
    return epochTime

#------------------------------------------------------------------------------------    
def getSongFromMPDLogLine(line):
    
    name = re.findall('"([^"]*)"', line)[0]
    return name

#------------------------------------------------------------------------------------

    

