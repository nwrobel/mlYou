'''
update_ratestat_tags_from_vote_playlists.py

Created: ?
Modified: 01/22/20


'''

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
import mlu.cache.io

parser = argparse.ArgumentParser()

parser.add_argument("playlistRootDir", 
                    help="absolute filepath of the folder containing the vote playlist files (1.m3u, 2.m3u, ..., 10.m3u) to use as the data source",
                    type=str)

parser.add_argument("playlistArchiveDir", 
                    help="absolute filepath of the folder where the archive of the vote playlist files should be saved for backup after the music rating tags are updated",
                    type=str)

args = parser.parse_args()

# Start the main ratestat tag-writing process
logger.info("Loading audio file votes data from all vote playlists")
audioFileVoteDataList = mlu.tags.ratestats.getAudioFileVoteDataFromRatePlaylists(args.playlistRootDir)

logger.info("Vote playlists data loaded successfully")
logger.info("Writing new ratestats tag data to audio files")

erroredAudioFileVoteDataList = []
for audioFileVoteData in audioFileVoteDataList:
    try:
        mlu.tags.ratestats.updateRatestatTagsFromVoteData(audioFileVoteData)
    except:
        logger.info("Failed to update ratestat tag values with new votes: File={}".format(audioFileVoteData.filepath))
        erroredAudioFileVoteDataList.append(audioFileVoteData)

logger.info("Ratestats tag data update completed")
logger.info("{} audio files were processed".format(len(audioFileVoteDataList)))
logger.info("{} audio files failed update".format(len(erroredAudioFileVoteDataList)))

# Print the results of all updated songs in table form and what changes occurred
tagUpdatesTable = PrettyTable()
tagUpdatesTable.field_names = ["Title", "Artist", "Votes Added", "New Rating", "New Votes List"]
tagUpdatesTable.align["Title"] = "l"
tagUpdatesTable.align["Artist"] = "l"
tagUpdatesTable.align["Votes Added"] = "r"
tagUpdatesTable.align["New Rating"] = "r"
tagUpdatesTable.align["New Votes List"] = "r"

successfulAudioFileVoteDataList = [voteData for voteData in audioFileVoteDataList if (voteData not in erroredAudioFileVoteDataList)]

for audioFileVotesData in successfulAudioFileVoteDataList:

    tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFileVotesData.filepath)
    currentTags = tagHandler.getTags()

    votesAdded = mlu.tags.common.formatValuesListToAudioTag(audioFileVotesData.votes)

    tagUpdatesTable.add_row([
        currentTags.title, 
        currentTags.artist, 
        votesAdded,
        currentTags.rating,
        currentTags.votes
    ])

logger.info("\nThe following changes were made to music library:\n{}".format(tagUpdatesTable.get_string()))

logger.info("Failed to update ratestat tags for some audio files: see 'update-ratestat-tags-failed-data.json'")
errorJsonFilepath = mlu.common.file.JoinPaths(mlu.common.file.getMLUCacheDirectory(), 'update-ratestat-tags-failed-data.json')
mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=erroredAudioFileVoteDataList, outputFilepath=errorJsonFilepath)
   
logger.info('Archiving vote playlists')
mlu.tags.ratestats.archiveVotePlaylists(playlistsDir=args.playlistRootDir, archiveDir=args.playlistArchiveDir)

logger.info('Emptying already counted votes from vote playlists')
mlu.tags.ratestats.resetVotePlaylists(playlistsDir=args.playlistRootDir)

logger.info('Script complete')