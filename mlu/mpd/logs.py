'''
Created on May 5, 2019

@author: nick.admin

This module deals with reading, writing, moving, and copying MPD log files to support operations
of the mlu.mpd.playstats module.

The MPDLogsHandler class focuses on reading in all the current MPD logs and returning a single array
of log lines - each line has 2 properties:
- text: what the log actually says (minus the string timestamp info)
- timestamp: Epoch timestamp for when this log occured, with correct year caclulated
'''

from time import gmtime, strftime
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

   def GetProcessedLogLines(self):
      self.CopyLogFilesToTemp()
      self.DecompressLogFiles()

      # GetLogFilesContextCurrentYear - get user to enter in the year that each log file has entries
      # up until - this year will be the 'current' year for that log file when timestamps are updated
      # this can be skipped based on param passed to the loghandler
      # Make an dict: logfilepath -> contextCurrentYear

      # ProcessAllLogFileLines
      # - Use the dict created earlier - for each logfile:
      #     Read in all lines into raw array
      #     For each log line:
      #           Get correct, full timestamp w/ corrected year (getTimestampFromMPDLogLine)
      #           Get the text-only part of the log line (remove text-based timestamp and other unneeded info)
      #           Make a LogLine object with the timestamp and text properties
      #           Add this object to the "master" processed LogLine array for all log lines
      # - Sort the object array based on the timestamp property, least recent to most recent
      # - Return the array from this function back to caller to use
   
   def CopyLogFilesToTemp(self): 
      # Create the cache directory to store the log files in temporarily so we can manipulate them
      Common.CreateDirectory(self.tempLogDir)

      # Get all MPD log files and copy them into the temp dir
      mpdLogFiles = Common.GetAllFilesDepth1(self.logRootPath)
      Common.CopyFilesToFolder(srcFiles=mpdLogFiles, destDir=self.tempLogDir)


   # Decompresses any compressed, archived log files that are given  
   def DecompressLogFiles(self):
      mpdLogFiles = Common.GetAllFilesDepth1(self.tempLogDir)
      gzippedLogFiles = []

      for logFile in mpdLogFiles:
         if (Common.GetFileExtension(logFile) == "gz"):
            gzippedLogFiles.append(logFile)

      # Decompress each gz file and output the uncompressed logs to the temp dir
      for gzippedLogFilePath in gzippedLogFiles:
         gzippedBaseFilename = Common.GetFileBaseName(gzippedLogFilePath)
         extractedFilepath = Common.JoinPaths(self.tempLogDir, gzippedBaseFilename)
         Common.DecompressSingleGZFile(gzippedLogFilePath, extractedFilepath)

      # Delete the original compressed .gz files
      Common.DeleteFiles(gzippedLogFiles)





def GetTempLogDirName():
   return Common.JoinPaths(Common.GetProjectRoot(), "cache/mpdlogs")

def getTimestampFromMPDLogLine(line, currentYear):
    
    parts = line.split(" ")
    time = parts[0] + " " + parts[1] + " " +  currentYear + " " + parts[2]
    print(time)
    datetime = datetime2.strptime(time, "%b %d %Y %H:%M")
    epochTime = datetime.timestamp()
    print(epochTime)
    
    return epochTime

# Read in all log file lines from all log files and return all the logfile lines to caller
# PUBLIC
def GetAllLogLines():
    pass




# Get a list of the paths of all the valid logfiles found in the logfile dir
def GetAllLogFiles(mpdLogDir):
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