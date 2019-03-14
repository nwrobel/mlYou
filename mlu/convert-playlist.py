'''
@author: Nick Wrobel

First Created: 3/5/19
Last Modified: 3/9/19

Argument-based script that allows the user to convert/fix music playlists by
changing the root folder path for every song entry in the playlist. 

This may be useful in case you want to preserve your playlists, but your music
library root path has changed.
'''

import argparse
from mlu.app import playlist

parser = argparse.ArgumentParser()

parser.add_argument("sourcePlaylistDir", 
                    help="absolute filepath of the folder containing the playlist files to convert",
                    type=string)

parser.add_argument("outputPlaylistDir", 
                    help="absolute filepath of the folder the converted playlists should be output to",
                    type=string)

parser.add_argument("oldRoot", 
                    help="absolute filepath of the old music library root folder, to be replaced in each song entry in the playlists",
                    type=string)

parser.add_argument("newRoot", 
                    help="absolute filepath of the new music library root folder, which will replace the old root for each song entry in the playlists",
                    type=string)



args = parser.parse_args()

# newPlaylistFilename = playlistFileInfo.fileName + '_converted' + playlistFileInfo.fileExt
# newPlaylistPath = playlistFileInfo.pathObject.parent.joinpath(newPlaylistFilename)

playlist.ChangeRootPathForAllPlaylistEntries(sourcePlaylistDir=args.sourcePlaylistDir, 
                                             outputPlaylistDir=args.outputPlaylistDir, 
                                             oldRoot=args.oldRoot, 
                                             newRoot=args.newRoot)