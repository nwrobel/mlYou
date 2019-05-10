#--------------------------------------------------------------------------------------------------
def PrintPlaybackDataTable(playbackData):
    
    # (Message) "Log files span dates between <datetimeEarliest> to <datetimeLatest>"
    
    # Playmap:
    # SongTitle - Artist - NumPlays
    
    table = PrettyTable(['Song Title', 'Artist', 'Plays'])
    
    for songFilePath, playbackTimes in playbackData.items():  
        songTitle = '' # mlu.tags.commontags.GetTitle(songFilePath)
        artist = ''   # mlu.tags.commontags.GetArtist(songFilePath)
        plays = len(playbackTimes)
        table.add_row([song, artist, plays])
    
    print(table)