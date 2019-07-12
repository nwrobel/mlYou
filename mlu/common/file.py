'''
mlu.common.file

This module contains functionality related to performing file/directory operations: getting, 
renaming, deleting, and moving.
'''

import os
from pathlib import Path
import gzip
import shutil


def GetProjectRoot():
    """
    Gets the absolute filepath for the root of the MLU project.

    TIP: use JoinPaths() to join this project root returned with any other path part,
    so trailing slashes don't need to be considered.
    """
    thisModulePath = os.path.dirname(os.path.realpath(__file__))
    projectRoot = os.path.abspath(os.path.join(thisModulePath ,".."))
    return projectRoot


def GetAllFilesRecursive(rootPath):
    """
    Gets the filepaths of all files in the given root directory and all of its subdirectories.
    Does not return directories.
    """
    allFiles = []
    
    for path, subdirs, files in os.walk(rootPath):
        for name in files:
            theFile = os.path.join(path, name)
            allFiles.append(theFile)
            
    return allFiles


def GetAllDirsDepth1(rootPath):
    """
    Gets the directory path of all folders in the given root directory, limited to depth 1. It does
    not get directories contained within the root directory's subfolders. Also does not get files.
    """
    path = Path(rootPath)
    dirs = [x for x in path.iterdir() if x.is_dir()]

    return dirs


def GetAllFilesDepth1(rootPath):
    """
    Gets the filepaths of all files in the given root directory, limited to depth 1. It does
    not get files contained within the root directory's subfolders. Also does not get folders.
    """
    path = Path(rootPath)
    files = [x for x in path.iterdir() if x.is_file()]

    return files


def GetAllFilesAndFolders(rootPath):
    """
    Gets the filepaths of all files AND folders within the given root directory, recursively.
    """
    pathObj = Path(rootPath)
    children = pathObj.glob('**/*')
    
    paths = [str(child) for child in children]
    return paths


def GetAllFilesByExtension(rootPath, fileExt):
    """
    Gets the filepaths of all files contained within the given root directory that have the given 
    file extension. Searches for files recursively. Give file extension with the dot.

    ex) GetAllFilesByExtension("C:\temp", ".mp3")
    """
    allFiles = GetAllFilesRecursive(rootPath)
    matchingFilepaths = []

    for filepath in allFiles:
        currentFileExt = GetFileExtension(filepath)
        if (currentFileExt == fileExt):
            matchingFilepaths.append(filepath)

    return matchingFilepaths


def CreateDirectory(folderPath):
    """
    Creates the directory specified by the given directory path.
    """
    folderPathObject = Path(folderPath)
    folderPathObject.mkdir(parents=True) 


def CopyFilesToFolder(srcFiles, destDir):
    """
    Given a list of source filepaths and a single destination directory path, this copies the files 
    to that destination. Metadata and permissions are preserved and will be the same as the originals
    for the new file copies.
    """
    for file in srcFiles:
        shutil.copy2(file, destDir)


def DeleteFiles(filePaths):
    """
    Deletes all files and/or folders, given a list of paths of files/folders to delete.
    """
    for filePath in filePaths:
        os.remove(filePath)


def DeleteAllFromDirectory(directoryPath):
    """
    Deletes all files and/or folders contained within the given root directory.
    """
    allPaths = GetAllFilesAndFolders(directoryPath)
    DeleteFiles(allPaths)


def GetFilename(filePath):
    """
    Given a filepath, returns only the filename, without the parent folders and containing its 
    file extension.
    """
    filePathObject = Path(filePath)
    return filePathObject.name


def GetFileExtension(filePath):
    """
    Returns the file extension of a file, given its filepath. Specifically, this returns the final 
    ".something" in the given file's name. File extension is returned including the dot.
    Returns an empty string if no file extension exists.
    """
    filePathObject = Path(filePath)
    return filePathObject.suffix


def GetFileBaseName(filePath):
    """
    Returns the "base" name of the file, given the filepath. The base name is the filename minus the
    file's extension. 

    ex) C:\data\playlist.m3u.tar --> playlist.m3u
    ex) C:\prog\connect.log --> connect
    """
    filePathObject = Path(filePath)
    return filePathObject.stem


def JoinPaths(path1, path2):
    """
    Given a root absolute filepath and a child relative filepath, returns the effective combination
    of these two paths to make a 3rd filepath.

    ex) JoinPaths("C:\prog\temp", "..\test.txt") --> "C:\prog\test.txt" 
    """
    return os.path.join(path1, path2)


def FileExists(filePath):
    """
    Checks if the file at the given filepath exists (boolean)
    """
    filePathObject = Path(filePath)
    if (filePathObject.exists() and filePathObject.is_file()):
        return True
    
    return False

def FolderExists(folderPath):
    """
    Checks if the folder at the given path exists (boolean)
    """
    folderPathObject = Path(folderPath)
    if (folderPathObject.exists() and folderPathObject.is_dir()):
        return True
    
    return False

def DecompressSingleGZFile(gzippedFilePath, decompFilePath):
    """
    Given the filepath of an input .GZ file and the filepath of the output file, this
    decompresses that single .gz file and creates the decompressed output file.

    This only works for .gz archives that contain single files (a single file is compressed), not 
    for multi-file archives.
    """
    with gzip.open(gzippedFilePath, 'rb') as inputFile:
        with open(decompFilePath, 'wb') as outputFile:
            shutil.copyfileobj(inputFile, outputFile)