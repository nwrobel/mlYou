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




    
