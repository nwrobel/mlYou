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

parser.add_argument("sourcePlaylistPath", 
                    help="absolute filepath of the playlist to convert",
                    type=string)

parser.add_argument("oldRoot", 
                    help="absolute filepath of the old music library root folder, which the playlist currently references",
                    type=string)

parser.add_argument("newRoot", 
                    help="absolute filepath of the new music library root folder, which will replace the old root for each song entry in the playlist",
                    type=string)

parser.add_argument("newPlaylistPath", 
                    help="absolute filepath of the new, converted output playlist",
                    type=string)

args = parser.parse_args()

# newPlaylistFilename = playlistFileInfo.fileName + '_converted' + playlistFileInfo.fileExt
# newPlaylistPath = playlistFileInfo.pathObject.parent.joinpath(newPlaylistFilename)

playlist.ChangeRootPathForAllPlaylistEntries(sourcePlaylistFilepath=args.playlistPath, 
                                             newPlaylistFilepath=args.newPlaylistFilepath, 
                                             oldRoot=args.oldRoot, 
                                             newRoot=args.newRoot)