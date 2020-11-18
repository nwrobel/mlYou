'''
fix-mpd-logs-missing-yr.py

This utility script is used to fix/correct MPD log files that were created without having a proper
timestamp format in their log line timestamps. Such log files are missing the year value in the 
timestamps, making the logs hard to work with for use with playstats. 

This script fixes that and replaces the timestamp in each line with one that is formatted like 
that of the default format used in syslog logs.

'''

import argparse
import datetime

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

import mlu.mpd.logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("logFilepath", 
        help="Absolute filepath of the MPD log to fix the timestamps for, by adding the year to each timestamp.",
        type=str)

    parser.add_argument("startYear", 
        help="The year of the timestamp of the first line in this log file (when log was first written to)",
        type=str)

    args = parser.parse_args()

    rawLogFileLines = mypycommons.file.readFile(args.logFilepath)
    rawLogFileLines = [logLine.replace('\n', '') for logLine in rawLogFileLines]
    fixedRawLogFileLines = []

    firstLineTimestamp = mlu.mpd.logs.getTimestampFromRawLogLineAddYear(logLine=rawLogFileLines[0], year=args.startYear)
    firstLineSyslogFmtTime = mlu.mpd.logs.formatTimestampToSyslogFormat(firstLineTimestamp)

    logTextPart = rawLogFileLines[0].split(' : ')[1]
    fixedRawLogFileLines.append(firstLineSyslogFmtTime + " " + logTextPart)
    del rawLogFileLines[0]

    for logLine in rawLogFileLines:
        lineTimestamp = mlu.mpd.logs.getTimestampFromRawLogLineAddYear(logLine=logLine, year=args.startYear)

        if (firstLineTimestamp > lineTimestamp):
            nextYear = str(int(args.startYear) + 1)
            lineTimestamp = mlu.mpd.logs.getTimestampFromRawLogLineAddYear(logLine=logLine, year=nextYear)

        if (firstLineTimestamp > lineTimestamp):
            raise RuntimeError("Logic error: this log line timestamp is incorrect - it is older than the oldest log line in the file")

        lineSyslogFmtTime = mlu.mpd.logs.formatTimestampToSyslogFormat(lineTimestamp)
        logTextPart = logLine.split(' : ')[1]
        fixedRawLogFileLines.append(lineSyslogFmtTime + " " + logTextPart)

    newLogFileName = "{} {}".format("[YR+FIX]", mypycommons.file.GetFilename(args.logFilepath))
    newLogFilepath = mypycommons.file.JoinPaths(mypycommons.file.getParentDirectory(args.logFilepath), newLogFileName)
    mypycommons.file.writeToFile(filepath=newLogFilepath, content=fixedRawLogFileLines)
