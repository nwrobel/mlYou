'''
mlu.file.playlist

Module containing functionality related to working with audio playlists.
'''

from pathlib import Path
import os
from collections import namedtuple
from mlu.app.common import CreateDirectory

# TODO - MOVE THESE DIRECTORY FUNCTIONS TO COMMON MODULE
# TODO - REWRITE SOME DIR FUNCTIONS USING pathlib

def RemoveTrailingSlash(path):
    while (path[-1] == '/' or path[-1] == '\\'):
        path = path[:-1] # remove last char. from string
        
    return path

def FixPathSlashDirectionToMatchRootPath(rootPath, path):
    if ('/' in rootPath): # rootPath is a unix filepath
        fixedPath = path.replace('\\', '/')
    elif ('\\' in rootPath) or (':' in rootPath): # rootpath is a Windows filepath or a Windows drive letter
        fixedPath = path.replace('/', '\\')
        
    return fixedPath

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


def DeleteAllInDirectory(folderPath):
    pathObj = Path(folderPath)
    children = pathObj.glob('**/*')
    
    for child in children:
        os.remove(child)

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
    
    print("Attempting to load all playlists in source directory:", sourcePlaylistDir)
    
    assert FolderpathIsValid(sourcePlaylistDir), "ERROR: The given playlist source folder is invalid or cannot be found"
    playlistFilePaths = GetAllPlaylistFilesInDirRecursive(sourcePlaylistDir)
    numPlaylists = len(playlistFilePaths)
    
    print("Looking for output directory:", outputPlaylistDir)
    
    if (not FolderpathIsValid(outputPlaylistDir)):
        print("Output directory not found...attempting to create it")
        CreateDirectory(outputPlaylistDir)
        
    else:
        print("WARNING: Output directory already exists - all files currently within this directory WILL BE DELETED:\n", outputPlaylistDir)        
        while True:
            confirmation = input("Are you sure you want to continue? [Y/N]").lower()
            
            if (confirmation == 'y'):
                print("User confirmed, continuing process")
                break
            
            elif (confirmation == 'n'):
                print("User chose to exit, stopping script")
                return
            
            else:
                print("Invalid choice: please enter Y or N (case insensitive)")
                
        os.remove(outputPlaylistDir)
        CreateDirectory(outputPlaylistDir)

    oldRoot = RemoveTrailingSlash(oldRoot)
    newRoot = RemoveTrailingSlash(newRoot)

    print("For each playlist, each music file path entry will have the parent path (root) changed as follows:")
    print(oldRoot, " --> ", newRoot)
    
    
    print("The following", numPlaylists, "playlists will be processed and their new, converted versions will be saved in the output dir")
    print("(The original playlist files in the source folder will not be modified)")
    for playlistFilePath in playlistFilePaths:
        print(playlistFilePath)
    
    
    for playlistFilePath in playlistFilePaths:
    
        playlistFileName = GetFilenameFromFilepath(playlistFilePath)
        outputPlaylistFilePath = os.path.join(outputPlaylistDir, playlistFileName)
        
        newPlaylistLines = []
        
        with open(playlistFilePath, mode='r', encoding='utf-8-sig') as file:
            rawLines = file.readlines()
            
        lines = [line.rstrip('\n') for line in rawLines] # remove the newline character

        for line in lines:
            convertedLine = line.replace(oldRoot, newRoot)
            convertedLine = FixPathSlashDirectionToMatchRootPath(newRoot, convertedLine)
            newPlaylistLines.append(convertedLine)
        
        # Remove the '#' that is sometimes added to playlists when exported from Foobar2000
        if (len(newPlaylistLines) > 0 and newPlaylistLines[0] == '#'):
            newPlaylistLines.pop(0)  
                
        # Write out the converted lines to a new playlist file in the output dir
        # with UTF-8 encoding (important!)
        with open(outputPlaylistFilePath, mode='w', encoding='utf-8') as newPlaylist:
            for item in newPlaylistLines:
                # format string: build the string based on what's in "" - the item var. and the newline
                newPlaylist.write(f"{item}\n") 
            
            
        print("Playlist converted successfully, saved as:", outputPlaylistFilePath)
        
    print(numPlaylists, "playlists converted and output to the destination dir successfully!")
    