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

import mlu.tags.ratestats

parser = argparse.ArgumentParser()

parser.add_argument("libraryRootDir", 
                    help="absolute filepath of the music library root directory, where all music is stored",
                    type=str)

args = parser.parse_args()

mlu.tags.ratestats.updateAvgRatingForAllLibrarySongs(libraryRootPath=args.libraryRootPath)