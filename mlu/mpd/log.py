'''
'''
from datetime import datetime
from typing import List

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

from mlu.settings import MLUSettings

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

class MpdLogProvider:
    '''
    '''
    def __init__(self, mluSettings: MLUSettings, commonLogger: mypycommons.logger.CommonLogger) -> None:
        if (not mluSettings):
            raise ValueError("mluSettings not passed")
        if (commonLogger is None):
            raise ValueError("CommonLogger not passed")

        # validate that the filepath exists
        if (not mypycommons.file.pathExists(mluSettings.userConfig.mpdConfig.logFilepath)):
            raise ValueError("logFilepath must be a valid filepath to an existing file: invalid value '{}'".format(mluSettings.userConfig.mpdConfig.logFilepath))

        self.logFilepath = mluSettings.userConfig.mpdConfig.logFilepath
        self._logger = commonLogger.getLogger()

    def getLines(self) -> MpdLogLine:
        self._lines = self._readLogLines()
        return self._lines

    def _readLogLines(self) -> List[MpdLogLine]:
        '''
        Collects all log lines (as MPDLogLine objects) from the MPD log file.
        The list is then sorted by the timestamp of each line (earliest first) and returned.
        '''
        rawLogFileLines = self._getRawLines()
        self._logger.info("Parsing {} lines from MPD log".format(len(rawLogFileLines)))
        allMpdLogLines = []

        for logLine in rawLogFileLines:
            if (logLine):
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