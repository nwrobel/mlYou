# TODO: add a progress bar/status messages for how many files found and how many remaining to
# check/update

# TODO: configure, set up, and use logger logging statements instead of print, so messages can be 
# easily saved into files and pruned down based on log importance level

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

logger.info("Finding audio files that need rating tag updated")
songsNeedRatingUpdate = []
for songFilepath in librarySongs:
    if (mlu.tags.ratestats.songNeedsRatingTagUpdate(songFilepath)):
        logger.info("Found file flagged for rating update: {}".format(songFilepath))
        songsNeedRatingUpdate.append(songFilepath)

logger.info("Found {} audio files that need rating tag updated...performing updates now".format(len(songsNeedRatingUpdate)))
for songFilepath in songsNeedRatingUpdate:
    mlu.tags.ratestats.updateSongRatestatTags(songFilepath)

logger.info("Rating tag update process completed successfully")