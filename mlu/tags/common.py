'''
mlu.tags.common

Module for functionality that is needed/shared between various other mlu.tags modules.
'''

def formatValuesListToAudioTag(valuesList):
    if (not valuesList):
        return ''
        
    listStr = ';'.join(map(str, valuesList))
    return str(listStr)

def formatAudioTagToValuesList(audioTagStr, valuesAs=''):
    if (not audioTagStr):
        return []
    
    valuesList = audioTagStr.split(';')

    if (valuesAs == 'int'):
        valuesList = [int(value) for value in valuesList]

    elif (valuesAs == 'float'):
        valuesList = [float(value) for value in valuesList]

    else:
        valuesList = [str(value) for value in valuesList]

    return valuesList
