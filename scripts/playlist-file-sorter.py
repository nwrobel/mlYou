'''
@author: Nick Wrobel

'''

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import argparse
from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

from mlu.settings import MLUSettings

def _getThisScriptCacheDirectory():
    dirName = "playlist-file-sorter"
    scriptCacheDir = mypycommons.file.joinPaths(MLUSettings.cacheDirectory, dirName)

    if (not mypycommons.file.pathExists(scriptCacheDir)):
        mypycommons.file.createDirectory(scriptCacheDir)

    return scriptCacheDir

def _getPlaylistSortDataFilepath():
    return mypycommons.file.joinPaths(_getThisScriptCacheDirectory(), 'playlists-sort-data.json')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument("inputDir", 
        help="absolute filepath of the folder that should either be sorted or is already sorted and should be used as a model to learn the sort structure",
        type=str
    )
    group.add_argument('--scan', 
        action='store_true',   
        help="scan the sorted inputDir and save the organizational structure of the playlists",
    )
    group.add_argument('--sort', 
        action='store_true',   
        help="sort the playlists in the unsorted inputDir into the organizational structure found in a previous run of this script",
    )
    parser.add_argument("--output-dir", 
        help="absolute filepath of the folder that the sorted playlists should be placed under (required if --sort is specified)",
        type=str,
        dest='outputDir'
    )

    args = parser.parse_args()

    if (args.scan):
        sortedPlaylistsDir = mypycommons.file.removeTrailingSlashFromPath(args.inputDir)
        playlistFilepaths = mypycommons.file.getChildPathsRecursive(sortedPlaylistsDir)

        playlistLocations = []
        for playlist in playlistFilepaths:
            playlistFilename = mypycommons.file.getFilename(playlist)
            playlistParentDirPath = mypycommons.file.getParentDirectoryPath(playlist)
            playlistParentDirPath = mypycommons.file.removeTrailingSlashFromPath(playlistParentDirPath)

            playlistSubfolderPartialPath = playlistParentDirPath.replace(sortedPlaylistsDir, '')
            playlistSubfolderPartialPath = playlistSubfolderPartialPath[1:] # remove initial slash left over

            playlistLocations.append({ 'playlistFilename': playlistFilename, 'playlistSubfolders': playlistSubfolderPartialPath })

        sortDataFilepath = _getPlaylistSortDataFilepath()
        if (mypycommons.file.pathExists(sortDataFilepath)):
            mypycommons.file.deletePath(sortDataFilepath)

        mypycommons.file.writeJsonFile(_getPlaylistSortDataFilepath(), playlistLocations)


    elif (args.sort):
        '''
        unsorted: a.m3u, b.m3u, c.m3u
        sort-data: [{'filaname': }]
        '''
        if (not args.outputDir):
            raise ValueError("Parameter --output-dir is required if the --sort param is specified")
        if (mypycommons.file.pathExists(args.outputDir)):
            raise FileExistsError("The given output dir for the sorted playlists already exists")

        playlistLocationNotFoundDir = mypycommons.file.joinPaths(args.outputDir, '_unknown-sort-location')

        sortDataFilepath = _getPlaylistSortDataFilepath()
        if (not mypycommons.file.pathExists(sortDataFilepath)):
            raise Exception("Unable to sort the inputDir: no sort locations data file was found (a --scan of a pre-sorted directory must be done first)")

        sortData = mypycommons.file.readJsonFile(sortDataFilepath)

        unsortedPlaylistsDir = mypycommons.file.removeTrailingSlashFromPath(args.inputDir)
        playlistFilepathsInUnsortedDir = mypycommons.file.getChildPathsRecursive(unsortedPlaylistsDir)

        for unsortedPlaylistFilepath in playlistFilepathsInUnsortedDir:
            currentPlaylistFilename = mypycommons.file.getFilename(unsortedPlaylistFilepath)
            currentPlaylistSubfolders =  [playlistLocation['playlistSubfolders'] for playlistLocation in sortData if playlistLocation['playlistFilename'] == currentPlaylistFilename] 
            
            if (not currentPlaylistSubfolders):
                if (not mypycommons.file.pathExists(sortDataFilepath)):
                    mypycommons.file.createDirectory(playlistLocationNotFoundDir)
                mypycommons.file.moveToDirectory(unsortedPlaylistFilepath, playlistLocationNotFoundDir)
                
            else:
                playlistDestDir = mypycommons.file.joinPaths(args.outputDir, currentPlaylistSubfolders[0])

                if (not mypycommons.file.pathExists(playlistDestDir)):
                    mypycommons.file.createDirectory(playlistDestDir)

                mypycommons.file.moveToDirectory(unsortedPlaylistFilepath, playlistDestDir)



