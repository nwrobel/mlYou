'''
mlu.file.playlist

Module containing functionality related to working with audio playlists.
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

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
    