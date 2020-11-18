'''
Created on May 5, 2019

@author: nick.admin

This module handles functionality related to retreiving information related to the music library
as a whole. 

'''
from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
from mlu.settings import MLUSettings

def getAllMusicLibraryAudioFilepaths():
    '''
    Returns a list of filepaths for all songs (audio files) in the music library. The root directory
    for the music library is taken from the MLU settings.
    '''
    audioFileExtensions = ['.flac', '.mp3', '.m4a']
    allSongs = mypycommons.file.GetAllFilesByExtension(rootPath=MLUSettings.musicLibraryRootDir, fileExt=audioFileExtensions)
    return allSongs