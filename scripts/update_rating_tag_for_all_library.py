# TODO: add a progress bar/status messages for how many files found and how many remaining to
# check/update

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import argparse

# setup logging for this script using MLU preconfigured logger
import mlu.common.logger
mlu.common.logger.initMLULogger()
logger = mlu.common.logger.getMLULogger()

import mlu.tags.ratestats

parser = argparse.ArgumentParser()

parser.add_argument("libraryRootDir", 
                    help="absolute filepath of the music library root directory, where all music is stored",
                    type=str)

args = parser.parse_args()

logger.info("Searching for all audio under music library root path {}".format(args.libraryRootDir))
librarySongs = mlu.library.musiclib.getAllSongFilepathsInLibrary(args.libraryRootDir)
logger.info("Found {} audio files in music library root path".format(len(librarySongs)))

logger.info("Updating ratestat tags for all audio files that are flagged for rating update")
flaggedSongsCount = 0

for songFilepath in librarySongs:

    songRatestatTagsHander = mlu.tags.ratestats.SongRatestatTagsHandler(songFilepath)
    songRatestatTags = songRatestatTagsHander.getTags()

    if (songRatestatTags.needsRatingUpdate):
        logger.info("Updating ratestat tags for file flagged for rating update: '{}'".format(songFilepath))
        flaggedSongsCount += 1

        songRatestatTagsHander.updateTags()
        songRatestatTagsHander.writeTags()

logger.info("Rating tag update process completed successfully: {} flagged songs were updated".format(flaggedSongsCount))