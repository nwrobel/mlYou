'''
mlu.file.playlist

Module containing functionality related to working with audio playlists.
'''

import mlu.common.file

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


def ChangeRootPathForAllPlaylistEntries(sourcePlaylistDir, outputPlaylistDir, oldRoot, newRoot):
    
    print("Attempting to load all playlists in source directory:", sourcePlaylistDir)
    
    assert mlu.common.file.FolderExists(sourcePlaylistDir), "ERROR: The given playlist source folder is invalid or cannot be found"
    
    playlistFilePathsM3U = mlu.common.file.GetAllFilesByExtension(sourcePlaylistDir, ".m3u")
    playlistFilePathsM3U8 = mlu.common.file.GetAllFilesByExtension(sourcePlaylistDir, ".m3u8")
    playlistFilePaths = playlistFilePathsM3U + playlistFilePathsM3U8
    numPlaylists = len(playlistFilePaths)
    
    print("Looking for output directory:", outputPlaylistDir)
    
    if (not mlu.common.file.FolderExists(outputPlaylistDir)):
        print("Output directory not found...attempting to create it")
        mlu.common.file.CreateDirectory(outputPlaylistDir)
        
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
                
        mlu.common.file.DeleteDirectory(outputPlaylistDir)
        mlu.common.file.CreateDirectory(outputPlaylistDir)

    oldRoot = RemoveTrailingSlash(oldRoot)
    newRoot = RemoveTrailingSlash(newRoot)

    print("For each playlist, each music file path entry will have the parent path (root) changed as follows:")
    print(oldRoot, " --> ", newRoot)
    
    for playlistFilePath in playlistFilePaths:
        print("Converting playlist:", playlistFilePath)

        # Each output playlist will have a .m3u8 extension by default, even if original was .m3u
        # This ensures support for UTF-8 encoding always will be used
        outputPlaylistFileName = mlu.common.file.GetFileBaseName(playlistFilePath) + ".m3u8"
        outputPlaylistFilePath = mlu.common.file.JoinPaths(outputPlaylistDir, outputPlaylistFileName)
        
        # Read in all lines from the original playlist
        with open(playlistFilePath, mode='r', encoding='utf-8-sig') as file:
            originalLines = file.readlines()

        # Remove the '#' that is sometimes added to playlists when exported from Foobar2000
        if (len(originalLines) > 0 and originalLines[0] == '#\n'):
            originalLines.pop(0) 
        
        # Convert each line and add the result to the list of new playlist lines
        newPlaylistLines = []
        for originalLine in originalLines:
            convertedLine = originalLine.replace(oldRoot, newRoot)
            convertedLine = FixPathSlashDirectionToMatchRootPath(newRoot, convertedLine)
            newPlaylistLines.append(convertedLine)
               
        # Write out the converted lines to a new playlist file in the output dir
        # with UTF-8 encoding (important!)
        with open(outputPlaylistFilePath, mode='w+', encoding='utf-8') as newPlaylist:
            newPlaylist.writelines(newPlaylistLines)
  
        print("Playlist converted successfully! New file:", outputPlaylistFilePath)
        
    print(numPlaylists, "playlists converted and output to the destination dir successfully!")
    