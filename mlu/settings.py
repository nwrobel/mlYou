'''
mlu.common.settings

Author:   Nick Wrobel
Created:  2020-12-25
Modified: 2021-12-17

Module containing the definition for setting values for MLU (project-wide constants).
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

def getProjectRootDir():
    thisScriptDir = mypycommons.file.getThisScriptCurrentDirectory()
    projectRootDir = mypycommons.file.joinPaths(thisScriptDir, '..')
    return projectRootDir

class MLUSettings:
    projectRootDir = getProjectRootDir()
    logDir = mypycommons.file.joinPaths(projectRootDir, '~logs')
    cacheDir = mypycommons.file.joinPaths(projectRootDir, '~cache')

    # Dirs of where various types of cache files are stored
    tempDir = mypycommons.file.joinPaths(cacheDir, 'temp')

    # Test data
    testDataDir = mypycommons.file.joinPaths(projectRootDir, 'test/data')

    # Create empty directories
    if (not mypycommons.file.pathExists(logDir)):
        mypycommons.file.createDirectory(logDir)

    if (not mypycommons.file.pathExists(cacheDir)):
        mypycommons.file.createDirectory(cacheDir)

    if (not mypycommons.file.pathExists(tempDir)):
        mypycommons.file.createDirectory(tempDir)

