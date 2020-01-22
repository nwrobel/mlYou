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

from time import strftime
import datetime
import mlu.common.file
import mlu.common.time


# -------------------------------------------------------------------------------------------------
# BEGIN LOG DATA GET ROUTINE

# Class representing a single log from an MPD log - 2 properties:
#  text: what the log actually says (minus the string timestamp info)
#  timestamp: Epoch timestamp for when this log occured, with correct year caclulated
class MPDLogLine:
   def __init__(self, timestamp, text):
      self.text = text
      self.timestamp = timestamp

# Class representing the timespan information for a single logfile
#  logfilepath: path of the log file
#  contextCurrentYear: the year of the date of the last log line, provided by the user since the log lines have no year in the timestamps
#  firstEntryTime: timestamp of the the oldest (first) log line in the log file
#  lastEntryTime: timestamp of the the most recent (last) log line in the log file
class _LogFileTimeInfo:
   def __init__(self, logfilepath, contextCurrentYear):
      self.logfilepath = logfilepath
      self.contextCurrentYear = contextCurrentYear
      
      logfileEntryTimeRange = self.GetEntryTimeRange()
      self.firstEntryTime = logfileEntryTimeRange[0]
      self.lastEntryTime = logfileEntryTimeRange[1]

   def GetEntryTimeRange(self):
      with open(self.logfilepath, mode='r') as file:
         loglines = file.readlines()
         
      firstEntry = loglines[0]
      lastEntry = loglines[-1] # get last item in list

      # Last entry time must have the same year as currentcontextyear (it's the year of the date of last log entry)
      lastEntryTime = _getCorrectTimestampFromMPDLogLine(lastEntry, self.contextCurrentYear)

      # Find the oldest possible entry time for this log file based on the most recent entry time above,
      # assuming that all the logfiles span no more than 1 year (this is a requirement for this script to work)
      # Simply subtract 1 year from the log file's lastEntryTime
      minEntryTime = mlu.common.time.applyDeltaYearsToTimestamp(startTimestamp=lastEntryTime, years=-1)

      # Find the first entry time:
      #  - add current year to the first entry month+day to make full date
      #  - check if this first entry is more recent than the date of the last entry
      #  ---- if so, decrement the current year and add this to first entry month+day
      #  - check to ensure the calculated full date of first entry is not older than minEntryTime
      #  ---- if so, throw exception
      firstEntryTime = _getCorrectTimestampFromMPDLogLine(firstEntry, self.contextCurrentYear)
      # If the calculated first entry time is wrong, 
      if ( firstEntryTime > lastEntryTime ):
         # Try again with using the previous year
         firstEntryTime = _getCorrectTimestampFromMPDLogLine(firstEntry, (self.contextCurrentYear - 1))

      # Sanity check to ensure the first entry time is not older than the min age for an entry
      # If so, throw exception
      if ( firstEntryTime < minEntryTime ):
         raise Exception("ERROR: cannot determine the full timestamp of the first log entry for logfile " + self.logfilepath)
      
      return (firstEntryTime, lastEntryTime)
      

class MPDLogLineCollector:
   def __init__(self, mpdLogDir, promptForLogFileYears):
      self.mpdLogDir = mpdLogDir
      self.promptForLogFileYears = promptForLogFileYears
      self.tempLogDir = mlu.common.file.getMPDLogCacheDirectory()
      self.logFileContextCurrentYear = {}

   def GetMPDLogLines(self):
      self.CopyLogFilesToTemp()
      self.DecompressLogFiles()
      self.SetLogFilesContextCurrentYear()
      
      allLogLines = self.ProcessAllLogFileLines()
      return allLogLines
   
   def CopyLogFilesToTemp(self): 
      # Create the cache directory to store the log files in temporarily so we can manipulate them
      mlu.common.file.createDirectory(self.tempLogDir)

      # Get all MPD log files and copy them into the temp dir
      mpdLogFiles = mlu.common.file.GetAllFilesDepth1(self.mpdLogDir)
      mlu.common.file.CopyFilesToDirectory(srcFiles=mpdLogFiles, destDir=self.tempLogDir)


   # Decompresses any compressed, archived log files that are given  
   def DecompressLogFiles(self):
      mpdLogFiles = mlu.common.file.GetAllFilesDepth1(self.tempLogDir)
      gzippedLogFiles = []

      for logFile in mpdLogFiles:
         if (mlu.common.file.GetFileExtension(logFile) == "gz"):
            gzippedLogFiles.append(logFile)

      # Decompress each gz file, output each uncompressed log file to the temp dir, and delete
      # each original compressed .gz file
      for gzippedLogFilePath in gzippedLogFiles:
         gzippedBaseFilename = mlu.common.file.GetFileBaseName(gzippedLogFilePath)
         extractedFilepath = mlu.common.file.JoinPaths(self.tempLogDir, gzippedBaseFilename)
         mlu.common.file.DecompressSingleGZFile(gzippedLogFilePath, extractedFilepath)
         mlu.common.file.DeleteFile(gzippedLogFilePath)

   # SetLogFilesContextCurrentYear - get user to enter in the year that each log file has entries
   # up until - this year will be the 'current' year for that log file when timestamps are updated
   # this can be skipped based on param passed to the loghandler
   # Make an dict: logfilepath -> contextCurrentYear
   def SetLogFilesContextCurrentYear(self):
      mpdLogFiles = mlu.common.file.GetAllFilesDepth1(self.tempLogDir)
      currentCalendarYear = mlu.common.time.getCurrentYear()

      if (self.promptForLogFileYears):
         print("Please enter the logfile's context current year for each log file (the year when each log file was last written to...year of the date of the last log line in each log file)")
         print("MPD logs - enter context current year for each:\n")

         # Prompt the user to enter in the context current year for each logfile
         # Perform validation on the year entered: should not be more than the actual current year
         # or less than 1960
         for logfilepath in mpdLogFiles:
            logfilename = mlu.common.file.GetFilename(logfilepath)
            currentEntryComplete = False

            # Loop until the user enters a valid date to validate input year
            while (not currentEntryComplete):
               logContextCurrentYear = int( input(logfilename + ': ') )

            if ((logContextCurrentYear > currentCalendarYear) or (logContextCurrentYear < 1960)):
               print("ERROR: Invalid date: enter a correct date")
            else:
               self.logFileContextCurrentYear[logfilepath] = logContextCurrentYear
               currentEntryComplete = True

      # If promptForLogFileYears is false, we just set the context current year for all logfiles to 
      # the actual calendar current year      
      else:
         for logfilepath in mpdLogFiles:
            self.logFileContextCurrentYear[logfilepath] = currentCalendarYear

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
      mpdLogFiles = mlu.common.file.GetAllFilesDepth1(self.tempLogDir)
      allMPDLogLines = []

      for logfilepath in mpdLogFiles:
         logTimeInfo = _LogFileTimeInfo(logfilepath=logfilepath, contextCurrentYear=self.logFileContextCurrentYear[logfilepath])         

         with open(logfilepath, mode='r') as file:
            rawLogfileLines = file.readlines()

         for logLine in rawLogfileLines:
            lineTimestamp = _getCorrectTimestampFromMPDLogLine(line=logLine, logfileTimeInfo=logTimeInfo)
            lineText = _getTextFromMPDLogLine(logLine)
            allMPDLogLines.append( _MPDLogLine(timestamp=lineTimestamp, text=lineText) )

      # Sort the loglines array - this sorts the array object in place (does not copy/return a new, sorted array)
      allMPDLogLines.sort(key=lambda line: line.timestamp)

      return allMPDLogLines
            
# -------------------------------------------------------------------------------------------------
# MODULE HELPER FUNCTIONS
#

def _getCorrectTimestampFromMPDLogLine(line, logfileTimeInfo):
   timestamp = _getTimestampFromMPDLogLine(line=line, year=logfileTimeInfo.contextCurrentYear) 

   # If the timestamp formed by using the log's current context year is incorrect (outside the bounds of the first and last entry times),
   # form a new timestamp using the previous year
   if ((timestamp > logfileTimeInfo.lastEntryTime) or (timestamp < logfileTimeInfo.firstEntryTime)):
      timestamp = _getTimestampFromMPDLogLine( line=line, year=(logfileTimeInfo.contextCurrentYear - 1) ) 

   # Sanity check: ensure that this new timestamp also is not outside the bounds
   # If it is, raise exception
   if ((timestamp > logfileTimeInfo.lastEntryTime) or (timestamp < logfileTimeInfo.firstEntryTime)):
      raise Exception("ERROR: cannot determine the full timestamp for a log entry line for logfile " + logfileTimeInfo.logfilepath)

   return timestamp

def _getTimestampFromMPDLogLine(line, year):
    lineParts = line.split(" ")
    lineTime = lineParts[0] + " " + lineParts[1] + " " +  year + " " + lineParts[2]

    # Tell the datetime library how to parse this time string from the MPD log line into a timestamp value
    lineFormattedTime = datetime.datetime.strptime(lineTime, "%b %d %Y %H:%M")
    epochTimestamp = lineFormattedTime.timestamp()
    return epochTimestamp


def _getTextFromMPDLogLine(line):
   lineParts = line.split(":")
   lineText = lineParts[1]

   # Remove the leading space taken after splitting the string
   lineText = lineText[1:]
   # Remove the newline char at the end
   lineText = lineText.rstrip("\n")

   return lineText

