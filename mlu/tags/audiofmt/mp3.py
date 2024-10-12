'''
mlu.tags.audiofmt.mp3

Module containing class which reads data for a single mp3 audio file.
'''

import mutagen
from mutagen.mp3 import BitrateMode
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX
from datetime import timedelta

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.utils
import com.nwrobel.mypycommons.string

from mlu.tags import values

class AudioFormatHandlerMP3:
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
        Returns an AudioFileTags object for the tag values for the Mp3 audio file
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)

        title = self._getTagValueFromMutagenInterface(mutagenInterface, 'TIT2')
        artist = self._getTagValueFromMutagenInterface(mutagenInterface, 'TPE1')
        album = self._getTagValueFromMutagenInterface(mutagenInterface, 'TALB')
        albumArtist = self._getTagValueFromMutagenInterface(mutagenInterface, 'TPE2')
        genre = self._getTagValueFromMutagenInterface(mutagenInterface, 'TCON')
        dateLastPlayed = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:PLAY_COUNT')
        rating = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:RATING')

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
        # Use the EasyId3 interface for setting the standard Mp3 tags
        # mutagenInterface = EasyID3(self.audioFilepath)

        # mutagenInterface['title'] = audioFileTags.title
        # mutagenInterface['artist'] = audioFileTags.artist
        # mutagenInterface['album'] = audioFileTags.album
        # mutagenInterface['albumartist'] = audioFileTags.albumArtist
        # mutagenInterface['genre'] = audioFileTags.genre

        # mutagenInterface.save()
        
        # Use the ID3 interface for setting the nonstandard Mp3 tags
        mutagenInterface = ID3(self.audioFilepath, v2_version=3)

        mutagenInterface['TXXX:DATE_LAST_PLAYED'] = TXXX(3, desc='DATE_LAST_PLAYED', text=audioFileTags.dateLastPlayed)
        mutagenInterface['TXXX:PLAY_COUNT'] = TXXX(3, desc='PLAY_COUNT', text=audioFileTags.playCount)
        mutagenInterface['TXXX:RATING'] = TXXX(3, desc='RATING', text=audioFileTags.rating)

        mutagenInterface.save(v2_version=3)

    def _getTagValueFromMutagenInterface(self, mutagenInterface, mutagenKey):
        try:
            if (mypycommons.utils.stringStartsWith(mutagenKey, 'WXXX:')):
                mutagenValue = mutagenInterface[mutagenKey].url
            else:
                mutagenValue = mutagenInterface[mutagenKey].text

            if (len(mutagenValue) == 1):
                tagValue = mutagenValue[0]
            elif (len(mutagenValue) > 1):
                tagValue = ';'.join(mutagenValue)
            else:
                tagValue = ''

        # failure to read tag result in blank values
        # TODO: add logging here
        except Exception:
            tagValue = ''

        return str(tagValue) 