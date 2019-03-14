'''
@author: Nick Wrobel

First Created: 3/9/19
Last Modified: 3/9/19

Module containing functionality related to working with playlist data, used 
throughout the MLU project.
'''

from pathlib import Path
import os
from collections import namedtuple

def FilepathIsValid(filePath):
    filePathObject = Path(filePath)
    if (filePathObject.exists() and filePathObject.is_file()):
        return True
    
    return False

def FolderpathIsValid(folderPath):
    folderPathObject = Path(folderPath)
    if (folderPathObject.exists() and folderPathObject.is_dir()):
        return True
    
    return False


def GetFilenameFromFilepath(filePath):
    
    filePathObject = Path(filePath)
    return filePathObject.name


def GetNameAndExtensionFromFileName(fileName):

    parts = fileName.split(".")
    fileExt = parts[-1] # get the 1st last item (or, the last item) in the list
    del parts[:-1] # remove the last item from the list
    fileName = parts.join(".") # put the filename back together, in case of filenames like "file.playlist.m3u"
    
    fileInfo = namedtuple("fileInfo", ["fileName", "fileExt"])
    return fileInfo(fileName, fileExt)

def GetAllPlaylistFilesInDirRecursive(parentDir):
    pathObj = Path(parentDir)
    playlistFileObjs = pathObj.rglob('*.m3u*')
    
    playlistFilePaths = [str(playlistFileObj) for playlistFileObj in playlistFileObjs]
    return playlistFilePaths


def ChangeRootPathForAllPlaylistEntries(sourcePlaylistDir, outputPlaylistDir, oldRoot, newRoot):
    
    print("Attempting to load all playlists in ", sourcePlaylistDir)
    assert FolderpathIsValid(sourcePlaylistDir), "The given playlist source folder is invalid or cannot be found"
    playlistFilePaths = GetAllPlaylistFilesInDirRecursive(sourcePlaylistDir)

    print("All song entries in each playlist will have their parent paths (root) changed as follows:")
    print(oldRoot, " --> ", newRoot)
    
    print("The following playlists will be converted and have new versions saved in the output dir:")
    print(playlistFilePaths)
    
    
    for playlistFilePath in playlistFilePaths:
    
        playlistFileName = GetFilenameFromFilepath(playlistFilePath)
        outputPlaylistFilePath = os.path.join(outputPlaylistDir, playlistFileName)
        
        newPlaylistLines = []
        
        with open(playlistFilePath, 'r') as file:
            for line in file:
                convertedLine = line.replace(oldRoot, newRoot)
                newPlaylistLines.append(convertedLine)
                      
        with open(outputPlaylistFilePath, 'w') as newPlaylist:
            for item in newPlaylistLines:
                newPlaylist.write(f"{item}\n")
            
            
        print("Playlist converted successfully, saved as:", outputPlaylistFilePath)
    