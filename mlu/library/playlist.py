'''
mlu.file.playlist

Module containing functionality related to working with audio playlists.
'''
from typing import List
from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

import mlu.library.audiolib
import mlu.tags.io
from mlu.tags.values import AudioFileTags
from mlu.settings import MLUSettings


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

