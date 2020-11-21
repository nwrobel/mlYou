'''
update-playstat-tags-from-mpd-log.py

'''

from prettytable import PrettyTable
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX
from mutagen.mp4 import MP4
# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()





# #--------------------------------------------------------------------------------------------------
# def PrintPlaybackDataTable(songPlaybackRecords):
    
#     # Create a table, which will have these 4 columns with corresponding header titles
#     table = PrettyTable(['Song Title', 'Artist', '# Plays', 'Play Times'])

#     for songPlaybackRecord in songPlaybackRecords:
#         # Get the common tags so we can display the ones we need to in the playback table for this song
#         songTags = mlu.tags.basic.getSongBasicTags(songFilepath=songPlaybackRecord.songFilePath)

#         numPlays = len(songPlaybackRecord.playbackTimes)
#         # Get the playback times: for each playback timestamp on this songPlaybackRecord, format it for display
#         # and return this formatted timestamp
#         playTimes = ( mlu.common.time.formatTimestampForDisplay(timestamp) for timestamp in songPlaybackRecord.playbackTimes )

#         # Add the songPlaybackRecord data we found above to the table as a row
#         table.add_row([songTags.title, songTags.artist, numPlays, playTimes])

#     # Display the table, begin and end it with a newline to look better
#     print("\n" + table + "\n")

# #--------------------------------------------------------------------------------------------------
# def GetJSONCacheFilepath(cacheFileID ):
#     jsonFilename = "mpd-playstats-cache-" + cacheFileID + ".json"
#     return mlu.common.file.JoinPaths(mlu.common.file.getMLUCacheDirectory(), jsonFilename)


# # ------------------------------- Main script procedure --------------------------------------------
# #
if __name__ == "__main__":
    mutagenInterface = mutagen.File("Z:\\Development\\Test Data\\mlYou\\test-audio-files\\test-1.flac")
    print(mutagenInterface.info.length)

    mutagenInterface = mutagen.File("Z:\\Development\\Test Data\\mlYou\\test-audio-files\\test-1.mp3")
    print(mutagenInterface.info.length)

    mutagenInterface = mutagen.File("Z:\\Development\\Test Data\\mlYou\\test-audio-files\\test-1.m4a")
    print(mutagenInterface.info.length)

   
   
#     print("Caching data...")

#     # Write 1st cache file: SongPlaybackRecords found from MPD
#     print("Cache step 1: Writing newly found playback data...")
#     mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=songPlaybackRecords, outputFilepath=GetJSONCacheFilepath(1))

#     # Write 2nd cache file: current SongPlaystatTags values for each song that will be updated
#     print("Cache step 2: Writing current playstat tags for all songs...")
#     songsToUpdate = (playbackRecord.songFilePath for playbackRecord in songPlaybackRecords)
#     allSongPlaystatTagsCurrent = mlu.tags.playstats.ReadPlaystatTagsFromSongs(songFilepaths=songsToUpdate)

#     mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=allSongPlaystatTagsCurrent, outputFilepath=GetJSONCacheFilepath(2))

#     # Write 3rd cache file: calculate new playstat tags based on playback instances + old tags
#     # and return new, updated SongPlaystatTags values for all the songs
#     print("Cache step 3: Writing new computed tag values (current tags + playback data) for all songs...")
    
#     # new code:
#     allSongPlaystatTagsNew = mlu.tags.playstats.MergeSongPlaystatTagsWithPlaybackRecords(songPlaystatTags=allSongPlaystatTagsCurrent, songPlaybackRecords=songPlaybackRecords)

#     # old code:
#     # tagUpdateResolver = mlu.tags.playstats.SongPlaystatTagsUpdateResolver(songPlaybackRecords=songPlaybackRecords, songsPlaystatTags=songsCurrentPlaystatTags)
#     # songsNewPlaystatTags = tagUpdateResolver.GetUpdatedPlaystatTags()
#     mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=allSongPlaystatTagsNew, outputFilepath=GetJSONCacheFilepath(3))

#     print("Playback data gathering, caching, and tag preparation complete!\n")

#     # Take the SongPlaybackRecord instances display them in table form to the user, once everything
#     # has been prepared and we are ready to write the updated tags
#     print("The following playstat tag updates are ready to write to the audio library:")
#     PrintPlaybackDataTable(songPlaybackRecords)

#     # continue if we want to make the changes, otherwise we exit
#     writeChanges = input("Do you wish to continue? [y/n]: ")

#     if ( (writeChanges != 'y') and (writeChanges != 'Y') ):
#         print("Exiting due to choice of user")
#         return
    
#     # write the new, updated tag values (same ones we just wrote to the 3rd json cache file) to the
#     # audio files
#     mlu.tags.playstats.WritePlaystatTagsToSongs(songsPlaystatTags=allSongPlaystatTagsNew)

#     # Verify the changes made: read in the current, now updated playstat tags from the audio files 
#     # and verify they match the updated tags list built earlier
#     tagIssueSongs = mlu.tags.playstats.FindSongsWithWrongPlaystatTags(expectedSongsPlaystatTags=allSongPlaystatTagsNew)

#     if (tagIssueSongs):
#         logger.error("Playstats tag verification failed: one or more songs have incorrect playstat tag values: examine the files below to resolve incorrect tags manually")
#         for songFilePath in tagIssueSongs:
#             logger.error("Incorrect playstat tags: {}".format(songFilePath))

#     # archive log files and clear/reset mpd logs
#     logger.info("Archiving MPD logs...")
#     mpdLogsManager.archiveLogs()

#     logger.info("Emptying MPD logs to reset collected playback data...")
#     mpdLogsManager.clearLogs()
    