'''
@author: Nick Wrobel

First Created: 12/26/18
Last Modified: 3/9/19

Module containing "common" (non-specific) functionality that is used throughout
the MLU project.
'''

import os
from os import listdir
from pathlib import Path
import os.path as path
from os.path import join
from shutil import copy2


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
        copy2(file, destDir)


# Returns the file extenstion for a file, given its filepath
def GetFileExtension(filePath):
    parts = fileName.split(".")
    fileExt = parts[-1] # get the 1st last item (or, the last item) in the list
    return fileExt

# Gets the absolute filepath for the root of the MLU project.
#
def getProjectRoot():
    thisModulePath = os.path.dirname(os.path.realpath(__file__))
    projectRoot = path.abspath(path.join(thisModulePath ,".."))
    return (projectRoot + '/')

    
