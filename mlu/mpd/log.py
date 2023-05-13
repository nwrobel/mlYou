'''
'''
from datetime import datetime
from typing import List

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
from com.nwrobel.mypycommons.logger import CommonLogger

class MpdLogLine:
   '''
   Class representing a single log line entry from an MPD log file.

   Params:
      text: what the log actually says (log line minus the string timestamp info)
      timestamp: time for when this log line occurred/was written, as an epoch timestamp (float or int)
      originalText: the full line text as originally read from the file
   '''
   def __init__(self, text: str, dateTime: datetime, originalText: str) -> None:
        # perform validation on input data
        if (not text):
            raise ValueError("logFilepath not passed")
        if (not originalText):
            raise ValueError("originalText not passed")
        if (dateTime is None):
            raise ValueError("dateTime not passed")

        self.text = text
        self.dateTime = dateTime
        self.originalText = originalText

class MpdLog:
    '''
    '''
    def __init__(self, logFilepath: str, commonLogger: CommonLogger) -> None:
        if (not logFilepath):
            raise ValueError("logFilepath not passed")
        if (commonLogger is None):
            raise ValueError("CommonLogger not passed")

        # validate that the filepath exists
        if (not mypycommons.file.pathExists(logFilepath)):
            raise ValueError("logFilepath must be a valid filepath to an existing file: invalid value '{}'".format(logFilepath))

        self.logFilepath = logFilepath
        self._logger = commonLogger.getLogger()
        self._lines = self._readLogLines()

    def getLines(self) -> MpdLogLine:
        return self._lines

    def reset(self, mpdLogLineToPreserve: MpdLogLine) -> None:
        '''
        
        '''
        currentLines = self._getRawLines()
        previousLines = [logLine.originalText for logLine in self._lines]
        newLines = [currentLine for currentLine in currentLines if (currentLine not in previousLines)]

        mypycommons.file.clearFileContents(self.logFilepath)

        # Insert the line to preserve at the beginning of the list of new lines (if there is one), 
        # since the line to preserve is older than the newer lines
        if (mpdLogLineToPreserve):
            newLines.insert(0, mpdLogLineToPreserve.originalText)     

        mypycommons.file.writeToFile(self.logFilepath, newLines)

    def _readLogLines(self) -> List[MpdLogLine]:
        '''
        Collects all log lines (as MPDLogLine objects) from the MPD log file.
        The list is then sorted by the timestamp of each line (earliest first) and returned.
        '''
        rawLogFileLines = self._getRawLines()
        allMpdLogLines = []

        for logLine in rawLogFileLines:
            # Try using the start year first
            lineDatetime = self._getDatetimeFromRawLogLine(logLine)
            lineText = self._getTextFromRawLogLine(logLine)

            allMpdLogLines.append(
                MpdLogLine(dateTime=lineDatetime, text=lineText, originalText=logLine)
            )

        # Sort the loglines array
        sortedLines = self._sortLogLinesByDatetime(allMpdLogLines)
        return sortedLines

    def _getRawLines(self) -> List[str]:
        rawLogFileLines = mypycommons.file.readFile(self.logFilepath)
        rawLogFileLines = [logLine.replace('\n', '') for logLine in rawLogFileLines]
        return rawLogFileLines

    def _getDatetimeFromRawLogLine(self, logLine: str) -> float:
        '''
        Gets epoch timestamp from the raw log line of a log file - for the new, MPD logfiles that use syslog
        and timestamps have the year
        '''
        lineTimeData = logLine[0:26]
        lineDatetime = datetime.strptime(lineTimeData, "%Y-%m-%dT%H:%M:%S.%f")
        return lineDatetime

    def _getTextFromRawLogLine(self, logLine: str) -> str:
        lineText = logLine[33:]
        return lineText

    def _sortLogLinesByDatetime(self, mpdLogLines: List[MpdLogLine]) -> List[MpdLogLine]:
        mpdLogLines.sort(key=lambda line: line.dateTime)
        return mpdLogLines