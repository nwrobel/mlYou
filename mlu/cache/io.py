"""
mlu.cache.io

This module contains common caching functionality used by other modules within the mlu.cache
package. It deals with writing and reading objects to/from cache locations, such a JSON files.
"""

import json
from collections import OrderedDict


def WriteMLUObjectsToJSONFile(mluObjects, outputFilepath):
    """
    Takes a given list of MLU objects (list of instances of any class defined here in this project), 
    converts each one to JSON, and dumps the JSON array to the given output filepath. The order
    of the properties for each object in the JSON file follows the same order as the properties
    are defined in that class.
    """
    with open(outputFilepath, "w+") as outfile:
        json.dump(mluObjects, outfile, default=_prepareMLUObjectForJSON)


def ReadMLUObjectsFromJSONFile(inputFilepath, mluClassDefinition):
    """
    Given an input JSON filepath, reads in one or more JSON-encoded MLU objects (class instances)
    and converts them back into their original python objects of the given type. Returns a list
    of one or more MLU objects of given type, retrieved from the json data.

    Note: mluClassDefinition must be the class name/class definition for the type of object
    that each JSON item in the file represents.
    """
    with open(inputFilepath, "r") as inputfile:
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


def _prepareMLUObjectForJSON(self):
    # Given the instance of a class defined in this project, create an ordered dictionary out of its 
    # data so it can be coverted to a JSON encoding
    classDataDict = OrderedDict()
    objectProperties = vars(self)

    for key, value in objectProperties.items():
        classDataDict[key] = value

    return classDataDict