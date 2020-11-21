'''
mlu.tags.io

This module deals with reading tag values from and writing tag values to an audio file. Contains
the AudioFileTags object class and the AudioFileTagsIOHandler class definitions.

Supports tag IO for FLAC, Mp3, and M4A audio file types. Only gets/sets tags that are supported by
the MLU project. These supported tags are the properties of the AudioFileTags object.
'''

# TODO: set up validation of tag values using the mlu.tags.validation module

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX
from mutagen.mp4 import MP4

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time

logger = mypycommons.logger.getSharedLogger()

import mlu.tags.validation

SUPPORTED_AUDIO_TYPES = ['flac', 'mp3', 'm4a']

def getAudioFileDurationAsTimestamp(audioFilepath):
    mutagenInterface = mutagen.File(audioFilepath)
    durationSeconds = mutagenInterface.info.length
    durationTimestamp = mypycommons.time.convertSecondsToTimestamp(durationSeconds)

    return durationTimestamp

class AudioFileTags:
    '''
    Data structure holding the values for a single audio file of all the tags supported by MLU.
    '''

    def __init__(
        self, 
        title,
        artist,
        album,
        albumArtist,
        genre, 
        dateAllPlays, 
        dateLastPlayed, 
        playCount, 
        votes, 
        rating
    ):
        self.title = title
        self.artist = artist
        self.album = album
        self.albumArtist = albumArtist
        self.genre = genre
        self.dateAllPlays = dateAllPlays
        self.dateLastPlayed = dateLastPlayed
        self.playCount = playCount
        self.votes = votes
        self.rating = rating

    def equals(self, otherAudioFileTags):
        tagsAreEqual = (
            self.title == otherAudioFileTags.title and
            self.artist == otherAudioFileTags.artist and
            self.album == otherAudioFileTags.album and
            self.albumArtist == otherAudioFileTags.albumArtist and
            self.genre == otherAudioFileTags.genre and
            self.dateAllPlays == otherAudioFileTags.dateAllPlays and
            self.dateLastPlayed == otherAudioFileTags.dateLastPlayed and
            self.playCount == otherAudioFileTags.playCount and
            self.votes == otherAudioFileTags.votes and
            self.rating == otherAudioFileTags.rating
        )

        return tagsAreEqual


    # def validate(self):
    #     mlu.tags.validation.validateAudioFileTags(self)


class AudioFileTagIOHandler:
    '''
    Class that handles the reading and writing of tag data values for a single audio file. This
    file can be any of the supported audio file types.

    The trackNumber, totalTracks, discNumber, and totalDiscs tags are not supported by MLU for M4A 
    files due to limitations of mutagen.

    Constructor params:
        audioFilepath: absolute filepath of the audio file
    '''

    def __init__(self, audioFilepath):
        # validate that the filepath exists
        if (not mypycommons.file.fileExists(audioFilepath)):
            raise ValueError("Class attribute 'audioFilepath' must be a valid filepath to an existing file: invalid value '{}'".format(audioFilepath))

        self.audioFilepath = audioFilepath

        # Strip the dot from the file extension to get the audio file type, used by this class
        self._audioFileType = mypycommons.file.GetFileExtension(self.audioFilepath).replace('.', '')

        # Check that the given audio file type is supported
        if (self._audioFileType not in SUPPORTED_AUDIO_TYPES):
            raise Exception("Cannot open file '{}': Audio file format is not supported".format(self.audioFilepath))

    def getTags(self):
        '''
        Returns an AudioFileTags object representing all the values for all the tags on this audio
        file that we care about (only those tags supported by MLU).

        This method performs a read operation of the audio file to fetch the latest tags each time.
        '''

        if (self._audioFileType == 'flac'):
            audioFileTags = self._getTagsForFLACFile()

        elif (self._audioFileType == 'mp3'):
            audioFileTags = self._getTagsForMp3File()

        elif (self._audioFileType == 'm4a'):
            audioFileTags = self._getTagsForM4AFile()

        return audioFileTags

    def setTags(self, audioFileTags):
        '''
        Sets the tags on this audio file to those represented by the given AudioFileTags object.
        This method performs a write operation on the audio file to write the given tag values each
        time. 
        
        Validation is performed on each tag value and an AudioFileTagsValidationError will be thrown
        if any tag values are invalid.
        '''

        # TODO: perform validation here

        # Check to see whether or not the new tags to be set are actually new (did the values actually
        # change?): if not, a write operation is not needed
        currentTags = self.getTags()
        if (currentTags.equals(audioFileTags)):
            logger.debug("setTags() write operation skipped (no change needed): the current tag values are the same as the new given tag values")

        else:
            if (self._audioFileType == 'flac'):
                self._setTagsForFLACFile(audioFileTags)

            elif (self._audioFileType == 'mp3'):
                self._setTagsForMp3File(audioFileTags)

            elif (self._audioFileType == 'm4a'):
                self._setTagsForM4AFile(audioFileTags)

    def _getTagsForFLACFile(self):
        '''
        Returns an AudioFileTags object for the tag values for the FLAC audio file
        '''

        mutagenInterface = mutagen.File(self.audioFilepath)

        title = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'title')
        artist = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'artist')
        album = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'album')
        albumArtist = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'albumartist')
        genre = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'genre')
        dateAllPlays = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date_all_plays')
        dateLastPlayed = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date_last_played') 
        playCount = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'play_count')
        votes = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'votes')
        rating = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'rating')

        audioFileTags = AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            genre=genre, 
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            votes=votes, 
            rating=rating
        )

        return audioFileTags
     
    def _getTagsForMp3File(self):
        '''
        Returns an AudioFileTags object for the tag values for the Mp3 audio file
        '''

        # Use the EasyId3 interface for getting the standard Mp3 tags
        mutagenInterface = EasyID3(self.audioFilepath)

        title = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'title')
        artist = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'artist')
        album = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'album')
        albumArtist = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'albumartist')
        genre = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'genre')
    
        # Use the normal file interface for getting the nonstandard Mp3 tags
        mutagenInterface = mutagen.File(self.audioFilepath)

        dateAllPlays = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:DATE_ALL_PLAYS')
        dateLastPlayed = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:PLAY_COUNT')
        votes = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:VOTES')
        rating = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:RATING')

        audioFileTags = AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            genre=genre, 
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            votes=votes, 
            rating=rating
        )

        return audioFileTags

    def _getTagsForM4AFile(self):
        '''
        Returns an AudioFileTags object for the tag values for the M4A audio file
        '''

        mutagenInterface = MP4(self.audioFilepath)

        # Standard M4A tags
        title = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9nam')
        artist = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9ART')
        album = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9alb')
        albumArtist = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, 'aART')
        genre = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9gen')

        # Nonstandard (custom) M4A tags
        dateAllPlays = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:DATE_ALL_PLAYS')
        dateLastPlayed = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:PLAY_COUNT')
        votes = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:VOTES')
        rating = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:RATING')

        audioFileTags = AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            genre=genre, 
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            votes=votes, 
            rating=rating
        )

        return audioFileTags

    def _getTagValueFromMutagenInterfaceFLAC(self, mutagenInterface, mutagenKey):
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

    def _getTagValueFromMutagenInterfaceMp3(self, mutagenInterface, mutagenKey):
        try:
            if ('TXXX:' in mutagenKey):
                mutagenValue = mutagenInterface[mutagenKey].text
            else:    
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

    def _getTagValueFromMutagenInterfaceM4A(self, mutagenInterface, mutagenKey):

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

    def _setTagsForFLACFile(self, audioFileTags):
        '''
        Sets the FLAC file's tags to that of the AudioFileTags object given.
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)

        mutagenInterface['title'] = audioFileTags.title
        mutagenInterface['artist'] = audioFileTags.artist
        mutagenInterface['album'] = audioFileTags.album
        mutagenInterface['albumartist'] = audioFileTags.albumArtist
        mutagenInterface['genre'] = audioFileTags.genre
        mutagenInterface['date_all_plays'] = audioFileTags.dateAllPlays
        mutagenInterface['date_last_played'] = audioFileTags.dateLastPlayed
        mutagenInterface['play_count'] = audioFileTags.playCount
        mutagenInterface['votes'] = audioFileTags.votes
        mutagenInterface['rating'] = audioFileTags.rating

        mutagenInterface.save()

    def _setTagsForMp3File(self, audioFileTags):
        '''
        Sets the Mp3 file's tags to that of the AudioFileTags object given.
        '''
        # Use the EasyId3 interface for setting the standard Mp3 tags
        mutagenInterface = EasyID3(self.audioFilepath)

        mutagenInterface['title'] = audioFileTags.title
        mutagenInterface['artist'] = audioFileTags.artist
        mutagenInterface['album'] = audioFileTags.album
        mutagenInterface['albumartist'] = audioFileTags.albumArtist
        mutagenInterface['genre'] = audioFileTags.genre

        mutagenInterface.save()
        
        # Use the ID3 interface for setting the nonstandard Mp3 tags
        mutagenInterface = ID3(self.audioFilepath, v2_version=3)

        mutagenInterface['TXXX:DATE_ALL_PLAYS'] = TXXX(3, desc='DATE_ALL_PLAYS', text=audioFileTags.dateAllPlays)
        mutagenInterface['TXXX:DATE_LAST_PLAYED'] = TXXX(3, desc='DATE_LAST_PLAYED', text=audioFileTags.dateLastPlayed)
        mutagenInterface['TXXX:PLAY_COUNT'] = TXXX(3, desc='PLAY_COUNT', text=audioFileTags.playCount)
        mutagenInterface['TXXX:VOTES'] = TXXX(3, desc='VOTES', text=audioFileTags.votes)
        mutagenInterface['TXXX:RATING'] = TXXX(3, desc='RATING', text=audioFileTags.rating)

        mutagenInterface.save(v2_version=3)


    def _setTagsForM4AFile(self, audioFileTags):
        '''
        Sets the M4A file's tags to that of the AudioFileTags object given.
        '''

        mutagenInterface = MP4(self.audioFilepath)

        # Standard M4A tags
        mutagenInterface['\xa9nam'] = audioFileTags.title
        mutagenInterface['\xa9ART'] = audioFileTags.artist
        mutagenInterface['\xa9alb'] = audioFileTags.album
        mutagenInterface['aART'] = audioFileTags.albumArtist
        mutagenInterface['\xa9gen'] = audioFileTags.genre

        # trackNumber, totalTracks, discNumber, and totalDiscs tags are not supported by MLU for
        # M4A files due to limitations of mutagen

        # Nonstandard (custom) M4A tags
        mutagenInterface['----:com.apple.iTunes:DATE_ALL_PLAYS'] = (audioFileTags.dateAllPlays).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:DATE_LAST_PLAYED'] = (audioFileTags.dateLastPlayed).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:PLAY_COUNT'] = (audioFileTags.playCount).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:VOTES'] = (audioFileTags.votes).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:RATING'] = (audioFileTags.rating).encode('utf-8')

        mutagenInterface.save()