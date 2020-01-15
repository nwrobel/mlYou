import os
from abc import ABC, abstractmethod

class SongTagsHandler(ABC):

    def __init__(self, songFilepath):
        # validate that the given is a valid actual filepath (does not check existence)
        if (not os.path.isabs(songFilepath)):
            raise TypeError("Class field 'songFilepath' must be a valid absolute filepath string (either existent or non-existent)")

        self._songFilepath = songFilepath


    @abstractmethod
    def _validateTagValues(self):
        pass  

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
    def setTags(self):
        pass