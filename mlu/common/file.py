'''
mlu.common.file

This module contains functionality related to performing file/directory operations: getting, 
renaming, deleting, and moving.
'''

import os
from pathlib import Path
import gzip
import shutil
import tarfile

def isValidPossibleFilepath(filepath):
    '''
    Checks whether or not the given string is a legal, absolute, valid possible/potential filepath.
    This does not check for the existence of the path.  
    '''
    return os.path.isabs(filepath)

def getMLUProjectRoot():
    '''
    Gets the absolute filepath for the root of the MLU project.

    TIP: use JoinPaths() to join this project root returned with any other path part,
    so trailing slashes don't need to be considered.
    '''
    thisModulePath = os.path.dirname(os.path.realpath(__file__))
    projectRoot = JoinPaths(thisModulePath ,"..\\..")
    return projectRoot

def GetAllFilesAndDirectoriesRecursive(rootPath):
    '''
    Gets the filepaths of all files AND folders within the given root directory, recursively. All
    filepaths will use the extended path syntax, to avoid problems with long filepaths.
    '''
    pathObj = Path(rootPath)
    children = pathObj.glob('**/*')
    
    paths = [('\\\\?\\' + str(child)) for child in children]
    return paths

def GetAllFilesRecursive(rootPath):
    '''
    Gets the filepaths of all files in the given root directory and all of its subdirectories.
    Does not return directories. All filepaths will use the extended path syntax, to avoid problems
    with long filepaths.
    '''
    pathObj = Path(rootPath)
    childrenObjs = pathObj.glob('**/*')
    
    fileObjs = [childObj for childObj in childrenObjs if _isFile(childObj)]
    filePaths = [('\\\\?\\' + str(fileObj)) for fileObj in fileObjs]
    return filePaths


# def GetAllDirectoriesDepth1(rootPath):
#     '''
#     Gets the directory path of all folders in the given root directory, limited to depth 1. It does
#     not get directories contained within the root directory's subfolders. Also does not get files.
#     '''
#     path = Path(rootPath)
#     dirs = [x for x in path.iterdir() if _isDir(x)]

#     return dirs


# def GetAllFilesDepth1(rootPath):
#     '''
#     Gets the filepaths of all files in the given root directory, limited to depth 1. It does
#     not get files contained within the root directory's subfolders. Also does not get folders.
#     '''
#     path = Path(rootPath)
#     files = [x for x in path.iterdir() if _isFile(x)]

#     return files


def GetAllFilesByExtension(rootPath, fileExt):
    '''
    Gets the filepaths of all files contained within the given root directory that have the given 
    file extension(s). Searches for files recursively. Either a single file extension or a list of 
    file extensions may be specified. If more than 1 extension is given, files matching any of those
    extensions are returned (searches using OR). Give file extension(s) with the dot.

    ex) 
    GetAllFilesByExtension("C:\temp", ".mp3")
    GetAllFilesByExtension("C:\temp", [".mp3", ".flac"])
    '''
    if (not isinstance(fileExt, list)):
        fileExt = [fileExt]
    
    allFiles = GetAllFilesRecursive(rootPath)
    matchingFilepaths = []

    for filepath in allFiles:
        currentFileExt = GetFileExtension(filepath)
        if (currentFileExt in fileExt):
            matchingFilepaths.append(filepath)

    return matchingFilepaths


def createDirectory(folderPath):
    '''
    Creates the directory specified by the given directory path.
    '''
    folderPathObject = Path(folderPath)
    folderPathObject.mkdir(parents=True) 


def CopyFilesToDirectory(srcFiles, destDir):
    '''
    Given a list of source filepaths and a single destination directory path, this copies the files 
    to that destination. Metadata and permissions are preserved and will be the same as the originals
    for the new file copies.
    '''
    for file in srcFiles:
        shutil.copy2(file, destDir)


def DeleteFile(filePath):
    '''
    Deletes a single file, given the filepath. Does not delete directories.
    '''
    os.remove(filePath)


def DeleteDirectory(directoryPath):
    '''
    Deletes the given directory and all files/folders contained within it, recursively.
    '''
    shutil.rmtree(directoryPath)

def getParentDirectory(filepath):
    '''
    Given a filepath, returns the parent directory of the file or folder object. Directory path 
    will use the extended path syntax, to avoid problems with long filepaths.
    '''
    filePathObject = Path(filepath)
    return ('\\\\?\\' + str(filePathObject.parent))

def GetFilename(filePath):
    '''
    Given a filepath, returns only the filename, without the parent folders and containing its 
    file extension.
    '''
    filePathObject = Path(filePath)
    return filePathObject.name


def GetFileExtension(filePath):
    '''
    Returns the file extension of a file, given its filepath. Specifically, this returns the final 
    ".something" in the given file's name. File extension is returned including the dot.
    Returns an empty string if no file extension exists.
    '''
    filePathObject = Path(filePath)
    return filePathObject.suffix


def GetFileBaseName(filePath):
    '''
    Returns the "base" name of the file, given the filepath. The base name is the filename minus the
    file's extension. 

    ex) C:\data\playlist.m3u.tar --> playlist.m3u
    ex) C:\prog\connect.log --> connect
    '''
    filePathObject = Path(filePath)
    return filePathObject.stem

def JoinPaths(path1, path2):
    '''
    Given a root absolute filepath and a child relative filepath, returns the effective combination
    of these two paths to make a 3rd filepath.

    ex) JoinPaths("C:\prog\temp", "..\test.txt") --> "C:\prog\test.txt" 
    '''
    joined = os.path.join(path1, path2)
    return os.path.abspath(joined)

def fileExists(filePath):
    '''
    Returns bool for whether or not the given filepath represents a valid, existing file. Directories
    will return false.

    Params:
        filePath: the path to test
    '''
    pathObj = Path(filePath)
    return (_isFile(pathObj))

def directoryExists(filePath):
    '''
    Returns bool for whether or not the given filepath represents a valid, existing directory. Files
    will return false.

    Params:
        filePath: the path to test
    '''
    pathObj = Path(filePath)
    return (_isDir(pathObj))

def DecompressSingleGZFile(gzippedFilePath, decompFilePath):
    '''
    Given the filepath of an input .GZ file and the filepath of the output file, this
    decompresses that single .gz file and creates the decompressed output file.

    This only works for .gz archives that contain single files (a single file is compressed), not 
    for multi-file archives.
    '''
    with gzip.open(gzippedFilePath, 'rb') as inputFile:
        with open(decompFilePath, 'wb') as outputFile:
            shutil.copyfileobj(inputFile, outputFile)

def compressFileToArchive(inputFilePath, archiveOutFilePath):
    '''
    Compresses one or more files to a .GZ archive, given the absolute input file path(s) and file
    path for the archive file.

    Params:
        inputFilepath: single path of the file to compress, or a list of paths
        archiveOutFilePath: filepath of the archive file to output to
    '''
    if (not isinstance(inputFilePath, list)):
        inputFilePath = [inputFilePath]

    archiveFileParentDir = getParentDirectory(archiveOutFilePath)
    if (not directoryExists(archiveFileParentDir)):
        createDirectory(archiveFileParentDir)

    with tarfile.open(archiveOutFilePath, 'w:gz') as archive:
        for filepath in inputFilePath:
            archive.add(filepath, arcname=GetFilename(filepath))


def clearFileContents(filepath):
    '''
    Removes all the data from the target file by deleting the file and re-creating it as an empty
    file with 0 bytes of data.
    '''
    DeleteFile(filepath)
    open(filepath, 'wb').close()


def writeToFile(filepath, content):
    '''
    Writes the given content to the given file. This only works with string data.

    Params:
        filePath: path to the output file
        content: string data to be written to the file
    '''
    with open(filepath, 'w', encoding='utf-8') as outputFile:
        outputFile.write(content)

# -------------------------------- Private module helper functions ---------------------------------
#
def _isFile(pathObj):
    '''
    Returns bool for whether or not the given Path object represents a valid, existing file.
    '''
    if (pathObj.is_file()):
        return True
    else:
        extendedFilepath = "\\\\?\\" + str(pathObj)
        extendedPathObj = Path(extendedFilepath)

        if (extendedPathObj.is_file()):
            return True
        else:
            return False

def _isDir(pathObj):
    '''
    Returns bool for whether or not the given Path object represents a valid, existing directory.
    '''
    if (pathObj.is_dir()):
        return True
    else:
        extendedFilepath = "\\\\?\\" + str(pathObj)
        extendedPathObj = Path(extendedFilepath)

        if (extendedPathObj.is_dir()):
            return True
        else:
            return False



