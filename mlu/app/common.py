'''
@author: Nick Wrobel

First Created: 12/26/18
Last Modified: 3/9/19

Module containing "common" (non-specific) functionality that is used throughout
the MLU project.
'''

import os
from pathlib import Path
import gzip
import shutil
import datetime



# -------------------------------------------------------------------------------------------------
# Gets the filepaths of all files in the given root directory and all of its subdirectories.
# Does not return directories.
# 
def GetAllFilesRecursive(rootPath):
    
    allFiles = []
    
    for path, subdirs, files in os.walk(rootPath):
        for name in files:
            theFile = os.path.join(path, name)
            allFiles.append(theFile)
            
    return allFiles


# Gets the folder paths of all folders in the root directory, limited to depth 1, meaning it does
# not get directories contained within the root directory's subfolders. Does not get files.
#
def GetAllDirsDepth1(rootPath):
    path = Path(rootPath)
    dirs = [x for x in path.iterdir() if x.is_dir()]

    return dirs


# Gets the filepaths of all files within the given root directory, limited to depth 1, meaning it
# does not get files contained within subfolders in the root folder. Does not get directories.
#
def GetAllFilesDepth1(rootPath):
    path = Path(rootPath)
    files = [x for x in path.iterdir() if x.is_file()]

    return files

# Gets filepaths of all files within a root folder that have a given file extension
#
# def GetAllFilesByExtension(rootPath, fileExtension):
#     pathObj = Path(rootPath)
#     regexQuery = '*.' + fileExtension
#     desiredFiles = pathObj.rglob(regexQuery)
    
#     desiredFilepaths = [str(file) for file in desiredFiles]
#     return desiredFilepaths


# Gets the filepaths of all files AND folders within the given root directory, recursively.
#  
def GetAllFilesAndFolders(rootPath):
    pathObj = Path(rootPath)
    children = pathObj.glob('**/*')
    
    paths = [str(child) for child in children]
    return paths


# Creates the given directory path
# 
def CreateDirectory(folderPath):
    folderPathObject = Path(folderPath)
    folderPathObject.mkdir(parents=True) 


# Copies the given files (filepaths) to the specified directory
# This uses copy2, which also copies metadata and permissions on files
#
def CopyFilesToFolder(srcFiles, destDir):
    for file in srcFiles:
        shutil.copy2(file, destDir)

# Delete the given files given their filepaths
def DeleteFiles(filePaths):
    for filePath in filePaths:
        os.remove(filePath)


# Returns the name of the file, containing its extension from the given filepath.
#
def GetFilename(filePath):
    filePathObject = Path(filePath)
    return filePathObject.name

# Returns the file extension for a file, given its filepath - specifically, the final .something
# in the given filename.
# Returns an empty string if no file extension found.
#
def GetFileExtension(filePath):
    filePathObject = Path(filePath)
    return filePathObject.suffix


# Returns the "base" name of the file, given the filepath. For example, returns 'playlist.m3u' for
# a file named 'playlist.m3u.tar'
#
def GetFileBaseName(filePath):
    filePathObject = Path(filePath)
    return filePathObject.stem


def JoinPaths(path1, path2):
    return os.path.join(path1, path2)

# Decompresses a single .gz file and creates a decompressed output file in the desired location.
# This only works for single files which are compressed, not for multi-file archives.
#
def DecompressSingleGZFile(gzippedFilePath, decompFilePath):
    with gzip.open(gzippedFilePath, 'rb') as inputFile:
        with open(decompFilePath, 'wb') as outputFile:
            shutil.copyfileobj(inputFile, outputFile)


# Converts epoch timestamp int. value to a timestamp that can be displayed and understood
# format ex) 2012-01-27 02:29:33
#
def FormatTimestampForDisplay(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    formattedTime = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    return formattedTime


# Gets the absolute filepath for the root of the MLU project.
# NOTE: use JoinPaths to join this project root returned from here with any other path part,
# so trailing slashes don't need to be considered.
#
def GetProjectRoot():
    thisModulePath = os.path.dirname(os.path.realpath(__file__))
    projectRoot = os.path.abspath(os.path.join(thisModulePath ,".."))
    return projectRoot

    
