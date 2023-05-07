'''
mlu.tags.common

Module for functionality that is needed/shared between various other mlu.tags modules.
'''

def formatValuesListToAudioTag(valuesList):
    '''
    Formats list of data elements into a comma separated string that can be written into audio tag.
    '''
    if (not valuesList):
        return ''
        
    listStr = ';'.join(map(str, valuesList))
    return str(listStr)

def formatAudioTagToValuesList(audioTagStr, valuesAsType=str):
    '''
    Formats audio tag into a list of values.
    '''
    if (not audioTagStr):
        return []
    
    valuesList = audioTagStr.split(';')

    valuesList = [valuesAsType(value) for value in valuesList]
    # if (valuesAs == 'int'):
    #     valuesList = [int(value) for value in valuesList]

    # elif (valuesAs == 'float'):
    #     valuesList = [float(value) for value in valuesList]

    # else:
    #     valuesList = [str(value) for value in valuesList]

    return valuesList
