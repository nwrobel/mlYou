'''
merge-mpd-logs.py

This utility script is used to merge several MPD log files into one large file by using concatenation.
The log line entries are ordered from oldest to newest, oldest being first at the top of the file.

'''

import argparse
import datetime

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.settings import MLUSettings

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.logger

mypycommons.logger.initSharedLogger(logDir=MLUSettings.logDir)
logger = mypycommons.logger.getSharedLogger()

import mlu.mpd.logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("masterLogFilepath", 
        help="Filepath of where the master MPD log containing all MPD log lines from all files, should be saved",
        type=str)

    parser.add_argument('--logs', nargs='+', help='List of MPD log filepaths to merge into a single log file', required=True)
    args = parser.parse_args()

    allMPDLogLines = []
    for logFilepath in args.logs:
        currentMPDLogLines = mlu.mpd.logs.collectMPDLogLinesFromLogFile(logFilepath)
        allMPDLogLines += currentMPDLogLines
        logger.info("Found {} MPDLogLines in log file '{}'".format(len(currentMPDLogLines), logFilepath))

    logger.info("MPDLogLines collected total: {}".format(len(allMPDLogLines)))
    logger.info("Removing duplicate MPDLogLines from total list and sorting them oldest -> newest")
    uniqueSortedMPDLogLines = mlu.mpd.logs.removeDuplicateMPDLogLines(allMPDLogLines)

    logger.info("Unique MPDLogLines total: {} ({} were duplicates and were removed)".format(len(uniqueSortedMPDLogLines), len(allMPDLogLines) - len(uniqueSortedMPDLogLines) ))
    logger.info("Dumping all MPDLogLines to master MPD log file '{}'".format(args.masterLogFilepath))
    mlu.mpd.logs.dumpMPDLogLinesToLogFile(destLogFilepath=args.masterLogFilepath, mpdLogLines=uniqueSortedMPDLogLines)