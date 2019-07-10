'''
mlu.cache.io

This module contains common caching functionality used by other modules within the mlu.cache
package. It deals with writing and reading objects to/from cache locations, such a JSON files.
'''

import json
from collections import OrderedDict


def PrepareMLUObjectForJSON(self):
    classDataDict = OrderedDict()
    objectProperties = vars(self)

    for key, value in objectProperties.items():
        classDataDict[key] = value

    return classDataDict


def WriteMLUObjectsToJSONFile(mluObjects, outputFilename):
    with open(outputFilename, 'w+') as outfile:
        json.dump(mluObjects, outfile, default=PrepareMLUObjectForJSON)



def ReadMLUObjectsFromJSONFile(mluObjects, mluClassDefinition, inputFilename):
    with open(inputFilename, 'r') as inputfile:
        mluObjDicts = json.load(inputfile)
        
    # Create a list with one element if only one object dictionary is read from the given json file
    if ( isinstance(mluObjDicts, dict) ):
        mluObjDicts = [mluObjDicts]

    # For each dictionary, which holds the data of a class instance after it's read from json,
    # create a new instance of that class, given the class definition from the parameters, and
    # add it to the list to collect all of them, if there is more than 1
    mluObjs = []
    for objDict in mluObjDicts:
        # Use kwargs "**" to pass in the params to the class constructor
        # "**" will take the dictionary and expand it to make the keyword args and pass it to the 
        # constructor, just as you would normally
        mluObjs.append( mluClassDefinition(**objDict) )

    return mluObjs