'''
mlu.mpd.logs

Author: Nick Wrobel
First Created:  05/05/19
Last Modified:  01/27/20

This module deals with reading, writing, moving, and copying MPD log files to support operations
of the mlu.mpd.playstats module.

The MPDLogsHandler class focuses on reading in all the current MPD logs and returning a single array
of MPDLogLine objects - each object has 2 properties:
- text: what the log actually says (minus the string timestamp info)
- timestamp: Epoch timestamp for when this log ocurred, with correct year calculated
'''

import datetime
import mlu.common.file
import mlu.common.time

# TODO: look into and figure out how to use syslog or other linux configurable system logger so
# that I can set it to output the full timestamp in the MPD log files, including year, and make
# this code simpler

# -------------------------------------------------------------------------------------------------
# BEGIN LOG DATA GET ROUTINE


class MPDLogLine:
   '''
   Class representing a single log line entry from an MPD log file.
   
   Params:
      text: what the log actually says (log line minus the string timestamp info)
      timestamp: time for when this log line occurred/was written, as an epoch timestamp (float or int)
   '''
   def __init__(self, text, timestamp):
      # perform validation on input data
      if (not text) or (not isinstance(text, str)):
         raise TypeError("Class attribute 'text' must be a non-empty string")

      if (not mlu.common.time.isValidTimestamp(timestamp)):
         raise ValueError("Class attribute 'timestamp' must be a valid timestamp, value '{}' is invalid".format(timestamp))

      self.text = text
      self.timestamp = timestamp



class MPDLogFileHandler:
   '''
   Deals with handling the MPD log files, including copying them to the cache/temp dir to be read,
   extracting compressed log files, archiving processed log files, and resetting the main 'mpd.log' 
   file once all operations are complete.
   '''

   def __init__(self, mpdLogDir):
      self._mpdLogDir = mpdLogDir

      # Get the temp mpd logs directory location (inside the MLU project cache folder)
      # This directory will created for us if it doesn't exist
      self._tempLogDir = self._getMPDLogTempCacheDirectory()

   def prepareLogFilesForDataCollection(self):
      '''
      Prepares the MPD log files for reading in/data collection by copying them to the temp dir
      and extracting any of them that are archived. The filepath of the prepared MPD log files
      (temp dir) is returned: this is to be the 'working dir' from where the log files are read in.
      '''
      self._copyLogFilesToTempDir()
      self._resetActiveLogFile()
      self._decompressLogFiles()

      return self._tempLogDir


   def finalizeLogFilesAfterDataCollection(self):
      pass

   def _copyLogFilesToTempDir(self): 
      '''
      Copies the MPD log files from the MPD log directory to the MPD temp log file dir. Two copies
      of the original MPD logs will be made: one in the temp directory, and the other in a subfolder
      named 'original' in the temp directory. This is so that original MPD logs can archived at the
      end of the process, and in case something goes wrong and a reset is needed.
      
      This throws an exception if the temp log file dir is not empty beforehand.
      '''
      # First check if there are already any MPD logs in the temp dir - if so, throw an exception:
      # this means something wasn't cleaned up right and the log files from a previous run may 
      # not have been handled correctly
      logFilesInTempDir = mlu.common.file.GetAllFilesDepth1(self._tempLogDir)
      if (logFilesInTempDir):
         raise Exception("Unable to copy new MPD log files to the log file temp dir: files already exist there (invalid state).`nPlease check temp dir '{}'".format(self._tempLogDir))

      # Get all the files from the MPD log dir (only depth 1, does not get subfolder files)
      # Copy them to the MPD log temp dir
      mpdLogFiles = mlu.common.file.GetAllFilesDepth1(self._mpdLogDir)
      mlu.common.file.CopyFilesToDirectory(srcFiles=mpdLogFiles, destDir=self._tempLogDir)

      # Also create a 2nd copy of the MPD logs in a subfolder 'original' in the temp logs directory
      originalLogsDir = mlu.common.file.JoinPaths(self._tempLogDir, 'original-bak')
      mlu.common.file.CopyFilesToDirectory(srcFiles=mpdLogFiles, destDir=originalLogsDir)

   
   # TODO: delete mpd.log and all other files in top level dir of MPD logs dir
   def _resetActiveLogFile(self):
      pass

  
   def _decompressLogFiles(self):
      '''
      Decompress/extract any log files in the MPD logs temp dir that are compressed. These compressed
      log files are extracted and turned into normal log files, and the compressed versions of them
      are deleted.
      '''
      # Get a list of which files are compressed (have .gz extension)
      logFiles = mlu.common.file.GetAllFilesDepth1(self._tempLogDir)
      compressedLogFiles = []

      for logFile in logFiles:
         if (mlu.common.file.GetFileExtension(logFile) == "gz"):
            compressedLogFiles.append(logFile)

      # Decompress each gz file, output each uncompressed log file to the temp dir, and delete
      # each original compressed .gz file
      for compressedLogFile in compressedLogFiles:
         baseFilename = mlu.common.file.GetFileBaseName(compressedLogFile)
         extractedFilepath = mlu.common.file.JoinPaths(self._tempLogDir, baseFilename)

         mlu.common.file.DecompressSingleGZFile(compressedLogFile, extractedFilepath)
         mlu.common.file.DeleteFile(compressedLogFile)

   def _getMPDLogTempCacheDirectory(self):
      """
      Gets the absolute filepath of the cache directory inside the project folder where MPD logs will
      be stored temporarily while being processed. This is used by the MPD playstats updater script.
      Also does a check to ensure the cache directory exists and creates it if it doesn't.
      """
      rootCacheDir = mlu.common.file.getMLUCacheDirectory()
      mpdLogCacheDir = mlu.common.file.JoinPaths(rootCacheDir, "mpd-logs")

      if (not mlu.common.file.directoryExists(mpdLogCacheDir)):
         mlu.common.file.createDirectory(mpdLogCacheDir)

      return mpdLogCacheDir



class MPDLogLineCollector:
   def __init__(self, mpdLogDir):

      logFileHandler = MPDLogFileHandler(mpdLogDir=mpdLogDir)
      preparedLogsDir = logFileHandler.prepareLogFilesForDataCollection()
   
      self._logDir = preparedLogsDir


   def collectMPDLogLines(self):
      '''
      Collects and returns all log lines (as MPDLogLine objects) from all the MPD log files currently
      stored in the MPD prepared log (temp) directory. 
      
      Each log file in the prepared logs directory is opened, read, and loaded into an MPDLogLine objects list. 
      This list is then sorted by the timestamp of each line (earliest first) and returned.
      '''

      logFiles = mlu.common.file.GetAllFilesDepth1(self._logDir)
      allMPDLogLines = []

      for logfilepath in logFiles:
         with open(logfilepath, mode='r') as file:
            rawLogfileLines = file.readlines()

         for logLine in rawLogfileLines:
            lineTimestamp = self._getTimestampFromRawLogLine(logLine)
            lineText = self._getTextFromRawLogLine(logLine)

            allMPDLogLines.append(MPDLogLine(timestamp=lineTimestamp, text=lineText))

      # Sort the loglines array - this sorts the array object in place 
      # (does not copy or return a new array, modifies the existing one)
      allMPDLogLines.sort(key=lambda line: line.timestamp)

      return allMPDLogLines
      
   # TODO: UPDATE THIS FUNCTION TO GET THE TIMESTAMP THAT INCLUDES THE YEAR
   def _getTimestampFromRawLogLine(self, line):
      '''
      '''
      lineParts = line.split(" ")
      lineTime = lineParts[0] + " " + lineParts[1] + " " + " " + lineParts[2]

      # Tell the datetime library how to parse this time string from the MPD log line into a timestamp value
      lineFormattedTime = datetime.datetime.strptime(lineTime, "%b %d %Y %H:%M")
      epochTimestamp = lineFormattedTime.timestamp()
      return epochTimestamp


   def _getTextFromRawLogLine(self, line):
      lineParts = line.split(":")
      lineText = lineParts[1]

      # Remove the leading space taken after splitting the string
      lineText = lineText[1:]
      # Remove the newline char at the end
      lineText = lineText.rstrip("\n")

      return lineText







