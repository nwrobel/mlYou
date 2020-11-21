'''
mlu.mpd.logs

'''
from collections import Counter

import datetime

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

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

      if (not mypycommons.time.isValidTimestamp(timestamp)):
         raise ValueError("Class attribute 'timestamp' must be a valid timestamp, value '{}' is invalid".format(timestamp))

      self.text = text
      self.timestamp = timestamp

def collectMPDLogLinesFromLogFile(mpdLogFilepath):
   '''
   Collects and returns all log lines (as MPDLogLine objects) from all the MPD log files currently
   stored in the MPD prepared log (temp) directory. 
   
   Each log file in the prepared logs directory is opened, read, and loaded into an MPDLogLine objects list. 
   This list is then sorted by the timestamp of each line (earliest first) and returned.
   '''

   rawLogFileLines = mypycommons.file.readFile(mpdLogFilepath)
   rawLogFileLines = [logLine.replace('\n', '') for logLine in rawLogFileLines]
   allMPDLogLines = []

   for logLine in rawLogFileLines:
      # Try using the start year first
      lineTimestamp = getTimestampFromRawLogLine(logLine)
      lineText = getTextFromRawLogLine(logLine)

      allMPDLogLines.append(MPDLogLine(timestamp=lineTimestamp, text=lineText))

   # Sort the loglines array
   sortedLines = sortMPDLogLinesByTimestamp(allMPDLogLines)
   return sortedLines

def sortMPDLogLinesByTimestamp(mpdLogLines):
   mpdLogLines.sort(key=lambda line: line.timestamp)
   return mpdLogLines

def removeDuplicateMPDLogLines(mpdLogLines):
   mpdLogLinesCollapsed = []
   for mpdLogLine in mpdLogLines:
      mpdLogLinesCollapsed.append(str(mpdLogLine.timestamp) + "(|)" + mpdLogLine.text)
   
   uniqueLogLinesCollapsed = set(mpdLogLinesCollapsed)

   uniqueMPDLogLines = []
   for logLineCollapsed in uniqueLogLinesCollapsed:
      lineTimestamp = float(logLineCollapsed.split("(|)")[0])
      lineText = logLineCollapsed.split("(|)")[1]
      uniqueMPDLogLines.append(MPDLogLine(timestamp=lineTimestamp, text=lineText))

   sortedUniqueMPDLogLines = sortMPDLogLinesByTimestamp(uniqueMPDLogLines)
   return sortedUniqueMPDLogLines

def dumpMPDLogLinesToLogFile(destLogFilepath, mpdLogLines):
   rawLogLines = []
   for mpdLogLine in mpdLogLines:
      timestampSyslogFmt = formatTimestampToSyslogFormat(mpdLogLine.timestamp)
      rawLogLine = timestampSyslogFmt + " " + mpdLogLine.text

      rawLogLines.append(rawLogLine)

   mypycommons.file.writeToFile(filepath=destLogFilepath, content=rawLogLines)

def formatTimestampToSyslogFormat(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    formattedTime = datetime.datetime.strftime(dt, "%Y-%m-%dT%H:%M:%S.%f-04:00")
    return formattedTime

def getTimestampFromRawLogLine(logLine):
   '''
   Gets epoch timestamp from the raw log line of a log file - for the new, MPD logfiles that use syslog
   and timestamps have the year
   '''
   lineTimeData = logLine[0:26]
   lineDatetime = datetime.datetime.strptime(lineTimeData, "%Y-%m-%dT%H:%M:%S.%f")
   epochTimestamp = lineDatetime.timestamp()

   return epochTimestamp

def getTimestampFromRawLogLineAddYear(logLine, year):
    '''
    Gets epoch timestamp from the raw log line of a log file - for the OLD, MPD default logfiles with
    timestamps missing the year
    '''
    timePart = logLine.split(' : ')[0]
    timePartWithYear = "{} {}".format(year, timePart)

    # Tell the datetime library how to parse this time string from the MPD log line into a timestamp value
    lineDatetime = datetime.datetime.strptime(timePartWithYear, "%Y %b %d %H:%M")
    epochTimestamp = lineDatetime.timestamp()

    return epochTimestamp

def getTextFromRawLogLine(logLine):
   lineTextData = logLine[33:]
   lineText = lineTextData.rstrip("\n")

   return lineText







