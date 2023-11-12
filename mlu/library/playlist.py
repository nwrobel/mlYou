'''
mlu.file.playlist

Module containing functionality related to working with audio playlists.
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

import mlu.library.audiolib
import mlu.tags.io

def createPlaylist(playlistFilepath, audioFilepaths):
    '''
    Creates a new playlist file from the given list of audio filepaths.
    '''
    mypycommons.file.writeToFile(filepath=playlistFilepath, content=audioFilepaths)

def getAllPlaylistLines(playlistFilepath):
    '''
    Returns a list of all the audio filepaths contained within a playlist.
    '''
    with open(playlistFilepath, mode='r', encoding='utf-8-sig') as file:
        lines = file.readlines()

    playlistLines = []
    for line in lines:
        lineFixed = line.replace('\n', '') # remove newline char from end of each line

        if (lineFixed):
            playlistLines.append(lineFixed) # only add the line if it isn't empty

    return playlistLines

def createRatingAutoplaylist(libraryRootDir, playlistFilepath, ratingMin, ratingMax):
    allAudioFilepaths = mlu.library.audiolib.getAllLibraryAudioFilepaths(libraryRootDir)
    playlistItemsTags = []

    for audioFilepath in allAudioFilepaths:
        tagHandler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
        currentTags = tagHandler.getTags()

        if (currentTags.rating):
            rating = float(currentTags.rating)
            if (rating >= ratingMin and rating <= ratingMax):
                playlistItemsTags.append(
                    {
                        'filepath': audioFilepath,
                        'tags': currentTags
                    }
                )

    # sort by multiple attributes
    # Rating descending, then by albumArtist - album - trackNumber
    playlistItemsTags.sort(key=lambda x: (x['tags'].albumArtist, x['tags'].album, x['tags'].trackNumber))
    playlistItemsTags.sort(key=lambda x: (float(x['tags'].rating)), reverse=True)

    playlistItemsSorted = []
    for playlistItemTags in playlistItemsTags:
        playlistItemsSorted.append(playlistItemTags['filepath'])

    createPlaylist(playlistFilepath, playlistItemsSorted)