import re 
import mutagen
from prettytable import PrettyTable
from shutil import copyfile
from time import gmtime, strftime
import argparse
from datetime import datetime as datetime2
import datetime 
import pathlib

#------------------------------------------------------------------------------------
def getPlayMap(mpdLogFilepath):
    
    mpdLogFile = open(mpdLogFilepath, "r+")
    playMap = {}
    
    now = datetime.datetime.now()
    currentYear = str(now.year)
    
    for line in mpdLogFile:
        if "player: played" in line: 
            song = getSongFromMPDLogLine(line)
            timePlayed = getTimestampFromMPDLogLine(line, currentYear)
            
            try:
                playMap[song].append(timePlayed)
                
            except KeyError:
                playMap[song] = []
                playMap[song].append(timePlayed)
       
    mpdLogFile.close()
    return playMap

#------------------------------------------------------------------------------------
def printPlayMap(playMap):
    
    table = PrettyTable(['Song', 'Play timestamps', 'Add to play_count'])
    for song, playTimes in playMap.items():
        playDates = timestampsToDates(playTimes)
        additionalPlays = len(playDates)
        table.add_row([song, playDates, additionalPlays])
    
    print(table)

#------------------------------------------------------------------------------------
def timestampToDate(timestamp):
    
    return datetime2.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

#------------------------------------------------------------------------------------
def timestampsToDates(timestamps):
    
    dates = []
    for timestamp in timestamps:
        date = timestampToDate(timestamp)
        dates.append(date)
        
    return dates

#------------------------------------------------------------------------------------    
def timestampToFoobarFormat(timestamp):
    
    foobarTimeFormat = (timestamp + 11644473600) * 10000000
    foobarTimeFormat = format(foobarTimeFormat, ".0f")
    return foobarTimeFormat

#------------------------------------------------------------------------------------    
def updatePlayCount(songFilePath, additionalPlays):
    
    audioFile = mutagen.File(songFilePath)
         
    try:
        # Make sure all items in the library have the play count tags name
        # as "play_count", not "plays", "play_counter", etc
        previousPlaycount = audioFile['play_count'][0]
    except KeyError:
        previousPlaycount = 0
         
    newPlaycount = int(additionalPlays) + int(previousPlaycount)
    audioFile['play_count'] = str(newPlaycount)
    audioFile.save()
    
    print(songFilePath, " playcount changed from ", previousPlaycount, " to ", newPlaycount)
    
 #------------------------------------------------------------------------------------    
def updatePlayTimes(songFilePath, playTimes): 
     
    mostRecentPlaytime = max(playTimes)
    leastRecentPlaytime = min(playTimes)
    mostRecentPlaytimeFoobar = int(timestampToFoobarFormat(mostRecentPlaytime))
    leastRecentPlaytimeFoobar = int(timestampToFoobarFormat(leastRecentPlaytime))
    
    audioFile = mutagen.File(songFilePath)
         
    try:
        # If the last_played_timestamp is set, we assume that the first_played_timestamp
        # is set, as well.
        
        # If the last played data in song exists...
        songLastPlayedData = int(audioFile['last_played_timestamp'][0])
        
        # Check if the most recent play from MPD is greater than the last_played_timestamp.
        # If so, we want to update the last_played_timestamp to that of MPDs most recent playtime
        if (mostRecentPlaytimeFoobar > songLastPlayedData):
            audioFile['last_played_timestamp'] = str(mostRecentPlaytimeFoobar) 
            
            print(songFilePath, " last_played_timestamp changed from ", songLastPlayedData, " to ", mostRecentPlaytimeFoobar, " which is ", timestampToDate(mostRecentPlaytime)) 
        
        else: 
            print(songFilePath, " last_played_timestamp is greater than or equal the most recent recorded MPD play. Keeping the file's original value")     
        
        # Otherwise, we do nothing, leaving the last_played_timestamp alone
    
    # If the last_played_timestamp is not set on the song, we assume it has never been played
    # and hence update the first_played timestamp as well with the first play in MPD
    except KeyError:
        audioFile['last_played_timestamp'] = str(mostRecentPlaytimeFoobar)
        audioFile['first_played_timestamp'] = str(leastRecentPlaytimeFoobar)
        
        print(songFilePath, " last_played_timestamp was empty, setting value to ", mostRecentPlaytimeFoobar, " which is ", timestampToDate(mostRecentPlaytime)) 
        print(songFilePath, " first_played_timestamp was empty, setting value to ", leastRecentPlaytimeFoobar, " which is ", timestampToDate(leastRecentPlaytime)) 
         
    audioFile.save()
    
#------------------------------------------------------------------------------------    
def getArchiveLogFilename():
    time = strftime("%Y-%m-%d %H.%M.%S", gmtime())
    archiveLogFilename = "mpd-" + time + ".log"
    return archiveLogFilename

#------------------------------------------------------------------------------------    
def archiveLogFile(mpdLogFilepath, mpdLogArchiveDir):
    
    # Makes the archive file directory if it doesn't exist   
    pathlib.Path(mpdLogArchiveDir).mkdir(exist_ok=True)
    
    # get full filepath
    archiveLogFilepath = mpdLogArchiveDir + getArchiveLogFilename()
    
    # Copy the mpd.log file to the archives under a new name (timestamped)
    copyfile(mpdLogFilepath, archiveLogFilepath)
    
    # Delete the contents of mpd.log, so that the file is 'reset'
    # and we cannot run the script again and mess up the tag values on songs
    open(mpdLogFilepath, "w").close()
    
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
def run():

    parser = argparse.ArgumentParser()
    parser.add_argument("musicDir", help="The root directory of the music library")
    parser.add_argument("-mpdLogs", help="The root directory of the mpd logs")
    args = parser.parse_args()
    
    musicDir = args.musicDir
    mpdDir = args.mpdLogs
    mpdLogFilepath = mpdDir + "mpd.log"
    mpdLogArchiveDir = mpdDir + "parsed-already/"
    
    playMap = getPlayMap(mpdLogFilepath)
     
    print("The following changes are about to be written to the audio library:")
    printPlayMap(playMap)
     
    answer = input("Do you wish to continue? [y/n]: ")
      
    if answer == "y":
        for song, playTimes in playMap.items():
            songFilePath = musicDir + song
            additionalPlays = len(playTimes)
             
            updatePlayCount(songFilePath, additionalPlays)
            updatePlayTimes(songFilePath, playTimes)
         
        print("Finished writing out data to song tags")
        print("Starting the archive procedure on mpd.log....")
        archiveLogFile(mpdLogFilepath, mpdLogArchiveDir)
        
        print("#################### All operations complete #############################")
              
    else:
        print("okay, exiting")

###################################################################################################################3

run()
    

