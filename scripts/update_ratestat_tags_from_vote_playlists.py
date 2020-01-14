# ==================================================================================================
#
#

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

# Do a pre scan through all playlists to get a list of all the unique songs (filepaths) that will be affected
# this will allow us to initialize our newVotes data structure to keep track of all the new votes 
# that were added to each affected song
allEntries = []
logger.info("Performing initial pre-scan of songs in all vote-value playlists")

for currentVoteValue in range(1, 10):
    currentVoteValuePlaylistName = "{}.m3u8".format(currentVoteValue)
    currentVoteValuePlaylistPath =  mlu.common.file.JoinPaths(args.votePlaylistsInputDir, currentVoteValuePlaylistName)
    votePlaylists.append(currentVoteValuePlaylistPath)
    
    playlistSongs = mlu.library.playlist.getAllPlaylistLines(currentVoteValuePlaylistPath)    
    allEntries += playlistSongs

allVotedSongs = set(allEntries)
logger.info("Pre-scan complete: found {} unique songs that were voted on".format(len(allVotedSongs)))

# initialize the newVotes data structure: add a dictionary for each unique song to this list of data
# dictionaries and set its new vote list to empty
newVotes = []
for songFilepath in allVotedSongs:
    newVotes.append({
            'songFilepath': songFilepath,
            'newVotes': []
        }
    )

# Start the main ratestat tag-writing process
logger.info("Starting to update ratestat tags for each song that was voted on")

for currentVoteValue in range(1, 10):
    currentVoteValuePlaylistName = "{}.m3u8".format(currentVoteValue)
    currentVoteValuePlaylistPath =  mlu.common.file.JoinPaths(args.votePlaylistsInputDir, currentVoteValuePlaylistName)
    
    logger.info("Reading songs with vote value {} from playlist {}".format(currentVoteValue, currentVoteValuePlaylistPath))
    playlistSongs = mlu.library.playlist.getAllPlaylistLines(currentVoteValuePlaylistPath)    
    logger.info("Found {} songs in vote value {} playlist: updating their ratestat tags now".format(len(playlistSongs), currentVoteValue))

    for songFilepath in playlistSongs:
        logger.debug("Adding new vote (value {}) to song '{}'".format(currentVoteValue, songFilepath))
        mlu.tags.ratestats.updateSongRatestatTags(songFilepath, newVote=currentVoteValue)

        newVotesListCurrentSong = [newVotesForSong['newVotes'] for newVotesForSong in newVotes if newVotesForSong['songFilepath'] == songFilepath]
        newVotesListCurrentSong.append(currentVoteValue)

logger.info('Music vote/rating tag data update completed successfully: {} songs were updated'.format(allVotedSongs))

# Print the results of all updated songs in table form and what changes occured
tagUpdatesTable = PrettyTable()
tagUpdatesTable.field_names = ["Song", "Artist", "Added Votes", "New Rating", "New Votes List"]

for newVotesForSong in newVotes:
    basicTags = mlu.tags.basic.getSongBasicTags(newVotesForSong['songFilepath'])
    ratestatTags = mlu.tags.ratestats.getSongRatestatTags(newVotesForSong['songFilepath'])

    newVotes = [newVotesForSong[songFilepath] for newVotesForSong in newVotesForSongs]

    tagUpdatesTable.add_row([
        basicTags.title, 
        basicTags.artist, 
        newVotesForSong['newVotes'],
        ratestatTags.rating,
        ratestatTags.votes
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