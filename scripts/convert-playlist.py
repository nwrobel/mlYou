'''
@author: Nick Wrobel

First Created: 3/5/19
Last Modified: 3/9/19

Argument-based script that allows the user to convert/fix music playlists by
changing the root folder path for every song entry in the playlist. 

This may be useful in case you want to preserve your playlists, but your music
library root path has changed.

This script and the other scripts in this "scripts" folder are all "entry points"
to this project: that is, the program execution will start from one of these 
scripts. Each script will take in user input, decide what needs to be done, and 
then utilize various modules within package "mlu", the main package of this project.

By separating the "mlu" package from these scripts, the package can be used independently
as an API separately from the scripts and the UI, such as for use in other projects.
'''

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import setup
setup.PrepareScriptsForExecution()

import argparse
import mlu.app.playlist

parser = argparse.ArgumentParser()

parser.add_argument("sourcePlaylistDir", 
                    help="absolute filepath of the folder containing the playlist files to convert",
                    type=str)

parser.add_argument("outputPlaylistDir", 
                    help="absolute filepath of the folder the converted playlists should be output to",
                    type=str)

parser.add_argument("oldRoot", 
                    help="absolute filepath of the old music library root folder, to be replaced in each song entry in the playlists",
                    type=str)

parser.add_argument("newRoot", 
                    help="absolute filepath of the new music library root folder, which will replace the old root for each song entry in the playlists",
                    type=str)



args = parser.parse_args()

mlu.app.playlist.ChangeRootPathForAllPlaylistEntries(sourcePlaylistDir=args.sourcePlaylistDir, 
                                             outputPlaylistDir=args.outputPlaylistDir, 
                                             oldRoot=args.oldRoot, 
                                             newRoot=args.newRoot)