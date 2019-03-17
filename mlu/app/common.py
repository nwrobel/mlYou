'''
@author: Nick Wrobel

First Created: 12/26/18
Last Modified: 3/9/19

Module containing "common" (non-specific) functionality that is used throughout
the MLU project.
'''

import os
from os import listdir
import os.path as path
from os.path import join

def getAllFilesRecursive(rootPath):
    
    allFiles = []
    
    for path, subdirs, files in os.walk(rootPath):
        for name in files:
            theFile = os.path.join(path, name)
            allFiles.append(theFile)
            
    return allFiles

def getAllDirsDepth1(rootPath):
    #onlydirs = [f for f in listdir(rootPath) if isdir(join(rootPath, f))]
    x = []
    for dir in listdir(rootPath):
        x.append(join(rootPath, dir))
    return x

def getProjectRoot():
    thisModulePath = os.path.dirname(os.path.realpath(__file__))
    projectRoot = path.abspath(path.join(thisModulePath ,".."))
    return (projectRoot + '/')

    