'''
Created on May 5, 2019

@author: nick.admin

This module handles functionality related to retreiving information related to the music library
as a whole. 
'''
import mlu.common.file
from mlu.common.settings import MLUSettings


def getAllMusicLibraryAudioFilepaths():
    '''
    Returns a list of filepaths for all songs (audio files) in the music library. The root directory
    for the music library is taken from the MLU settings.
    '''
    audioFileExtensions = ['.flac', '.mp3', '.m4a']
    allSongs = mlu.common.file.GetAllFilesByExtension(rootPath=MLUSettings.musicLibraryRootDir, fileExt=audioFileExtensions)
    return allSongs