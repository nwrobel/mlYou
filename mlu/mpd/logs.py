'''
Created on May 5, 2019

@author: nick.admin

This module deals with reading, writing, moving, and copying MPD log files to support operations
of the mlu.mpd.playstats module.
'''

import pathlib
from shutil import copyfile
from time import gmtime, strftime
import os.path as path

import mlu.app.common as Common


# global variables
# MAKE A CLASS instead (?)
mpdLogDir = ''
mpdArchivedLogDir = ''
mpdDefaultLogFilePath = ''
   # mpdLogFilepath = mpdDir + "mpd.log"
   # mpdLogArchiveDir = mpdDir + "parsed-already/"


# -------------------------------------------------------------------------------------------------
# BEGIN LOG DATA GET ROUTINE

class MPDLogsHandler:
   def __init__(self, mpdLogFilePath):
      self.logRootPath = mpdLogFilePath
      self.tempLogDir = GetTempLogDirName()

   
   def CopyLogFilesToTemp(self): 
      # Create the cache directory to store the log files in temporarily so we can manipulate them
      Common.CreateDirectory(self.tempLogDir)

      # Get all MPD log files and copy them into the temp dir
      mpdLogFiles = Common.GetAllFilesDepth1(self.mpdLogFilePath)
      Common.CopyFilesToFolder(srcFiles=mpdLogFiles, destDir=tempDir)


   # Decompresses any compressed, archived log files that are given  
   def DecompressLogFiles(self):
      mpdLogFiles = Common.GetAllFilesDepth1(self.tempLogDir)
      gzippedLogFiles = []

      for logFile in mpdLogFiles:
         if (Common.GetFileExtension(logFile) != "gz")
            gzippedLogFiles.append(logFile)

      for gzippedLogFile in gzippedLogFiles:
         pass

       

   def GetTempLogDirName(self):
      return path.join(Common.GetProjectRoot(), "cache/mpdlogs")



# Read in all log file lines from all log files and return all the logfile lines to caller
# PUBLIC
def GetAllLogLines():
    pass




# Get a list of the paths of all the valid logfiles found in the logfile dir
def GetAllLogFiles(mpdLogDir):
    pass

# Finds compressed log files from a list of log files
def IdentifyCompressedLogFiles():
    pass

# Finds which log file is the default "mpd.log" that has last been written to
# This file must exist after the process is complete
def IdentifyDefaultLogFile():
    pass





# Opens a log file, reads, and returns the data found in that log file
# as a string array of the lines
def ReadLogFile(logFilepath):
    pass





    



def GetArchivedLogFileName():
    time = strftime("%Y-%m-%d %H.%M.%S", gmtime())
    archiveLogFilename = "mpd-" + time + ".log"
    return archiveLogFilename


# Delete the contents of mpd.log, so that the file is 'reset', and the file still exists.
# and we cannot run the script again and mess up the tag values on songs
def ResetDefaultLogFile():

    open(mpdLogFilepath, "w").close()
    


# Moves all the read log files to the "parsed-already" directory
# Meant to be called after all the log files and lines that were returned have been consumed
# by the caller, and they are ready to archive the read logs now.
# def ArchiveParsedLogFiles():
    
#     # Makes the archive file directory if it doesn't exist   
#     pathlib.Path(mpdArchivedLogDir).mkdir(exist_ok=True)
    
#     # get full filepath
#     archiveLogFilepath = mpdLogArchiveDir + getArchiveLogFilename()
    
#     # Copy the mpd.log file to the archives under a new name (timestamped)
#     copyfile(mpdLogFilepath, archiveLogFilepath)