'''
mlu.tags.audiofmt.oggOpus

Module containing class which reads data for a single ogg OPUS audio file.
'''

import mutagen
from datetime import timedelta

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.utils

from mlu.tags import values

class AudioFormatHandlerOggOpus:
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
        Returns an AudioFileTags object for the tag values for the FLAC audio file
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)
        tags = mutagenInterface.tags

        title = self._getTagValueFromMutagenInterface(mutagenInterface, 'title')
        artist = self._getTagValueFromMutagenInterface(mutagenInterface, 'artist')
        album = self._getTagValueFromMutagenInterface(mutagenInterface, 'album')
        albumArtist = self._getTagValueFromMutagenInterface(mutagenInterface, 'albumartist')
        genre = self._getTagValueFromMutagenInterface(mutagenInterface, 'genre')
        dateLastPlayed = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_last_played') 
        playCount = self._getTagValueFromMutagenInterface(mutagenInterface, 'play_count')
        rating = self._getTagValueFromMutagenInterface(mutagenInterface, 'rating')

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
        mutagenInterface = mutagen.File(self.audioFilepath)

        mutagenInterface['date_last_played'] = audioFileTags.dateLastPlayed
        mutagenInterface['play_count'] = audioFileTags.playCount
        mutagenInterface['rating'] = audioFileTags.rating

        mutagenInterface.save()

    def _getTagValueFromMutagenInterface(self, mutagenInterface, mutagenKey):
        try:
            mutagenValue = mutagenInterface[mutagenKey]

            if (len(mutagenValue) == 1):
                tagValue = mutagenValue[0]
            elif (len(mutagenValue) > 1):
                tagValue = ';'.join(mutagenValue)
            else:
                tagValue = ''

        except KeyError:
            tagValue = ''

        return tagValue
