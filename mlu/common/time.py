'''
mlu.common.time

Module containing "common" functionality related to time and timestamp logic.
'''

import datetime


def FormatTimestampForDisplay(timestamp):
    """
    Converts a given epoch timestamp (integer) value to a string timestamp format that can be displayed and 
    easily understood. Output format example: "2012-01-27 02:29:33"
    """
    dt = datetime.datetime.fromtimestamp(timestamp)
    formattedTime = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    return formattedTime


def ApplyDeltaYearsToTimestamp(startTimestamp, years):
    """
    Given a starting time timestamp and a number of years, this returns a new epoch timestamp which represents
    that time X years before or after the given timestamp. Years can be positive to add time or 
    negative to subtract time. 
    """
    startDt = datetime.datetime.fromtimestamp(startTimestamp)
    newDt = startDt + datetime.timedelta(years=years)
    newTimestamp = datetime.datetime.timestamp(newDt)

    return newTimestamp


def ConvertSecondsToTimestamp(seconds):
    """
    Converts the given duration, represented in seconds, into the duration represented as epoch 
    timestamp duration/time delta.
    """
    secondsDt = datetime.timedelta(seconds=seconds)
    secondsTimestamp = datetime.datetime.timestamp(secondsDt)
    return secondsTimestamp


def GetCurrentYear():
    """
    Returns the 4 digit integer value of the current calendar year.
    """
    currentYear = (datetime.datetime.now()).year  
    return int(currentYear) 




    
