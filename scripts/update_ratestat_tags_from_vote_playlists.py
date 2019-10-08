# TODO: configure, set up, and use logger logging statements instead of print, so messages can be 
# easily saved into files and pruned down based on log importance level

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

parser.add_argument("votePlaylistsInputDir", 
                    help="absolute filepath of the folder containing the vote playlist files (1.m3u, 2.m3u, ..., 10.m3u) to use as the data source",
                    type=str)

parser.add_argument("votePlaylistsArchiveDir", 
                    help="absolute filepath of the folder where the archive of the vote playlist files should be saved for backup after the music rating tags are updated",
                    type=str)

args = parser.parse_args()
votePlaylists = []

for currentVoteValue in range(1, 10):
    currentVoteValuePlaylistName = currentVoteValue + '.m3u'
    currentVoteValuePlaylistPath =  mlu.common.file.JoinPaths(args.votePlaylistsInputDir, currentVoteValuePlaylistName)
    votePlaylists.append(currentVoteValuePlaylistPath)

    playlistSongs = mlu.library.playlist.getAllPlaylistLines(currentVoteValuePlaylistPath)

    for songFilepath in playlistSongs:
        print("Adding vote value " + currentVoteValue + " to song " + songFilepath)
        mlu.tags.ratestats.updateSongRatestatTags(songFilepath, newVote=currentVoteValue)

print('Vote/rating data update complete, saved to songs tags successfully! Vote playlists can now be emptied and reset')

print('Archiving vote playlists and clearing old data')
mlu.common.file.compressFileToArchive(inputFilePath=votePlaylists, archiveOutFilePath=args.votePlaylistsArchiveDir)

for votePlaylist in votePlaylists:
    mlu.common.file.clearFileContents(filePath=votePlaylist)