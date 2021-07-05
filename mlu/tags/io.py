'''
mlu.tags.io

This module deals with reading tag values from and writing tag values to an audio file. Contains
the AudioFileTags object class and the AudioFileTagsIOHandler class definitions.

Supports tag IO for FLAC, Mp3, and M4A audio file types. Only gets/sets tags that are supported by
the MLU project. These supported tags are the properties of the AudioFileTags object.
'''

# TODO: set up validation of tag values using the mlu.tags.validation module

import mutagen
import logging
from mutagen import mp3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX
from mutagen.mp4 import MP4

from com.nwrobel import mypycommons
#import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file

logger = logging.getLogger("mluGlobalLogger")

SUPPORTED_AUDIO_TYPES = ['flac', 'mp3', 'm4a']

# def getAudioFileDurationAsTimestamp(audioFilepath):
#     mutagenInterface = mutagen.File(audioFilepath)
#     durationSeconds = mutagenInterface.info.length
#     durationTimestamp = mypycommons.time.convertSecondsToTimestamp(durationSeconds)

#     return durationTimestamp

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
        composer,
        date,
        genre,
        trackNumber,
        totalTracks,
        discNumber,
        totalDiscs,
        bpm,
        key,
        lyrics,
        isCompilation,
        comment,
        dateAdded,
        dateFileCreated,
        dateAllPlays, 
        dateLastPlayed, 
        playCount, 
        votes, 
        rating,
        OTHER_TAGS
    ):
        self.title = title
        self.artist = artist
        self.album = album
        self.albumArtist = albumArtist
        self.composer = composer
        self.date = date
        self.genre = genre
        self.trackNumber = trackNumber
        self.totalTracks = totalTracks
        self.discNumber = discNumber
        self.totalDiscs = totalDiscs
        self.bpm = bpm
        self.key = key
        self.lyrics = lyrics
        self.isCompilation = isCompilation
        self.comment = comment
        self.dateAdded = dateAdded
        self.dateFileCreated = dateFileCreated
        self.dateAllPlays = dateAllPlays
        self.dateLastPlayed = dateLastPlayed
        self.playCount = playCount
        self.votes = votes
        self.rating = rating
        self.OTHER_TAGS = OTHER_TAGS

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

class AudioFileProperties:
    def __init__(
        self,
        fileSize,
        fileDateModified,
        duration,
        format,
        encoding,
        bitRate,
        sampleRate,
        bitDepth,
        numChannels,
        encodingTool,
        replayGain
    ):
        self.fileSize = fileSize
        self.fileDateModified = fileDateModified
        self.duration = duration
        self.format = format
        self.encoding = encoding
        self.bitRate = bitRate
        self.sampleRate = sampleRate
        self.bitDepth = bitDepth
        self.numChannels = numChannels
        self.encodingTool = encodingTool
        self.replayGain = replayGain

class AudioFileMetadataHandler:
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
        if (not mypycommons.file.isFile(audioFilepath)):
            raise ValueError("Class attribute 'audioFilepath' must be a valid filepath to an existing file: invalid value '{}'".format(audioFilepath))

        self.audioFilepath = audioFilepath

        # Strip the dot from the file extension to get the audio file type, used by this class
        self._audioFileType = mypycommons.file.getFileExtension(self.audioFilepath).replace('.', '')

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

    def getProperties(self):
        pass

    def getEmbeddedArtwork(self):
        if (self._audioFileType == 'flac'):
            artworksData = self._getEmbeddedArtworkForFLACFile()

        elif (self._audioFileType == 'mp3'):
            artworksData = self._getEmbeddedArtworkForMp3File()

        elif (self._audioFileType == 'm4a'):
            artworksData = self._getEmbeddedArtworkForM4AFile()

        return artworksData

    def _getEmbeddedArtworkForFLACFile(self):
        mutagenInterface = mutagen.File(self.audioFilepath)

        artworksData = []
        for picture in mutagenInterface.pictures:
            artworksData.append(picture.data)
        
        return artworksData 

    def _getEmbeddedArtworkForMp3File(self):
        mutagenInterface = mutagen.File(self.audioFilepath)

        artworksData = []
        pictureTags = []
        mutagenTagKeys = list(mutagenInterface.keys())

        for tagKey in mutagenTagKeys:
            if ("APIC:" in tagKey):
                pictureTags.append(tagKey)

        for picTag in pictureTags:
            picData = mutagenInterface[picTag].data
            artworksData.append(picData)

        return artworksData

    def _getEmbeddedArtworkForM4AFile(self):
        mutagenInterface = MP4(self.audioFilepath)
        
        artworkData = []
        try:
            picsData = mutagenInterface.tags['covr']
            if (isinstance(picsData, list)):
                for picData in picsData:
                    artworkData.append(bytes(picData))
            
            else:
                artworkData.append(bytes(picsData))

            return artworkData

        except:
            return []

    def _getTagsForFLACFile(self):
        '''
        Returns an AudioFileTags object for the tag values for the FLAC audio file
        '''

        mutagenInterface = mutagen.File(self.audioFilepath)

        title = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'title')
        artist = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'artist')
        album = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'album')
        albumArtist = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'albumartist')
        composer = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'composer')
        date = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date')
        genre = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'genre')
        trackNumber = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'tracknumber')
        totalTracks = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'tracktotal')
        discNumber = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'discnumber')
        totalDiscs = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'disctotal')
        bpm = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'bpm')
        key = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'key')
        lyrics = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'lyrics')
        isCompilation = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'is_compilation')
        comment = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'comment')
        dateAdded = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date_added')
        dateFileCreated = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date_file_created')
        dateAllPlays = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date_all_plays')
        dateLastPlayed = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date_last_played') 
        playCount = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'play_count')
        votes = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'votes')
        rating = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'rating')
        otherTags = {}

        tagFieldKeysFlac = [
            'title', 
            'artist', 
            'album', 
            'albumartist', 
            'composer', 
            'date', 
            'genre', 
            'tracknumber', 
            'tracktotal', 
            'discnumber', 
            'disctotal', 
            'bpm', 
            'key', 
            'lyrics', 
            'is_compilation', 
            'comment', 
            'date_added', 
            'date_file_created', 
            'date_all_plays', 
            'date_last_played',
            'play_count',
            'votes', 
            'rating'
        ]

        mutagenTagKeys = mutagenInterface.tags.keys()
        otherTagNames = []
        for tagKey in mutagenTagKeys:
            if (key.lower() not in tagFieldKeysFlac):
                otherTagNames.append(tagKey)

        for tagNameKey in otherTagNames:
            tagValue = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, tagNameKey)
            otherTags[tagNameKey] = tagValue

        audioFileTags = AudioFileTags(
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
            lyrics=lyrics,
            isCompilation=isCompilation,
            comment=comment,
            dateAdded=dateAdded,
            dateFileCreated=dateFileCreated,
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            votes=votes, 
            rating=rating,
            OTHER_TAGS=otherTags
        )

        return audioFileTags
     
    def _getTagsForMp3File(self):
        '''
        Returns an AudioFileTags object for the tag values for the Mp3 audio file
        '''
        # Use the normal file interface for getting the nonstandard Mp3 tags
        mutagenInterface = mutagen.File(self.audioFilepath)

        title = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TIT2')
        artist = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TPE1')
        album = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TALB')
        albumArtist = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TPE2')
        genre = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TCON')
        bpm = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TBPM')
        date = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TDRC')

        trackNumOfTotal = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TRCK')
        discNumOfTotal = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TPOS')

        if ('/' in trackNumOfTotal):
            parts = trackNumOfTotal.split('/')
            trackNumber = parts[0]
            totalTracks = parts[1]
        else:
            trackNumber = trackNumOfTotal
            totalTracks = ''

        if ('/' in discNumOfTotal):
            parts = discNumOfTotal.split('/')
            discNumber = parts[0]
            totalDiscs = parts[1]
        else:
            discNumber = discNumOfTotal
            totalDiscs = ''

        composer = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TCOM')
        key = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:Key')
        lyrics = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:LYRICS')
        isCompilation = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:IS_COMPILATION')
        comment = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'COMM::eng')
        dateAdded = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:DATE_ADDED')
        dateFileCreated = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:DATE_FILE_CREATED')
        dateAllPlays = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:DATE_ALL_PLAYS')
        dateLastPlayed = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:PLAY_COUNT')
        votes = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:VOTES')
        rating = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:RATING')
        otherTags = {}

        tagFieldKeysMp3 = [
            'TIT2', 
            'TPE1', 
            'TALB', 
            'TPE2', 
            'TCOM', 
            'TDRC', 
            'TCON', 
            'TRCK', 
            'TPOS',
            'TBPM', 
            'TXXX:Key', 
            'TXXX:LYRICS', 
            'TXXX:IS_COMPILATION', 
            'COMM::eng', 
            'TXXX:DATE_ADDED', 
            'TXXX:DATE_FILE_CREATED', 
            'TXXX:DATE_ALL_PLAYS', 
            'TXXX:DATE_LAST_PLAYED',
            'TXXX:PLAY_COUNT', 
            'TXXX:VOTES', 
            'TXXX:RATING'
        ]

        mutagenTagKeys = list(mutagenInterface.keys())
        relevantTagKeys = self._removeUnneededTagKeysFromMp3TagKeysList(mutagenTagKeys)

        otherTagKeys = []
        for tagKey in relevantTagKeys:
            if (tagKey not in tagFieldKeysMp3):
                otherTagKeys.append(tagKey)

        for tagKey in otherTagKeys:
            tagValue = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, tagKey)
            tagNameFormatted = self._formatMp3KeyToTagName(tagKey)
            otherTags[tagNameFormatted] = tagValue

        audioFileTags = AudioFileTags(
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
            lyrics=lyrics,
            isCompilation=isCompilation,
            comment=comment,
            dateAdded=dateAdded,
            dateFileCreated=dateFileCreated,
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            votes=votes, 
            rating=rating,
            OTHER_TAGS=otherTags
        )

        return audioFileTags

    def _removeUnneededTagKeysFromMp3TagKeysList(self, mp3TagKeys):
        ignoreKeysMp3 = [
            'COMM:ID3v1 Comment:eng'
        ]

        relevantKeys = []
        for tagKey in mp3TagKeys:
            if ("APIC:" not in tagKey):
                relevantKeys.append(tagKey)

        for ignoreKey in ignoreKeysMp3:
            relevantKeys.remove(ignoreKey)

        return relevantKeys

    def _formatMp3KeyToTagName(self, mp3Key):
        if ("TXXX:" in mp3Key):
            tagName = mp3Key[5:]
        else:
            tagName = mp3Key

        return tagName

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
        composer = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, '\xa9wrt')
        date = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, '\xa9day')
        genre = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9gen')
        lyrics = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9lyr')
        comment = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9cmt')
        trackNumOfTotal = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, 'trkn')
        discNumOfTotal = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, 'disk')

        if (isinstance(trackNumOfTotal, tuple)):
            trackNumber = trackNumOfTotal[0]
            totalTracks = trackNumOfTotal[1]
            if (trackNumber == 0):
                trackNumber = ''
            if (totalTracks == 0):
                totalTracks = ''
        else:
            trackNumber = ''
            totalTracks = ''

        if (isinstance(discNumOfTotal, tuple)):
            discNumber = discNumOfTotal[0]
            totalDiscs = discNumOfTotal[1]
            if (discNumber == 0):
                discNumber = ''
            if (totalDiscs == 0):
                totalDiscs = ''
        else:
            discNumber = ''
            totalDiscs = ''
        

        # Nonstandard (custom) M4A tags
        key = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:key')
        bpm = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:BPM')
        isCompilation = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:IS_COMPILATION')
        dateAdded = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:DATE_ADDED')
        dateFileCreated = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:DATE_FILE_CREATED')
        dateAllPlays = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:DATE_ALL_PLAYS')
        dateLastPlayed = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:PLAY_COUNT')
        votes = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:VOTES')
        rating = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:RATING')
        otherTags = {}

        tagFieldKeysM4A = [
            '\xa9nam', 
            '\xa9ART',
            '\xa9alb', 
            'aART', 
            '\xa9wrt', 
            '\xa9day', 
            '\xa9gen', 
            '\xa9lyr', 
            '\xa9cmt',
            'trkn', 
            'disk', 
            '----:com.apple.iTunes:key', 
            '----:com.apple.iTunes:BPM', 
            '----:com.apple.iTunes:IS_COMPILATION', 
            '----:com.apple.iTunes:DATE_ADDED', 
            '----:com.apple.iTunes:DATE_FILE_CREATED', 
            '----:com.apple.iTunes:DATE_ALL_PLAYS', 
            '----:com.apple.iTunes:DATE_LAST_PLAYED',
            '----:com.apple.iTunes:PLAY_COUNT', 
            '----:com.apple.iTunes:VOTES', 
            '----:com.apple.iTunes:RATING'
        ]

        mutagenTagKeys = list(mutagenInterface.keys())
        relevantTagKeys = self._removeUnneededTagKeysFromM4ATagKeysList(mutagenTagKeys)

        otherTagKeys = []
        for tagKey in relevantTagKeys:
            if (tagKey not in tagFieldKeysM4A):
                otherTagKeys.append(tagKey)

        for tagKey in otherTagKeys:
            tagValue = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, tagKey)
            tagNameFormatted = self._formatM4AKeyToTagName(tagKey)
            otherTags[tagNameFormatted] = tagValue

        audioFileTags = AudioFileTags(
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
            lyrics=lyrics,
            isCompilation=isCompilation,
            comment=comment,
            dateAdded=dateAdded,
            dateFileCreated=dateFileCreated,
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            votes=votes, 
            rating=rating,
            OTHER_TAGS=otherTags
        )
        return audioFileTags

    def _removeUnneededTagKeysFromM4ATagKeysList(self, m4aKeys):
        try:
            m4aKeys.remove('covr')
        except:
            pass

        return m4aKeys

    def _formatM4AKeyToTagName(self, m4aKey):
        if ("----:com.apple.iTunes:" in m4aKey):
            tagName = m4aKey[22:]
        else:
            tagName = m4aKey

        return tagName

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
            mutagenValue = mutagenInterface[mutagenKey].text

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