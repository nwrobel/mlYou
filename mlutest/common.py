"""
mlutest.common

This module contains functions that are commonly needed/used by various MLU unit tests in the
mlutest package. They deal with setting up and teardown of test cases and creation of random test
data.
"""
import envsetup
envsetup.PreparePythonProjectEnvironment()


from random import randrange
from random import choice
from string import ascii_letters, ascii_lowercase

import mlu.common.time


def getRandomTimestamp():
    """
    Returns a pseudo-random epoch timestamp for a time sometime in the past 15 years.
    """
    now = mlu.common.time.getCurrentTimestamp()
    # 500 million seconds ~ 15 years of range
    # make it negative to go into the past
    deltaSeconds = -(getRandomNumber(min=0, max=500000000)) 
    randomTimestamp = mlu.common.time.ApplyDeltaSecondsToTimestamp(startTimestamp=now, seconds=deltaSeconds)

    return randomTimestamp


def getRandomFilepath():
    """
    Returns a pseudo-random absolute filepath string of a (most likely) non-existent file. The filepath
    returned will have a max depth of 10 and each folder name and the file name will be a maximum of
    15 characters long. Each filepath will have some drive letter A-Z, and all file and folder names
    will be lowercase. The file will have a random, 3 lowercase letter file extension.
    """
    maxDepth = 10
    maxFileOrFolderNameLength = 15

    # Create the random file name and extension, and random drive letter
    randomFilenameLength = getRandomNumber(min=1, max=maxFileOrFolderNameLength)
    randomFileName = getRandomString(length=randomFilenameLength)
    randomFileExt = getRandomString(length=3)
    randomDriveLetter = (choice(ascii_letters)).upper()

    # Set up the random filepath and find a random depth for how deep the random file will be
    randomFilepath = randomDriveLetter + ":\\"
    randomDepth = getRandomNumber(min=1, max=maxDepth)

    # Create random subfolder names and append them to the random filepath until depth is satisfied
    for d in range(randomDepth):
        folderNameLength = getRandomNumber(min=1, max=maxFileOrFolderNameLength)
        folderName = getRandomString(folderNameLength)
        randomFilepath += folderName + "\\"

    # Add the filename and extension to the parent dir path to complete the filepath
    randomFilepath += randomFileName + "." + randomFileExt
    return randomFilepath


def getRandomString(length):
    """
    Returns a pseudo-random string, composed of only lowercase letters (no digits).
    """
    return (''.join(choice(ascii_lowercase) for i in range(length)))


def getRandomNumber(min, max):
    """
    Returns a pseudo-random integer that is greater than or equal to the given minimum and less than
    or equal to the given maximum numbers.
    """
    return randrange(start=min, stop=(max + 1))
