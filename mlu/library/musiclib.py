'''
Created on May 5, 2019

@author: nick.admin

This module handles functionality related to retreiving information related to the music library
as a whole. 
'''
import mlu.common.file

def getAllSongFilepathsInLibrary(libraryRootPath):
    '''
    Returns a list of filepaths for all songs (audio files) in the music library, given the root filepath of the library.
    '''
    audioFileExtensions = ['.flac', '.mp3', '.m4a', '.ogg']
    allSongs = mlu.common.file.GetAllFilesByExtension(rootPath=libraryRootPath, fileExt=audioFileExtensions)
    return allSongs