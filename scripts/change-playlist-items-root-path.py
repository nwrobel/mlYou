'''
@author: Nick Wrobel

Created: 2019-03-05
Modified: 2022-09-09

Argument-based script that allows the user to convert/fix music playlists by
changing the root folder path for every song entry in the playlist. 

This may be useful in case you want to preserve your playlists, but your music
library root path has changed.

This script and the other scripts in this "scripts" folder are all "entry points"
to this project: that is, the program execution will start from one of these 
scripts. Each script will take in user input, decide what needs to be done, and 
then utilize various modules within package "mlu", the main package of this project.

By separating the "mlu" package from these scripts, the package can be used independently
as an API separately from the scripts and the UI, such as for use in other projects.
'''

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import argparse
import sys
import time
from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file

from mlu.settings import MLUSettings

# --------------------------------------------------------------------------------------------------
# Helper functions
#
def _fixPathSlashDirectionToMatchRootPath(rootPath, inputPath):
    '''
    path: Z:/Music/Content/1 Tool - Undertow.flac
    rootPath: Z:
    fixedPath: Z:\Music\Content\0.1 Tool - Undertow.flac
    '''
    # rootPath is a unix filepath
    if ('/' in rootPath): 
        fixedPath = inputPath.replace('\\', '/')
    
     # rootpath is a Windows filepath or a the path is simply a Windows drive letter
    elif ('\\' in rootPath) or (rootPath[1] == ':'):
        fixedPath = inputPath.replace('/', '\\')
        
    return fixedPath

# --------------------------------------------------------------------------------------------------
# Script logic
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("oldRoot", 
                        help="absolute filepath of the old music library root folder, to be replaced in each song entry in the playlists",
                        type=str)

    parser.add_argument("newRoot", 
                        help="absolute filepath of the new music library root folder, which will replace the old root for each song entry in the playlists",
                        type=str)

    parser.add_argument("--config-file", 
        help="config file name located in root dir",
        default="mlu.config.json",
        type=str,
        dest='configFile'
    )
    args = parser.parse_args()

    settings = MLUSettings(configFilename=args.configFile)
    sourcePlaylistDir = settings.userConfig.convertPlaylistsInputDir
    outputPlaylistDir = settings.userConfig.convertPlaylistsOutputDir

    playlistFilePaths = mypycommons.file.getFilesByExtension(sourcePlaylistDir, [".m3u", ".m3u8"])
    numPlaylists = len(playlistFilePaths)

    print("Found {} playlists in source directory '{}'".format(numPlaylists, sourcePlaylistDir))
        
    if (mypycommons.file.pathExists(outputPlaylistDir)):
        print("WARNING: Output directory already exists - all files currently within this directory WILL BE DELETED:\n", outputPlaylistDir)    
        confirmation = None    
        while (confirmation != 'y' and confirmation != 'n'):
            confirmation = input("Are you sure you want to continue? [Y/N]").lower()
            
            if (confirmation == 'y'):
                print("User confirmed, continuing process")

            elif (confirmation == 'n'):
                print("User chose to exit, leaving function")
                sys.exit(0)

            else:
                print("Invalid choice: please enter y or n")
                
        mypycommons.file.deletePath(outputPlaylistDir)
        time.sleep(2)
    
    mypycommons.file.createDirectory(outputPlaylistDir)

    oldRoot = mypycommons.file.removeTrailingSlashFromPath(args.oldRoot)
    newRoot = mypycommons.file.removeTrailingSlashFromPath(args.newRoot)

    print("For each playlist, each path item will be changed as follows:")
    print(oldRoot, " --> ", newRoot)
    
    for originalPlaylistFilePath in playlistFilePaths:
        print("Converting playlist: {}".format(originalPlaylistFilePath))

        # Each output playlist will have a .m3u8 extension by default, even if original was .m3u
        # This ensures support for UTF-8 encoding always will be used
        outputPlaylistFileName = mypycommons.file.getFileBaseName(originalPlaylistFilePath) + ".m3u8"
        outputPlaylistFilePath = mypycommons.file.joinPaths(outputPlaylistDir, outputPlaylistFileName)
        
        # Read in all lines from the original playlist
        # Use utf8-sig (common in Windows files), which also reads utf8
        originalLines = mypycommons.file.readFile(originalPlaylistFilePath, encoding='utf-8-sig')

        # Remove the '#' that is sometimes added to playlists when exported from Foobar2000
        if (originalLines and originalLines[0] == "#\n"):
            originalLines.pop(0)

        # Convert each line and add the result to the list of new playlist lines
        newPlaylistLines = []
        for originalLine in originalLines:
            # remove newline character
            originalLine = originalLine.replace('\n', '')

            convertedLine = originalLine.replace(oldRoot, newRoot)
            convertedLine = _fixPathSlashDirectionToMatchRootPath(newRoot, convertedLine)

            newPlaylistLines.append(convertedLine)
               
        # Write out the converted lines to a new playlist file in the output dir
        # with UTF-8 encoding (important!)
        mypycommons.file.writeToFile(outputPlaylistFilePath, newPlaylistLines)
  
        print("Playlist converted successfully! New file:", outputPlaylistFilePath)
        
    print("{} playlists converted and output to the destination dir successfully!".format(numPlaylists))