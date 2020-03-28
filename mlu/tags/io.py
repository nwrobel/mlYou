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
            raise ValueError("Class attribute 'audioFilepath' must be a valid absolute filepath string to an existing file")

        self.audioFilepath = audioFilepath
        audioFileExt = mlu.common.file.GetFileExtension(self.audioFilepath)

        if (audioFileExt == '.flac'):
            self.audioFileType = 'flac'
        elif (audioFileExt == '.mp3'):
            self.audioFileType = 'mp3'
        else:
            raise Exception("Cannot open file '{}': Audio file format is not supported".format(self.audioFilepath))


    def getAudioTagValue(self, tagName):
        if (self.audioFileType == 'flac'):
            tagValue = self._getAudioTagValueFromFLACFile(tagName)

        elif (self.audioFileType == 'mp3'):
            tagValue = self._getAudioTagValueFromMp3File(tagName)

        return tagValue


    def setAudioTagValue(self, tagName, newValue):
        if (self.audioFileType == 'flac'):
            self._setAudioTagValueForFLACFile(tagName, newValue)

        elif (self.audioFileType == 'mp3'):
            self._setAudioTagValueForMp3File(tagName, newValue)


    def _getAudioTagValueFromFLACFile(self, tagName):
        tagName = tagName.upper()
        mutagenInterface = mutagen.File(self.audioFilepath)
        try:
            tagValue = mutagenInterface[tagName][0]
        except KeyError:
            tagValue = ''

        return tagValue


    def _setAudioTagValueForFLACFile(self, tagName, newValue):
        tagName = tagName.upper()
        mutagenInterface = mutagen.File(self.audioFilepath)

        mutagenInterface[tagName] = newValue
        mutagenInterface.save()


    def _getAudioTagValueFromMp3File(self, tagName):

        tagName = tagName.upper()
        tagValue = ''

        standardId3Tags = [tag.upper() for tag in EasyID3.valid_keys.keys()]
        if (tagName in standardId3Tags):

            mutagenInterface = EasyID3(self.audioFilepath)

            try:
                tagValue = mutagenInterface[tagName][0]
            except KeyError:
                print('Tag not set')

        else:
            mutagenInterface = mutagen.File(self.audioFilepath)
            id3TagName = "TXXX:{}".format(tagName)

            try:
                tagValue = mutagenInterface[id3TagName].text[0]
            except KeyError:
                print('Tag not set')

        return tagValue


    def _setAudioTagValueForMp3File(self, tagName, newValue):

        tagName = tagName.upper()
        newValueStr = str(newValue)

        standardId3Tags = [tag.upper() for tag in EasyID3.valid_keys.keys()]
        if (tagName in standardId3Tags):

            mutagenInterface = EasyID3(self.audioFilepath)
            mutagenInterface[tagName] = newValueStr
            mutagenInterface.save()

        else:
            mutagenInterface = ID3(self.audioFilepath, v2_version=3)

            mutagenInterface.add(TXXX(3, desc=tagName, text=newValueStr))
            mutagenInterface.save(self.audioFilepath, v2_version=3)
