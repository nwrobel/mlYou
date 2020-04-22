'''
mlu.tags.io
'''

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX
from mutagen.mp4 import MP4

import mlu.common.file

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
        date, 
        genre, 
        trackNumber,
        totalTracks, 
        discNumber, 
        totalDiscs, 
        lyrics, 
        bpm, 
        isCompilation, 
        dateAdded, 
        dateFileCreated, 
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
        self.date = date
        self.genre = genre
        self.trackNumber = trackNumber
        self.totalTracks = totalTracks
        self.discNumber = discNumber
        self.totalDiscs = totalDiscs
        self.lyrics = lyrics
        self.bpm = bpm
        self.isCompilation = isCompilation
        self.dateAdded = dateAdded
        self.dateFileCreated = dateFileCreated
        self.dateAllPlays = dateAllPlays
        self.playCount = playCount
        self.votes = votes
        self.rating = rating


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

        # Strip the dot from the file extension to get the audio file type, used by this class
        self._audioFileType = mlu.common.file.GetFileExtension(self.audioFilepath).replace('.', '')

        # Check that the given audio file type is supported
        SUPPORTED_AUDIO_TYPES = ['flac', 'mp3', 'm4a']
        if (self._audioFileType not in SUPPORTED_AUDIO_TYPES):
            raise Exception("Cannot open file '{}': Audio file format is not supported".format(self.audioFilepath))

        self._tags = None

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

    def setTags(self):
        '''
        Sets the tags on this audio file to those represented by the given AudioFileTags object.
        This method performs a write operation on the audio file to write the given tag values each
        time. 
        
        Validation is performed on each tag value and an AudioFileTagsValidationError will be thrown
        if any tag values are invalid.
        '''

        pass

    def _getTagsForFLACFile(self):
        '''
        Returns an AudioFileTags object for the tag values for the FLAC audio file
        '''

        mutagenInterface = mutagen.File(self.audioFilepath)

        title = self._getTagValueFromMutagenInterface(mutagenInterface, 'title')
        artist = self._getTagValueFromMutagenInterface(mutagenInterface, 'artist')
        album = self._getTagValueFromMutagenInterface(mutagenInterface, 'album')
        albumArtist = self._getTagValueFromMutagenInterface(mutagenInterface, 'albumartist')
        date = self._getTagValueFromMutagenInterface(mutagenInterface, 'date')
        genre = self._getTagValueFromMutagenInterface(mutagenInterface, 'genre')
        trackNumber = self._getTagValueFromMutagenInterface(mutagenInterface, 'tracknumber')
        totalTracks = self._getTagValueFromMutagenInterface(mutagenInterface, 'tracktotal')
        discNumber = self._getTagValueFromMutagenInterface(mutagenInterface, 'discnumber')
        totalDiscs = self._getTagValueFromMutagenInterface(mutagenInterface, 'disctotal')
        lyrics = self._getTagValueFromMutagenInterface(mutagenInterface, 'lyrics')
        bpm = self._getTagValueFromMutagenInterface(mutagenInterface, 'bpm')
        isCompilation = self._getTagValueFromMutagenInterface(mutagenInterface, 'is_compilation')
        dateAdded = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_added')
        dateFileCreated = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_file_created') 
        dateAllPlays = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_all_plays')
        dateLastPlayed = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_last_played') 
        playCount = self._getTagValueFromMutagenInterface(mutagenInterface, 'play_count')
        votes = self._getTagValueFromMutagenInterface(mutagenInterface, 'votes')
        rating = self._getTagValueFromMutagenInterface(mutagenInterface, 'rating')

        audioFileTags = AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            date=date, 
            genre=genre, 
            trackNumber=trackNumber,
            totalTracks=totalTracks, 
            discNumber=discNumber, 
            totalDiscs=totalDiscs, 
            lyrics=lyrics, 
            bpm=bpm, 
            isCompilation=isCompilation, 
            dateAdded=dateAdded, 
            dateFileCreated=dateFileCreated, 
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

        pass

    def _getTagsForM4AFile(self):
        '''
        Returns an AudioFileTags object for the tag values for the M4A audio file
        '''

        pass

    def _getTagValueFromMutagenInterface(self, mutagenInterface, mutagenKey):
        try:
            mutagenValue = mutagenInterface[mutagenKey]

            if (len(mutagenValue) == 1):
                tagValue = mutagenValue[0]
            elif (len(mutagenValue) > 1):
                tagValue = mutagenValue
            else:
                tagValue = None

        except KeyError:
            tagValue = None

        return tagValue  