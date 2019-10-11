'''
@author: Nick Wrobel

First Created: 3/5/19
Last Modified: 5/10/19

Argument-based script to allow the user to update the "Play Count" tags on their music files, based
on playback data contained within MPD (Media Player Daemon) server log files. 
'''

# TODO: configure, set up, and use logger logging statements instead of print, so messages can be 
# easily saved into files and pruned down based on log importance level

import argparse
from prettytable import PrettyTable

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

# setup logging for this script using MLU preconfigured logger
import mlu.common.logger
mlu.common.logger.initMLULogger()
logger = mlu.common.logger.getMLULogger()

import mlu.mpd.plays
import mlu.mpd.logs
import mlu.tags.basic
import mlu.common.time
import mlu.common.file
import mlu.cache.io

#--------------------------------------------------------------------------------------------------
def PrintPlaybackDataTable(songPlaybackRecords):
    
    # Create a table, which will have these 4 columns with corresponding header titles
    table = PrettyTable(['Song Title', 'Artist', '# Plays', 'Play Times'])

    for songPlaybackRecord in songPlaybackRecords:
        # Get the common tags so we can display the ones we need to in the playback table for this song
        songTags = mlu.tags.basic.getSongBasicTags(songFilepath=songPlaybackRecord.songFilePath)

        numPlays = len(songPlaybackRecord.playbackTimes)
        # Get the playback times: for each playback timestamp on this songPlaybackRecord, format it for display
        # and return this formatted timestamp
        playTimes = ( mlu.common.time.formatTimestampForDisplay(timestamp) for timestamp in songPlaybackRecord.playbackTimes )

        # Add the songPlaybackRecord data we found above to the table as a row
        table.add_row([songTags.title, songTags.artist, numPlays, playTimes])

    # Display the table, begin and end it with a newline to look better
    print("\n" + table + "\n")

#--------------------------------------------------------------------------------------------------
def GetJSONCacheFilepath(cacheFileID ):
    jsonFilename = "mpd-playstats-cache-" + cacheFileID + ".json"
    return mlu.common.file.JoinPaths(mlu.common.file.GetMLUCacheDirectory(), jsonFilename)


#--------------------------------------------------------------------------------------------------    
def Run():
    
    # TODO: add param switch for "automated" (no user input required) and for a log file, to send print statements to log instead of console
    # so this can be run as cron job

    print("NOTE: each log file must not span more than 1 year of log entries:")
    print("The difference between the dates of the first and last log line must NOT be more than 1 year\n")
    parser = argparse.ArgumentParser()
    
    parser.add_argument("musicDir", 
                        help="Absolute filepath of the root directory of the music library on this system.",
                        type=str)
    
    parser.add_argument("mpdLogsDir", 
                        help="Absolute filepath of the root directory where the MPD logs are stored on this system.",
                        type=str)

    parser.add_argument("--noLogfileAgePrompt",
                        help="Skip the user prompt to enter the year last modified for each MPD log file. If skipped, the present year will be used by default.",
                        action='store_true')
    
    args = parser.parse_args()
    
    # Dependency injection - chain:
    # MPDLogsHandler -> MPDPlaybackInstanceCollector -> SongPlaybackRecordCollector
    
    # Pass the playback instances array to a class "SongPlaybackRecordCollector" in the mlu.mpd.plays module, where it can be compressed down into a simpler form
    # that contains only 1 element for each unique song played (no duplicate song play instances are in the array)
    # We call this form a songPlaybackRecord object

    print("Building playback data structures from log files...")
    # MPDLogsManager class
    # PlaybackRecordsManager class

    # New code using the above:
    mpdLogsManager = mlu.mpd.logs.MPDLogsManager(mpdLogDir=args['mpdLogDir'])
    mpdLogsManager.loadMPDLogLines()
    mpdLogLines = mpdLogsManager.getMPDLogLines()

    playbackRecordsManager = mlu.mpd.plays.PlaybackRecordsManager(mpdLogLines=mpdLogLines)
    playbackRecordsManager.buildSongPlaybackRecords()
    songPlaybackRecords = playbackRecordsManager.getSongPlaybackRecords()

    if (playbackRecordsManager.ambiguousPlaybackRecordFound()):
        mpdLogsManager.preserveMostRecentLogLine()

    # old code
    # mpdLogLineCollector = mlu.mpd.logs.MPDLogLineCollector(mpdLogDir=args['mpdLogDir'], promptForLogFileYears=args['noLogfileAgePrompt'])
    # playbackInstanceCollector = mlu.mpd.plays.PlaybackInstanceCollector(mpdLogLineCollector=mpdLogLineCollector)
    # songPlaybackRecordCollector = mlu.mpd.plays.SongPlaybackRecordCollector(playbackInstanceCollector=playbackInstanceCollector)

    # songPlaybackRecords = songPlaybackRecordCollector.GetSongPlaybackRecords()

    # Write out 3 cache json files:
    #  1) current playback instances found
    #  2) current playstats tag values of the songs that will be updated
    #  3) new tag values that will be set, based on applying the changes from 1 to the tags in 2
    print("Caching data...")

    # Write 1st cache file: SongPlaybackRecords found from MPD
    print("Cache step 1: Writing newly found playback data...")
    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=songPlaybackRecords, outputFilepath=GetJSONCacheFilepath(1))

    # Write 2nd cache file: current SongPlaystatTags values for each song that will be updated
    print("Cache step 2: Writing current playstat tags for all songs...")
    songsToUpdate = (playbackRecord.songFilePath for playbackRecord in songPlaybackRecords)
    allSongPlaystatTagsCurrent = mlu.tags.playstats.ReadPlaystatTagsFromSongs(songFilepaths=songsToUpdate)

    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=allSongPlaystatTagsCurrent, outputFilepath=GetJSONCacheFilepath(2))

    # Write 3rd cache file: calculate new playstat tags based on playback instances + old tags
    # and return new, updated SongPlaystatTags values for all the songs
    print("Cache step 3: Writing new computed tag values (current tags + playback data) for all songs...")
    
    # new code:
    allSongPlaystatTagsNew = mlu.tags.playstats.MergeSongPlaystatTagsWithPlaybackRecords(songPlaystatTags=allSongPlaystatTagsCurrent, songPlaybackRecords=songPlaybackRecords)

    # old code:
    # tagUpdateResolver = mlu.tags.playstats.SongPlaystatTagsUpdateResolver(songPlaybackRecords=songPlaybackRecords, songsPlaystatTags=songsCurrentPlaystatTags)
    # songsNewPlaystatTags = tagUpdateResolver.GetUpdatedPlaystatTags()
    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=allSongPlaystatTagsNew, outputFilepath=GetJSONCacheFilepath(3))

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
    mlu.tags.playstats.WritePlaystatTagsToSongs(songsPlaystatTags=allSongPlaystatTagsNew)

    # Verify the changes made: read in the current, now updated playstat tags from the audio files 
    # and verify they match the updated tags list built earlier
    tagIssueSongs = mlu.tags.playstats.FindSongsWithWrongPlaystatTags(expectedSongsPlaystatTags=allSongPlaystatTagsNew)

    if (tagIssueSongs):
        logger.error("Playstats tag verification failed: one or more songs have incorrect playstat tag values: examine the files below to resolve incorrect tags manually")
        for songFilePath in tagIssueSongs:
            logger.error("Incorrect playstat tags: {}".format(songFilePath))

    # archive log files and clear/reset mpd logs
    logger.info("Archiving MPD logs...")
    mpdLogsManager.archiveLogs()

    logger.info("Emptying MPD logs to reset collected playback data...")
    mpdLogsManager.clearLogs()
    