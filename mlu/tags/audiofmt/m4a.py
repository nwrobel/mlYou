'''
mlu.tags.audiofmt.m4a

Module containing class which reads data for a single m4a audio file.
'''

import mutagen
from mutagen.mp4 import MP4
from datetime import timedelta

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.utils

from mlu.tags import values

class AudioFormatHandlerM4A:
    def __init__(self, audioFilepath):
        self.audioFilepath = audioFilepath

    def getProperties(self):
        '''
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)
        duration = timedelta(seconds=mutagenInterface.info.length)

        audioProperties = values.AudioFileProperties(duration)
        return audioProperties


    def getTags(self):
        '''
        Returns an AudioFileTags object for the tag values for the M4A audio file
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)

        # Standard M4A tags
        title = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9nam')
        artist = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9ART')
        albumArtist = self._getTagValueFromMutagenInterface(mutagenInterface, 'aART')
        album = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9alb')
        genre = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9gen')
        dateLastPlayed = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:PLAY_COUNT')
        rating = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:RATING')

        audioFileTags = values.AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            genre=genre, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            rating=rating
        )

        return audioFileTags

    def setTags(self, audioFileTags):
        '''
        '''
        mutagenInterface = MP4(self.audioFilepath)

        # Standard M4A tags
        # mutagenInterface['\xa9nam'] = audioFileTags.title
        # mutagenInterface['\xa9ART'] = audioFileTags.artist
        # mutagenInterface['\xa9alb'] = audioFileTags.album
        # mutagenInterface['aART'] = audioFileTags.albumArtist
        # mutagenInterface['\xa9gen'] = audioFileTags.genre

        # Nonstandard (custom) M4A tags
        mutagenInterface['----:com.apple.iTunes:DATE_LAST_PLAYED'] = (audioFileTags.dateLastPlayed).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:PLAY_COUNT'] = (audioFileTags.playCount).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:RATING'] = (audioFileTags.rating).encode('utf-8')

        mutagenInterface.save()

    def _getTagValueFromMutagenInterface(self, mutagenInterface, mutagenKey):

        try:    
            mutagenValue = mutagenInterface.tags[mutagenKey]

            if ('----:com.apple.iTunes:' in mutagenKey):
                if (len(mutagenValue) == 1):
                    tagValue = mutagenValue[0].decode('utf-8')
                elif (len(mutagenValue) > 1):
                    tagValueList = [value.decode('utf-8') for value in mutagenValue]
                    tagValue = ';'.join(tagValueList)
                else:
                    tagValue = ''

            else:
                if (len(mutagenValue) == 1):
                    tagValue = mutagenValue[0]
                elif (len(mutagenValue) > 1):
                    tagValue = ';'.join(mutagenValue)
                else:
                    tagValue = ''

        except KeyError:
            tagValue = ''

        return tagValue
