'''
mlu.tags.base

First created: 01/15/20
Last modified: 01/16/20

This module contains the definition of the base, abstract class SongTagsHandler. This class serves
as a blueprint and partial starting implementation for other SongTagsHandler-type classes in the 
tags module to build off of.

''' 

import os
from abc import ABC, abstractmethod

class SongTagsHandler(ABC):
    '''
    Abstract base class that is a blueprint and partial starting implementation for the 
    SongTagsHandler-type classes, which handle specific sets of audio tags, to be built from.

    The blueprint requires that a tags handler class implement 4 public methods and 1 private method:
        readTags: to read the tag values from the audio file (all tags are assumed to be present)
        writeTags: to write the tag values to the audio file
        getTags: to return the tag values of this file to the outside code
        updateTags: to validate and set (update) the tag values to the given values
        _validateTagValues: to validate the tags, throwing an exception if they are invalid (used
            by setTags)

    All child classes must accept the param 'songFilepath' as their single constructor argument, 
    which is the path of the audio file that the tag handler represents. 
    This is done by calling the super class (this class) and passing the songFilepath param to it.
    This class will do validation for the songFilepath given.

    This abstract class contains the following instance variables:
        _songFilepath: string, filepath for this song/audio file
        _tagsHaveBeenSet: bool, whether or not setTags() has been called for this tags handler 
         
    '''
    def __init__(self, songFilepath):
        # validate that the given is a valid actual filepath (does not check existence)
        if (not os.path.isabs(songFilepath)):
            raise TypeError("Class attribute 'songFilepath' must be a valid absolute filepath string (either existent or non-existent)")

        self._songFilepath = songFilepath
        self._tagsHaveBeenSet = False

    @abstractmethod
    def readTags(self):
        pass

    @abstractmethod
    def writeTags(self):
        pass

    @abstractmethod
    def getTags(self):
        pass

    @abstractmethod
    def updateTags(self):
        pass

    @abstractmethod
    def _validateTagValues(self):
        pass