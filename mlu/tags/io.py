'''
mlu.tags.io

Module for functionality related to reading and writing data to tags for any generic audio file 
type.
'''

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX

import mlu.common.file

class AudioFileTagIOHandler:
    def __init__(self, audioFilepath):
        # validate that the given is a valid possible filepath
        if (not mlu.common.file.isValidPossibleFilepath(audioFilepath)):
            raise TypeError("Class attribute 'audioFilepath' must be a valid absolute filepath string (either existent or non-existent)")

        self.audioFilepath = audioFilepath
        self.mutagenMp3Interface = None
        self.mutagenFlacInterface = None

        # audioFileExt = mlu.common.file.GetFileExtension(self.audioFilepath)

        # if (audioFileExt == '.flac'):
        #     self.mutagenFlacInterface = mutagen.File(self.audioFilepath)
        # elif (audioFileExt == '.mp3'):
        #     self.mutagenMp3Interface = ID3(self.audioFilepath, v2_version=3)
        # else:
        #     raise Exception("Cannot open file '{}': Audio file format is not supported".format(self.audioFilepath))

    def getAudioTagValue(self, tagName):

        # if (self.mutagenFlacInterface):
        #     mutagenInterface = self.mutagenFlacInterface
        # elif (self.mutagenMp3Interface):
        #     mutagenInterface = self.mutagenMp3Interface
        # else:
        #     raise Exception("No mutagen tag interface instance was found")

        # try:
        #     tagValue = mutagenInterface[tagName][0]
        # except KeyError:
        #     tagValue = ''

        keys = mutagen.File(self.audioFilepath).keys()
        mutagen.File(self.audioFilepath)['TXXX:play_count'].text

        return keys


    def setAudioTagValue(self, tagName, newValue):

        if (self.mutagenFlacInterface):
            mutagenInterface = self.mutagenFlacInterface
        elif (self.mutagenMp3Interface):
            mutagenInterface = self.mutagenMp3Interface
        else:
            raise Exception("No mutagen tag interface instance was found")

        newValueStr = str(newValue)
        mutagenInterface.add(TXXX(3, desc=tagName ,text=newValueStr))
        mutagenInterface.save(self.audioFilepath, v2_version=3)
    
        # self.mutagenTagInterface[tagName] = newValue 
        # self.mutagenTagInterface.save()
