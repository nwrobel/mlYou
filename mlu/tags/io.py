'''
mlu.tags.io

Module for functionality related to reading and writing data to tags for any supported audio file 
type.

'''

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX
from mutagen.mp4 import MP4

import mlu.common.file

MP4_STANDARD_TAGS = { 
    'TITLE': '\xa9nam',
    'ARTIST': '\xa9ART',
    'ALBUMARTIST': 'aART',
    'ALBUM': '\xa9alb',
    'COMPOSER': '\xa9wrt',
    'YEAR': '\xa9day',
    'COMMENT': '\xa9cmt',
    'GENRE': '\xa9gen',
    'LYRICS': '\xa9lyr',
    'ENCODED_BY': '\xa9too',
    'COPYRIGHT': 'cprt',
    'TRACKNUMBER': 'trkn',
    'TOTALTRACKS': 'trkn',
    'DISCNUMBER': 'disk',
    'TOTALDISCS': 'disk'
}
    
class AudioFileTagIOHandler:
    '''
    Class that handles the reading and writing of tag data values for a single audio file. This
    file can be any of the supported audio file types.

    Constructor params:
        audioFilepath: absolute filepath of the audio file
    '''
    def __init__(self, audioFilepath):
        # validate that the filepath exists
        if (not mlu.common.file.FileExists(audioFilepath)):
            raise ValueError("Class attribute 'audioFilepath' must be a valid absolute filepath string to an existing file")

        self.audioFilepath = audioFilepath
        audioFileExt = mlu.common.file.GetFileExtension(self.audioFilepath)

        if (audioFileExt == '.flac'):
            self.audioFileType = 'flac'
        elif (audioFileExt == '.mp3'):
            self.audioFileType = 'mp3'
        elif (audioFileExt == '.m4a'):
            self.audioFileType = 'm4a'
        else:
            raise Exception("Cannot open file '{}': Audio file format is not supported".format(self.audioFilepath))


    def getAudioTagValue(self, tagName):
        '''
        Gets the string value of the given tag for the audio file. This will return an empty string
        if the tag is empty or undefined.

        Params:
            tagName: name of the audio file tag
        '''
        if (self.audioFileType == 'flac'):
            tagValue = self._getAudioTagValueFromFLACFile(tagName)

        elif (self.audioFileType == 'mp3'):
            tagValue = self._getAudioTagValueFromMp3File(tagName)

        elif (self.audioFileType == 'm4a'):
            tagValue = self._getAudioTagValueFromM4AFile(tagName)

        return tagValue


    def setAudioTagValue(self, tagName, newValue):
        '''
        Sets the given tag to the specified value for the audio file.

        Params:
            tagName: name of the audio file tag to set the value for
            newValue: value to set for the given tag
        '''
        if (self.audioFileType == 'flac'):
            self._setAudioTagValueForFLACFile(tagName, newValue)

        elif (self.audioFileType == 'mp3'):
            self._setAudioTagValueForMp3File(tagName, newValue)

        elif (self.audioFileType == 'm4a'):
            self._setAudioTagValueForM4AFile(tagName, newValue)


    def _getAudioTagValueFromFLACFile(self, tagName):
        '''
        Gets the string value of the given tag for a FLAC audio file.

        Params:
            tagName: name of the audio file tag
        '''
        tagName = tagName.upper()
        mutagenInterface = mutagen.File(self.audioFilepath)
        try:
            tagValue = mutagenInterface[tagName][0]
        except KeyError:
            tagValue = ''

        return tagValue


    def _setAudioTagValueForFLACFile(self, tagName, newValue):
        '''
        Sets the given tag to the specified value for a FLAC audio file.

        Params:
            tagName: name of the audio file tag to set the value for
            newValue: value to set for the given tag
        '''
        tagName = tagName.upper()
        mutagenInterface = mutagen.File(self.audioFilepath)

        mutagenInterface[tagName] = newValue
        mutagenInterface.save()


    def _getAudioTagValueFromMp3File(self, tagName):
        '''
        Gets the string value of the given tag for an MP3 audio file.

        Params:
            tagName: name of the audio file tag
        '''
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
        '''
        Sets the given tag to the specified value for an MP3 audio file.

        Params:
            tagName: name of the audio file tag to set the value for
            newValue: value to set for the given tag
        '''
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


    def _getAudioTagValueFromM4AFile(self, tagName):
        '''
        Gets the string value of the given tag for an M4A/AAC audio file.

        Params:
            tagName: name of the audio file tag
        '''
        tagName = tagName.upper()
        tagValue = ''
        mutagenInterface = MP4(self.audioFilepath)

        try:
            if (tagName in MP4_STANDARD_TAGS):
                mp4TagName = MP4_STANDARD_TAGS[tagName]

                # Get the tag value from the tuple list value for these tags
                # They are stored as lists of tuples for track and disc numbers:
                # (TRACKNUMBER, TOTALTRACKS) and (DISCNUMBER, TOTALDISKS)
                if (tagName == 'TRACKNUMBER' or tagName == 'DISCNUMBER'):
                    tagValue = mutagenInterface.tags[mp4TagName][0][0]

                elif (tagName == 'TOTALTRACKS' or tagName == 'TOTALDISCS'):
                    tagValue = mutagenInterface.tags[mp4TagName][0][1]

                else:
                    tagValue = mutagenInterface.tags[mp4TagName][0]
                    
            else:
                mp4TagName = '----:com.apple.iTunes:{}'.format(tagName)
                tagValue = mutagenInterface[mp4TagName][0].decode('utf-8')

        except KeyError:
            print('Tag not set')

        return str(tagValue)


    def _setAudioTagValueForM4AFile(self, tagName, newValue):
        '''
        Sets the given tag to the specified value for an M4A/AAC audio file.

        Params:
            tagName: name of the audio file tag to set the value for
            newValue: value to set for the given tag
        '''
        tagName = tagName.upper()
        newValueStr = str(newValue)

        mutagenInterface = MP4(self.audioFilepath)

        if (tagName in MP4_STANDARD_TAGS):
            mp4TagName = MP4_STANDARD_TAGS[tagName]

        else:
            mp4TagName = '----:com.apple.iTunes:{}'.format(tagName)

        # These tags are stored as lists of tuples for track and disc numbers:
        # (TRACKNUMBER, TOTALTRACKS) and (DISCNUMBER, TOTALDISKS)
        if (tagName == 'TRACKNUMBER'):
            totalTracksValue = self._getAudioTagValueFromM4AFile('TOTALTRACKS')
            mutagenInterface.tags[mp4TagName][0] = (int(newValueStr), int(totalTracksValue))

        elif (tagName == 'TOTALTRACKS'):
            trackNumValue = self._getAudioTagValueFromM4AFile('TRACKNUMBER')
            mutagenInterface.tags[mp4TagName][0] = (int(trackNumValue), int(newValueStr))

        elif (tagName == 'DISCNUMBER'):
            totalDiscsValue = self._getAudioTagValueFromM4AFile('TOTALDISCS')
            mutagenInterface.tags[mp4TagName][0] = (int(newValueStr), int(totalDiscsValue))

        elif (tagName == 'TOTALDISCS'):
            discNumValue = self._getAudioTagValueFromM4AFile('DISCNUMBER')
            mutagenInterface.tags[mp4TagName][0] = (int(discNumValue), int(newValueStr))

        else:
            mutagenInterface.tags[mp4TagName] = (newValueStr.encode('utf-8'))
        
        mutagenInterface.save()
