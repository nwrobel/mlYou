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
    # We call this form a songPlaybackRecords object
    songPlaybackRecordCollector = mlu.mpd.playstats.SongPlaybackRecordCollector(playbackInstances=playbackInstances)
    songPlaybackRecords = songPlaybackRecordCollector.GetSongPlaybackRecords()


    # Take these instances and pass to module to display them in table form to use
    PrintPlaybackDataTable(songPlaybackRecords)

    # Write out the 3 cache json files:
    #   current playback instances found
    #   current playstats tag values of the songs that will be updated
    #   new tag values that will be set, based on applying the changes from 1 to the tags in 2
    # use the cache module to write the json and use the tags.playstats module to read old file playstat tag values 
    # and calculate new ones based on playback instances

    # Use tags.playstats module to update/write the new tag values, based on the 3rd json cache file

    # Use tags.playstats module to read the tags back and use the 3rd json cache file to verify integrity of each song's new values




    # print("The following changes are about to be written to the audio library:")
    # PrintPlaybackDataTable(playbackData)
     
    # answer = input("Do you wish to continue? [y/n]: ")
      
    # if answer == "y":
        
    #     # mlu.tags.playstats.WriteTagsFromPlaybackData(playbackData, musicDir)
        

         
    #     print("Finished writing out data to song tags")
    #     print("Starting the archive procedure on mpd.log....")
        
    #     mpdLogHandler.archiveLogFiles()
        
    #     print("#################### All operations complete #############################")
              
    # else:
    #     print("okay, exiting")


def PrintPlaybackDataTable(songPlaybackRecords):
    # Playmap:
    # SongTitle - Artist - NumPlays

    table = PrettyTable(['Song Title', 'Artist', 'Plays Found'])

    for playbackInstance in playbackInstances:
        songTitle = '' # mlu.tags.commontags.GetTitle(songFilePath)
        artist = ''   # mlu.tags.commontags.GetArtist(songFilePath)
        numPlays = len(playbackTimes)
        table.add_row([song, artist, plays])

    for songFilePath, playbackTimes in playbackData.items():  


    print(table)

