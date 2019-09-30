# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import argparse

import mlu.tags.ratestats
import mlu.common.file 
import mlu.library.playlist

parser = argparse.ArgumentParser()

parser.add_argument("votePlaylistsDir", 
                    help="absolute filepath of the folder containing the vote playlist files (1.m3u, 2.m3u, ..., 10.m3u) to use as the data source",
                    type=str)

args = parser.parse_args()

for currentVoteValue in range(1, 10):
    currentVoteValuePlaylistName = currentVoteValue + '.m3u'
    currentVoteValuePlaylistPath =  mlu.common.file.JoinPaths(args.votePlaylistsDir, currentVoteValuePlaylistName)

    playlistSongs = mlu.library.playlist.getAllPlaylistLines(currentVoteValuePlaylistPath)

    for songFilepath in playlistSongs:
        print("Adding vote value " + currentVoteValue + " to song " + songFilepath)
        mlu.tags.ratestats.addVoteAndUpdateSongRatestatTags(songFilepath, currentVoteValue)

print('Vote/rating data update complete, saved to songs tags successfully! Vote playlists can now be emptied and reset')

