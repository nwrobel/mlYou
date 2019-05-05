'''
mlu.tags.playstats

This module deals with reading and writing playback-related tag information on audio files.
'''

from datetime import datetime


#--------------------------------------------------------------------------------------------------
def timestampToDate(timestamp):
    
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

#--------------------------------------------------------------------------------------------------
def timestampsToDates(timestamps):
    
    dates = []
    for timestamp in timestamps:
        date = timestampToDate(timestamp)
        dates.append(date)
        
    return dates

#--------------------------------------------------------------------------------------------------
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
    

#--------------------------------------------------------------------------------------------------
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
    
    
def WriteTagsFromPlaybackData(playbackData):
    
    for song, playTimes in playMap.items():
    songFilePath = musicDir + song
    additionalPlays = len(playTimes)
     
    updatePlayCount(songFilePath, additionalPlays)
    updatePlayTimes(songFilePath, playTimes)



