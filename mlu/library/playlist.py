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
    
    assert mypycommons.file.directoryExists(sourcePlaylistDir), "ERROR: The given playlist source folder is invalid or cannot be found"
    
    playlistFilePathsM3U = mypycommons.file.GetAllFilesByExtension(sourcePlaylistDir, ".m3u")
    playlistFilePathsM3U8 = mypycommons.file.GetAllFilesByExtension(sourcePlaylistDir, ".m3u8")
    playlistFilePaths = playlistFilePathsM3U + playlistFilePathsM3U8
    numPlaylists = len(playlistFilePaths)
    
    print("Looking for output directory:", outputPlaylistDir)
    
    if (not mypycommons.file.directoryExists(outputPlaylistDir)):
        print("Output directory not found...attempting to create it")
        mypycommons.file.createDirectory(outputPlaylistDir)
        
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
                
        mypycommons.file.DeleteDirectory(outputPlaylistDir)
        mypycommons.file.createDirectory(outputPlaylistDir)

    oldRoot = RemoveTrailingSlash(oldRoot)
    newRoot = RemoveTrailingSlash(newRoot)

    print("For each playlist, each music file path entry will have the parent path (root) changed as follows:")
    print(oldRoot, " --> ", newRoot)
    
    for playlistFilePath in playlistFilePaths:
        print("Converting playlist:", playlistFilePath)

        # Each output playlist will have a .m3u8 extension by default, even if original was .m3u
        # This ensures support for UTF-8 encoding always will be used
        outputPlaylistFileName = mypycommons.file.GetFileBaseName(playlistFilePath) + ".m3u8"
        outputPlaylistFilePath = mypycommons.file.JoinPaths(outputPlaylistDir, outputPlaylistFileName)
        
        # Read in all lines from the original playlist
        originalLines = getAllPlaylistLines(playlistFilePath)

        # Remove the '#' that is sometimes added to playlists when exported from Foobar2000
        for index, line in enumerate(originalLines):
            if (line == "#"):
                originalLines.pop(index)
        
        # Convert each line and add the result to the list of new playlist lines
        newPlaylistLines = []
        for originalLine in originalLines:
            convertedLine = originalLine.replace(oldRoot, newRoot)
            convertedLine = FixPathSlashDirectionToMatchRootPath(newRoot, convertedLine)

            # Add the newline character back to the end
            convertedLine = convertedLine + "\n"

            newPlaylistLines.append(convertedLine)
               
        # Write out the converted lines to a new playlist file in the output dir
        # with UTF-8 encoding (important!)
        with open(outputPlaylistFilePath, mode='w', encoding='utf-8') as newPlaylist:
            newPlaylist.writelines(newPlaylistLines)
  
        print("Playlist converted successfully! New file:", outputPlaylistFilePath)
        
    print(numPlaylists, "playlists converted and output to the destination dir successfully!")


def getAllPlaylistLines(playlistFilepath):
    '''
    Returns a list of all the lines contained within a playlist, given the path of the playlist.
    Each line should be a filepath pointing to an audio file/song entry on that playlist.
    '''
    with open(playlistFilepath, mode='r', encoding='utf-8-sig') as file:
        lines = file.readlines()

    playlistLines = []
    # Remove newline at the end of each playlist line (song filepath)
    for line in lines:
        playlistLines.append(line.replace('\n', ''))

    return playlistLines
    