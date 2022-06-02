'''
mlu.mpd.logs

'''
from collections import Counter

import datetime

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time


   




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




def resetMPDLog(mpdLogFilepath, tempMpdLogFilepath, preserveLastLogLine):

   processedMpdLoglineCount = mypycommons.file.getTextFileLineCount(tempMpdLogFilepath)

      # Remove from the start of the actual log file the number of lines that were 
      # processed in the mpd log from the temp dir earlier - essentially we remove the lines that
      # have been processed already, leaving behind any new lines that may have been created
      # in the time between when the log was first copied to temp and now 

   if (preserveLastLogLine):
      removeFirstNLines = processedMpdLoglineCount - 1
   else:
      removeFirstNLines = processedMpdLoglineCount

   mypycommons.file.removeFirstNLinesFromTextFile(mpdLogFilepath, removeFirstNLines)






