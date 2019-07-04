'''
Created on May 5, 2019

@author: nick.admin

This module deals with reading, writing, moving, and copying MPD log files to support operations
of the mlu.mpd.playstats module.

The MPDLogsHandler class focuses on reading in all the current MPD logs and returning a single array
of MPDLogLine objects - each object has 2 properties:
- text: what the log actually says (minus the string timestamp info)
- timestamp: Epoch timestamp for when this log occured, with correct year caclulated
'''

from time import gmtime, strftime
import datetime
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

# Class representing a single log from an MPD log - 2 properties:
#  text: what the log actually says (minus the string timestamp info)
#  timestamp: Epoch timestamp for when this log occured, with correct year caclulated
class MPDLogLine:
   def __init__(self, timestamp, text):
      self.text = text
      self.timestamp = timestamp


class MPDLogsHandler:
   def __init__(self, mpdLogFilepath, promptForLogFileYears=False):
      self.logRootPath = mpdLogFilepath
      self.tempLogDir = GetTempLogDirName()
      self.promptForLogFileYears = promptForLogFileYears
      self.logFileContextCurrentYear = {}

   def GetProcessedLogLines(self):
      self.CopyLogFilesToTemp()
      self.DecompressLogFiles()
      self.SetLogFilesContextCurrentYear()
      
      allLogLines = self.ProcessAllLogFileLines()
      return allLogLines
   
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

   # SetLogFilesContextCurrentYear - get user to enter in the year that each log file has entries
   # up until - this year will be the 'current' year for that log file when timestamps are updated
   # this can be skipped based on param passed to the loghandler
   # Make an dict: logfilepath -> contextCurrentYear
   def SetLogFilesContextCurrentYear(self):
      mpdLogFiles = Common.GetAllFilesDepth1(self.tempLogDir)

      if (self.promptForLogFileYears):
         print("Please enter the year of when each log file was last written to")
         print("TODO--complete this functionality")
      
      else:
         currentYear = (datetime.datetime.now()).year
      
      for logfilepath in mpdLogFiles:
         self.logFileContextCurrentYear[logfilepath] = currentYear

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
   def ProcessAllLogFileLines(self):
      mpdLogFiles = Common.GetAllFilesDepth1(self.tempLogDir)
      allMPDLogLines = []

      for logfilepath in mpdLogFiles:
         logFileContextCurrentYear = self.logFileContextCurrentYear[logfilepath]

         with open(logfilepath, mode='r') as file:
            rawLogfileLines = file.readlines()

         for logLine in rawLogfileLines:
            lineTimestamp = GetTimestampFromMPDLogLine(logLine, logFileContextCurrentYear)
            lineText = GetTextFromMPDLogLine(logLine)
            allMPDLogLines.append( MPDLogLine(timestamp=lineTimestamp, text=lineText) )

      # Sort the loglines array - this sorts the array object in place (does not copy/return a new, sorted array)
      allMPDLogLines.sort(key=lambda line: line.timestamp)

      return allMPDLogLines
            
# -------------------------------------------------------------------------------------------------
# MODULE HELPER FUNCTIONS
#

def GetTempLogDirName():
   return Common.JoinPaths(Common.GetProjectRoot(), "cache/mpdlogs")


def GetTimestampFromMPDLogLine(line, currentYear):
    lineParts = line.split(" ")
    lineTime = lineParts[0] + " " + lineParts[1] + " " +  currentYear + " " + lineParts[2]
    lineFormattedTime = datetime.datetime.strptime(lineTime, "%b %d %Y %H:%M")
    epochTimestamp = lineFormattedTime.timestamp()
    return epochTimestamp


def GetTextFromMPDLogLine(line):
   lineParts = line.split(":")
   lineText = lineParts[1]

   # Remove the leading space taken after splitting the string
   lineText = lineText[1:]
   # Remove the newline char at the end
   lineText = lineText.rstrip("\n")

   return lineText







    



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