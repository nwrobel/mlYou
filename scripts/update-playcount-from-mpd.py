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
import mlu.common.time
import mlu.common.file
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
        playTimes = ( mlu.common.time.FormatTimestampForDisplay(timestamp) for timestamp in songPlaybackRecord.playbackTimes )

        # Add the songPlaybackRecord data we found above to the table as a row
        table.add_row([songTitle, artist, numPlays, playTimes])

    # Display the table, begin and end it with a newline to look better
    print("\n" + table + "\n")

#--------------------------------------------------------------------------------------------------
def GetJSONCacheFilepath(cacheFileID):
    cacheDir = mlu.common.file.JoinPaths(mlu.common.file.GetProjectRoot(), "cache")
    cacheFilename = "mpd-playstats-cache-" + cacheFileID + ".json"
    return mlu.common.file.JoinPaths(cacheDir, cacheFilename)


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

    # Dependency injection - chain:
    # MPDLogsHandler -> MPDPlaybackInstanceCollector -> SongPlaybackRecordCollector
    # 

    print("Building playback data from log files...")
    playbackInstanceCollector = mlu.mpd.playstats.MPDPlaybackInstanceCollector(mpdLogFilepath=args.mpdLogsDir)
    playbackInstances = playbackInstanceCollector.GetPlaybackInstances()

    # Pass the playback instances array to a class "SongPlaybackRecordCollector" in the mlu.mpd.playstats module, where it can be compressed down into a simpler form
    # that contains only 1 element for each unique song played (no duplicate song play instances are in the array)
    # We call this form a songPlaybackRecord object
    print("Consolidating playback data...")
    songPlaybackRecordCollector = mlu.mpd.playstats.SongPlaybackRecordCollector(playbackInstances=playbackInstances)
    songPlaybackRecords = songPlaybackRecordCollector.GetSongPlaybackRecords()


    # Write out 3 cache json files:
    #  1) current playback instances found
    #  2) current playstats tag values of the songs that will be updated
    #  3) new tag values that will be set, based on applying the changes from 1 to the tags in 2

    # Write 1st cache file: SongPlaybackRecords found from MPD
    print("Cache step 1: Writing newly found playback data...")
    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=songPlaybackRecords, outputFilepath=GetJSONCacheFilepath(1))

    # Write 2nd cache file: current SongPlaystatTags values for each song that will be updated
    print("Cache step 2: Writing current playstat tags for all songs...")
    songsToUpdate = (playbackRecord.songFilePath for playbackRecord in songPlaybackRecords)
    songsCurrentPlaystatTags = mlu.tags.playstats.ReadCurrentPlaystatTagsFromSongs(songFilepaths=songsToUpdate)
    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=songsCurrentPlaystatTags, outputFilepath=GetJSONCacheFilepath(2))

    # Write 3rd cache file: calculate new playstat tags based on playback instances + old tags
    # and return new, updated SongPlaystatTags values for all the songs
    print("Cache step 3: Writing new computed tag values (current tags + playback data) for all songs...")
    tagUpdateResolver = mlu.tags.playstats.SongPlaystatTagsUpdateResolver(songPlaybackRecords=songPlaybackRecords, songsPlaystatTags=songsCurrentPlaystatTags)
    songsNewPlaystatTags = tagUpdateResolver.GetUpdatedPlaystatTags()
    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=songsNewPlaystatTags, outputFilepath=GetJSONCacheFilepath(3))

    print("Playback data gathering, caching, and tag preparation complete!\n")

    # Take the SongPlaybackRecord instances display them in table form to the user, once everything
    # has been prepared and we are ready to write the updated tags
    print("The following playstat tag updates are ready to write to the audio library:")
    PrintPlaybackDataTable(songPlaybackRecords)

    # continue if we want to make the changes, otherwise we exit
    writeChanges = input("Do you wish to continue? [y/n]: ")

    if ( (writeChanges != 'y') and (writeChanges != 'Y') ):
        print("Exiting due to choice of user")
        return
    

    # write the new, updated tag values (same ones we just wrote to the 3rd json cache file) to the
    # audio files
    mlu.tags.playstats.WritePlaystatTagsToSongs(songsPlaystatTags=songsNewPlaystatTags)

    # Verify the changes made: read in the current, now updated playstat tags from the audio files 
    # and verify they match the updated tags list built earlier
    tagIssueSongs = mlu.tags.playstats.FindSongsWithWrongPlaystatTags(expectedSongsPlaystatTags=songsNewPlaystatTags)

    if (tagIssueSongs):
        print("Playstats tag verification failed: expected playstat tags and actual tags do not match for song(s):")
        for song in tagIssueSongs:
            print(song)

        raise("\nERROR: playstat tag writing failed - examine the above files to resolve incorrect tag data")

        







 
      






