'''
mlu.tags.common

Module for functionality that is needed/shared between various other mlu.tags modules.
'''

def formatValuesListToAudioTagString(valuesList):
    listStr = ';'.join(map(str, valuesList))
    return listStr

def formatAudioTagStringToValuesList(audioTagStr, valuesAsInt=False):
    valuesList = audioTagStr.split(';')

    if (valuesAsInt):
        valuesList = [int(value) for value in valuesList]
    else:
        valuesList = [str(value) for value in valuesList]

    return valuesList
