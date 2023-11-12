'''
This module handles functionality related to retreiving information related to the music library
as a whole. 

'''
from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

def getAllLibraryAudioFilepaths(libraryRootDir):
    '''
    Returns a list of filepaths for all songs (audio files) in the music library. The root directory
    for the music library is taken from the MLU settings.
    '''
    audioFileExtensions = ['.flac', '.mp3', '.m4a', '.ogg', '.opus']
    allSongs = mypycommons.file.getFilesByExtension(rootDirPath=libraryRootDir, fileExt=audioFileExtensions)
    return allSongs