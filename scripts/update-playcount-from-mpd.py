'''
@author: Nick Wrobel

First Created: 3/5/19
Last Modified: 5/10/19

Argument-based script to allow the user to update the "Play Count" tags on their music files, based
on playback data contained within MPD (Media Player Daemon) server log files. 
'''

import argparse

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import setup
setup.PrepareScriptsForExecution()

# import mlu.mpd.playstats
import mlu.app.common

#--------------------------------------------------------------------------------------------------    
def Run():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("musicDir", 
                        help="Absolute filepath of the root directory of the music library",
                        type=str)
    
    parser.add_argument("mpdLogsDir", 
                        help="Absolute filepath of the root directory of where the MPD logs are stored on this system",
                        type=str)
    
    args = parser.parse_args()
    
    # mpdLogHandler = MPDLogHandler(mpdLogsDir)
    # playbackData = mlu.mpd.playstats.GetPlaybackData(mpdLogHandler)
         
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

