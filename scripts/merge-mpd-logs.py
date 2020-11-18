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


from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

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
        allMPDLogLines += mlu.mpd.logs.collectMPDLogLinesFromLogFile(logFilepath)

    allMPDLogLinesSorted = mlu.mpd.logs.sortMPDLogLinesByTimestamp(allMPDLogLines)
    mlu.mpd.logs.dumpMPDLogLinesToLogFile(destLogFilepath=args.masterLogFilepath, mpdLogLines=allMPDLogLinesSorted)