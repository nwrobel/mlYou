# TODO: configure, set up, and use logger logging statements instead of print, so messages can be 
# easily saved into files and pruned down based on log importance level

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

# import external Python modules
import argparse
from prettytable import PrettyTable

# setup logging for this script using MLU preconfigured logger
import mlu.common.logger
mlu.common.logger.initMLULogger()
logger = mlu.common.logger.getMLULogger()

# import project-related modules
import mlu.tags.ratestats
import mlu.common.file 
import mlu.common.time
import mlu.library.playlist
import mlu.tags.basic

parser = argparse.ArgumentParser()

parser.add_argument("votePlaylistsInputDir", 
                    help="absolute filepath of the folder containing the vote playlist files (1.m3u, 2.m3u, ..., 10.m3u) to use as the data source",
                    type=str)

parser.add_argument("votePlaylistsArchiveDir", 
                    help="absolute filepath of the folder where the archive of the vote playlist files should be saved for backup after the music rating tags are updated",
                    type=str)

args = parser.parse_args()
votePlaylists = []
allPlaylistsSongs = []

# allSongsNewVotes (list)
#   songNewVotes (list item, a dictionary)
#       songFilepath variable key : new votes array for this song so far
allSongsNewVotes = [] # list of dictionaries, each dict maps key songFilePath (the variable) to array of new votes:

for currentVoteValue in range(1, 10):
    currentVoteValuePlaylistName = "{}.m3u8".format(currentVoteValue)
    currentVoteValuePlaylistPath =  mlu.common.file.JoinPaths(args.votePlaylistsInputDir, currentVoteValuePlaylistName)
    votePlaylists.append(currentVoteValuePlaylistPath)
    
    logger.info("Reading songs with vote value {} from playlist {}".format(currentVoteValue, currentVoteValuePlaylistPath))
    playlistSongs = mlu.library.playlist.getAllPlaylistLines(currentVoteValuePlaylistPath)

    # create empty vote array dictonaries for the songs that will be updated (all get current vote value added)
    for songFilePath in playlistSongs:
        songsInitialized = [songNewVotes.keys() for songNewVotes in allSongsNewVotes]

        if (not (songFilepath in songsInitialized)):
            allSongsNewVotes.append({ songFilePath: [] })


    allPlaylistsSongs += playlistSongs
    logger.info("Found {} songs in vote value {} playlist...updating their ratestat tags now".format(len(playlistSongs), currentVoteValue))

    for songFilepath in playlistSongs:
        logger.debug("Adding new vote (value {}) to song '{}'".format(currentVoteValue, songFilepath))
        mlu.tags.ratestats.updateSongRatestatTags(songFilepath, newVote=currentVoteValue)

        currentSongNewVotes = [songNewVotes[songFilepath] for songNewVotes in allSongsNewVotes] # by reference, this is the array in the dict in this list of songs new votes
        currentSongNewVotes.append(currentVoteValue)




allUpdatedSongs = set(allPlaylistsSongs)
logger.info('Music vote/rating data updated successfully: {} songs had ratestat tags updated'.format(allUpdatedSongs))

# Print the results of all updated songs in table form and what changes occured
tagUpdatesTable = PrettyTable()
tagUpdatesTable.field_names = ["Song", "Artist", "New Votes", "New Rating"]

for songFilepath in allUpdatedSongs:
    basicTags = mlu.tags.basic.getSongBasicTags(songFilepath)
    ratestatTags = mlu.tags.ratestats.getSongRatestatTags(songFilepath)
    newVotes = [songNewVotes[songFilepath] for songNewVotes in allSongsNewVotes]

    tagUpdatesTable.add_row([
        basicTags.title, 
        basicTags.artist, 
        newVotes,
        ratestatTags['rating']
    ])

    logger.info('\\nThe following changes were made to music library:\\n}{}'.format(tagUpdatesTable))

logger.info('Archiving vote playlists...')
archiveFilename = "[{}] Post-update archived vote data playlists.gz".format(mlu.common.time.getCurrentFormattedTime())
archiveFilePath = mlu.common.file.JoinPaths(args.votePlaylistsArchiveDir, archiveFilename)

mlu.common.file.compressFileToArchive(inputFilePath=votePlaylists, archiveOutFilePath=archiveFilePath)
logger.info('Vote playlists successfully compressed into archive file {}'.format(archiveFilePath))

logger.info('Emptying already counted votes from vote playlists...')
for votePlaylist in votePlaylists:
    mlu.common.file.clearFileContents(filePath=votePlaylist)

logger.info('Vote playlists reset successfully, script complete!')