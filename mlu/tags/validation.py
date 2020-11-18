'''
mlu.tags.validation

This module contains logic responsible for the validation of a single audio file's tag values. All 
audio file tags supported by MLU are validated here.

IN DEVELOPMENT, may or may not be used in the future

'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.time

class AudioFileTagsValidationError(Exception):
    pass

def validateAudioFileTags(audioFileTags):
    '''
    Does validation checking on an AudioFileTags object, ensuring that its current values (the tags
    currently set on the object) are valid relative to that specific tag's requirements. All tag
    validation logic is executed here.

    Throws a validation exception when a tag with an invalid value is found.

    Params:
        audioFileTags: the AudioFileTags object to validate
    '''

    validateDateTagValue(audioFileTags.date)


def validateDateTagValue(value):
    MIN_YEAR = 1900
    currentYear = mypycommons.time.getCurrentYear()

    if ((value < MIN_YEAR) or (value > currentYear)):
        raise AudioFileTagsValidationError("Invalid tag value: date")
