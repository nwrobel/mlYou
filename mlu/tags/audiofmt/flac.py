'''
mlu.tags.audiofmt.flac

Module containing class which reads data for a single FLAC audio file.
'''

import mutagen
from datetime import timedelta

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.utils

from mlu.tags import values

class AudioFormatHandlerFLAC:
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

        title = self._getTagValueFromMutagenInterface(mutagenInterface, 'title')
        artist = self._getTagValueFromMutagenInterface(mutagenInterface, 'artist')
        album = self._getTagValueFromMutagenInterface(mutagenInterface, 'album')
        albumArtist = self._getTagValueFromMutagenInterface(mutagenInterface, 'albumartist')
        composer = self._getTagValueFromMutagenInterface(mutagenInterface, 'composer')
        date = self._getTagValueFromMutagenInterface(mutagenInterface, 'date')
        genre = self._getTagValueFromMutagenInterface(mutagenInterface, 'genre')
        trackNumber = self._getTagValueFromMutagenInterface(mutagenInterface, 'tracknumber')
        totalTracks = self._getTagValueFromMutagenInterface(mutagenInterface, 'tracktotal')
        discNumber = self._getTagValueFromMutagenInterface(mutagenInterface, 'discnumber')
        totalDiscs = self._getTagValueFromMutagenInterface(mutagenInterface, 'disctotal')
        bpm = self._getTagValueFromMutagenInterface(mutagenInterface, 'bpm')
        key = self._getTagValueFromMutagenInterface(mutagenInterface, 'key')
        dateAdded = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_added')
        dateAllPlays = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_all_plays')
        dateLastPlayed = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_last_played') 
        playCount = self._getTagValueFromMutagenInterface(mutagenInterface, 'play_count')
        rating = self._getTagValueFromMutagenInterface(mutagenInterface, 'rating')

        audioFileTags = values.AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            composer=composer,
            date=date,
            genre=genre, 
            trackNumber=trackNumber,
            totalTracks=totalTracks,
            discNumber=discNumber,
            totalDiscs=totalDiscs,
            bpm=bpm,
            key=key,
            dateAdded=dateAdded,
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            rating=rating        
        )

        return audioFileTags

    def setTags(self, audioFileTags):
        '''
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)

        mutagenInterface['date_all_plays'] = audioFileTags.dateAllPlays
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
