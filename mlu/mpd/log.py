'''
'''
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
      originalText: the full line text as originally read from the file
   '''
   def __init__(self, text, epochTimestamp, originalText):
      # perform validation on input data
      if (not text) or (not isinstance(text, str)):
         raise TypeError("Class attribute 'text' must be a non-empty string")

      if (not mypycommons.time.isValidTimestamp(epochTimestamp)):
         raise ValueError("Class attribute 'timestamp' must be a valid timestamp, value '{}' is invalid".format(timestamp))

      self.text = text
      self.epochTimestamp = epochTimestamp
      self.originalText = originalText

class MPDLog:
    '''
    '''
    def __init__(self, filepath):
        if (not filepath) or (not isinstance(filepath, str)):
         raise TypeError("Class attribute 'filepath' must be a non-empty string")

        # validate that the filepath exists
        if (not mypycommons.file.isFile(filepath)):
            raise ValueError("Class attribute 'filepath' must be a valid filepath to an existing file: invalid value '{}'".format(logFilepath))

        self.filepath = filepath
        self.lines = self._readLogLines()

    def reset(self, mpdLogLineToPreserve):
        '''
        Save given last log line by default
        '''
        currentLines = self._getRawLines()
        previousLines = [logLine.originalText for logLine in self.lines]
        newLines = [currentLine for currentLine in currentLines if (currentLine not in previousLines)]

        mypycommons.file.clearFileContents(self.filepath)

        # Insert the line to preserve at the beginning of the list of new lines (if there is one), 
        # since the line to preserve is older than the newer lines
        if (mpdLogLineToPreserve):
            newLines.insert(0, mpdLogLineToPreserve.originalText)     

        mypycommons.file.writeToFile(self.filepath, newLines)

    def _readLogLines(self):
        '''
        Collects all log lines (as MPDLogLine objects) from the MPD log file.
        The list is then sorted by the timestamp of each line (earliest first) and returned.
        '''
        rawLogFileLines = self._getRawLines()
        allMPDLogLines = []

        for logLine in rawLogFileLines:
            # Try using the start year first
            lineTimestamp = self._getTimestampFromRawLogLine(logLine)
            lineText = self._getTextFromRawLogLine(logLine)

            allMPDLogLines.append(MPDLogLine(epochTimestamp=lineTimestamp, text=lineText, originalText=logLine))

        # Sort the loglines array
        sortedLines = self._sortMPDLogLinesByTimestamp(allMPDLogLines)
        return sortedLines

    def _getRawLines(self):
        rawLogFileLines = mypycommons.file.readFile(self.filepath)
        rawLogFileLines = [logLine.replace('\n', '') for logLine in rawLogFileLines]
        return rawLogFileLines

    def _getTimestampFromRawLogLine(self, logLine):
        '''
        Gets epoch timestamp from the raw log line of a log file - for the new, MPD logfiles that use syslog
        and timestamps have the year
        '''
        lineTimeData = logLine[0:26]
        lineDatetime = datetime.datetime.strptime(lineTimeData, "%Y-%m-%dT%H:%M:%S.%f")
        epochTimestamp = lineDatetime.timestamp()

        return epochTimestamp

    def _getTextFromRawLogLine(self, logLine):
        lineText = logLine[33:]
        return lineText

    def _sortMPDLogLinesByTimestamp(self, mpdLogLines):
        mpdLogLines.sort(key=lambda line: line.epochTimestamp)
        return mpdLogLines