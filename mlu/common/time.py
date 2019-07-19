'''
mlu.common.time

Module containing "common" functionality related to time and timestamp logic.
'''

import datetime


def FormatTimestampForDisplay(timestamp):
    """
    Converts a given epoch timestamp value to a string timestamp format that can be displayed and 
    easily understood. Output format example: "2012-01-27 02:29:33". If the given epoch timestamp
    contains a fractional (decimal) part, it will be rounded to remove it so it can be displayed
    in the output format YYYY-MM-DD HH-MM-SS.
    """
    roundedTimestamp = round(timestamp)
    dt = datetime.datetime.fromtimestamp(roundedTimestamp)
    formattedTime = datetime.datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S")
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

def ApplyDeltaSecondsToTimestamp(startTimestamp, seconds):
    """
    Given a starting time timestamp and a number of seconds, this returns a new epoch timestamp which represents
    that time X seconds before or after the given timestamp. Years can be positive to add time or 
    negative to subtract time. 
    """
    startDt = datetime.datetime.fromtimestamp(startTimestamp)
    newDt = startDt + datetime.timedelta(seconds=seconds)
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


def getCurrentTimestamp():
    """
    Returns the current time as an epoch timestamp.
    """
    dt = datetime.datetime.now()
    return datetime.datetime.timestamp(dt)




    
