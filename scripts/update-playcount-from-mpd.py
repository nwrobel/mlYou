'''
@author: Nick Wrobel

First Created: 3/5/19
Last Modified: 5/10/19

Argument-based script to allow the user to update the "Play Count" tags on their music files, based
on playback data contained within MPD (Media Player Daemon) server log files. 
'''

import argparse
from prettytable import PrettyTable

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import setup
setup.PrepareScriptsForExecution()

import mlu.mpd.playstats
import mlu.tags.common
import mlu.app.common
import mlu.cache.io

#--------------------------------------------------------------------------------------------------
def PrintPlaybackDataTable(songPlaybackRecords):
    
    # Create a table, which will have these 4 columns with corresponding header titles
    table = PrettyTable(['Song Title', 'Artist', '# Plays', 'Play Times'])

    for songPlaybackRecord in songPlaybackRecords:
        # Get the common tags so we can display the ones we need to in the playback table for this song
        songTags = mlu.tags.common.GetCommonTags(songFilepath=songPlaybackRecord.songFilePath)

        songTitle = songTags['title']
        artist = songTags['artist']
        numPlays = len(songPlaybackRecord.playbackTimes)
        # Get the playback times: for each playback timestamp on this songPlaybackRecord, format it for display
        # and return this formatted timestamp
        playTimes = ( mlu.app.common.FormatTimestampForDisplay(timestamp) for timestamp in songPlaybackRecord.playbackTimes )

        # Add the songPlaybackRecord data we found above to the table as a row
        table.add_row([songTitle, artist, numPlays, playTimes])

    # Display the table
    print(table)

#--------------------------------------------------------------------------------------------------
def GetJSONCacheFilepath(cacheFileID):
    cacheDir = mlu.app.common.JoinPaths(mlu.app.common.GetProjectRoot(), "cache")
    cacheFilename = "mpd-playstats-cache-" + cacheFileID + ".json"
    return mlu.app.common.JoinPaths(cacheDir, cacheFilename)


#--------------------------------------------------------------------------------------------------    
def Run():
    
    # TODO: add param switch for "automated" (no user input required) and for a log file, to send print statements to log instead of console
    # so this can be run as cron job

    print("NOTE: each log file must not span more than 1 year of log entries:")
    print("The difference between the dates of the first and last log line must NOT be more than 1 year\n")
    parser = argparse.ArgumentParser()
    
    parser.add_argument("musicDir", 
                        help="Absolute filepath of the root directory of the music library",
                        type=str)
    
    parser.add_argument("mpdLogsDir", 
                        help="Absolute filepath of the root directory of where the MPD logs are stored on this system",
                        type=str)
    
    args = parser.parse_args()
    

    # Create MPDPlaystatsCollector object and call CollectPlaybackInstances to get the playback instances
    playbackInstanceCollector = mlu.mpd.playstats.MPDPlaybackInstanceCollector(mpdLogFilepath=args.mpdLogsDir)
    playbackInstances = playbackInstanceCollector.GetPlaybackInstances()

    # Pass the playback instances array to a class "SongPlaybackRecordCollector" in the mlu.mpd.playstats module, where it can be compressed down into a simpler form
    # that contains only 1 element for each unique song played (no duplicate song play instances are in the array)
    # We call this form a songPlaybackRecord object
    songPlaybackRecordCollector = mlu.mpd.playstats.SongPlaybackRecordCollector(playbackInstances=playbackInstances)
    songPlaybackRecords = songPlaybackRecordCollector.GetSongPlaybackRecords()

    # Take the SongPlaybackRecord instances display them in table form to the user
    print("The following changes are about to be written to the audio library:")
    PrintPlaybackDataTable(songPlaybackRecords)

    #answer = input("Do you wish to continue? [y/n]: ")


    # Write out 3 cache json files:
    #   current playback instances found
    #   current playstats tag values of the songs that will be updated
    #   new tag values that will be set, based on applying the changes from 1 to the tags in 2

    # Write 1st cache file: SongPlaybackRecords found from MPD
    mlu.cache.io.WriteMLUObjectsToJSONFile(songPlaybackRecords, GetJSONCacheFilepath(1))

    # Write 2nd cache file: current SongPlaystatTags values for each song that will be updated
    songCurrentPlaystatTagsList = []
    for playbackRecord in songPlaybackRecords:
        currentTags = mlu.tags.playstats.GetSongCurrentPlaystatTags(playbackRecord.songFilepath)
        songCurrentPlaystatTagsList.append(currentTags)

    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=songCurrentPlaystatTagsList, outputFilename=GetJSONCacheFilepath(2))

    # Write 3rd cache file: calculate new playstat tags based on playback instances + old tags
    # and return new, updated SongPlaystatTags values for all the songs
    allSongsNewPlaystatTags = mlu.tags.playstats.GetUpdatedPlaystatTags(songPlaystatTagsList=songCurrentPlaystatTagsList, songPlaybackRecords=songPlaybackRecords)
    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=allSongsNewPlaystatTags, outputFilename=GetJSONCacheFilepath(3))

    # Use tags.playstats module to update/write the new tag values (same ones we just wrote to the 
    # 3rd json cache file)
    tagWriter = mlu.tags.playstats.PlaystatTagWriter(allSongsNewPlaystatTags)
    tagWriter.WritePlaystatTags()


    # use the 3rd json cache file to verify integrity of each song's new values: read in the current,
    # updated playstat tags from the audio files and verify they match the cache file
    
    # VerifySongPlaystatTags(allSongsNewPlaystatTags)








 
      






