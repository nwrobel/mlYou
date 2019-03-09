'''
@author: Nick Wrobel

First Created: 3/9/19
Last Modified: 3/9/19

Module containing functionality related to working with playlist data, used 
throughout the MLU project.
'''

from pathlib import Path
from collections import namedtuple

def FilepathIsValid(filePath):
    filePathObject = Path(filePath)
    if (filePathObject.exists() and filePathObject.is_file()):
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


def ChangeRootPathForAllPlaylistEntries(sourcePlaylistFilepath, newPlaylistFilepath, oldRoot, newRoot):
    
    print("Attempting to load playlist at ", sourcePlaylistFilepath)
    assert FilepathIsValid(sourcePlaylistFilepath), "The given playlist path is invalid or cannot be found"

    print("All song entries in this playlist will have their parent paths (root) changed as follows:")
    print(oldRoot, " --> ", newRoot)
        
    newPlaylistLines = []
    
    with open(sourcePlaylistFilepath, 'r') as file:
        for line in file:
            convertedLine = line.replace(oldRoot, newRoot)
            newPlaylistLines.append(convertedLine)
                  
    with open(newPlaylistFilepath, 'w') as newPlaylist:
        for item in newPlaylistLines:
            newPlaylist.write(f"{item}\n")
            
            
    print("Playlist converted successfully: new playlist saved as:", newPlaylistFilepath)
    