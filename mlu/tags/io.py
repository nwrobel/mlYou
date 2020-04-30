'''
mlu.tags.io
'''

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX
from mutagen.mp4 import MP4

import mlu.common.file
import mlu.tags.validation

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
        self.dateAdded = dateAdded
        self.dateFileCreated = dateFileCreated
        self.dateAllPlays = dateAllPlays
        self.dateLastPlayed = dateLastPlayed
        self.playCount = playCount
        self.votes = votes
        self.rating = rating

    def validate(self):
        mlu.tags.validation.validateAudioFileTags(self)


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

        # TODO: perform validation here

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
        date = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date')
        genre = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'genre')
        trackNumber = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'tracknumber')
        totalTracks = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'tracktotal')
        discNumber = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'discnumber')
        totalDiscs = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'disctotal')
        lyrics = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'lyrics')
        bpm = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'bpm')
        dateAdded = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date_added')
        dateFileCreated = self._getTagValueFromMutagenInterfaceFLAC(mutagenInterface, 'date_file_created') 
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
            date=date, 
            genre=genre, 
            trackNumber=trackNumber,
            totalTracks=totalTracks, 
            discNumber=discNumber, 
            totalDiscs=totalDiscs, 
            lyrics=lyrics, 
            bpm=bpm, 
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

        # Use the EasyId3 interface for getting the standard Mp3 tags
        mutagenInterface = EasyID3(self.audioFilepath)

        title = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'title')
        artist = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'artist')
        album = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'album')
        albumArtist = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'albumartist')
        date = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'date')
        genre = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'genre')
        bpm = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'bpm')

        # Extra work needed to unpack track/disc number/total tags
        trackNumberOverTotal = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'tracknumber')
        discNumberOverTotal = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'discnumber')

        if ('/' in trackNumberOverTotal):
            trackNumber = trackNumberOverTotal.split('/')[0]
            totalTracks = trackNumberOverTotal.split('/')[1]
        elif (trackNumberOverTotal):
            trackNumber = trackNumberOverTotal
            totalTracks = ''
        else:
            trackNumber = ''
            totalTracks = ''

        if ('/' in discNumberOverTotal):
            discNumber = discNumberOverTotal.split('/')[0]
            totalDiscs = discNumberOverTotal.split('/')[1]
        elif (discNumberOverTotal):
            discNumber = discNumberOverTotal
            totalDiscs = ''
        else:
            discNumber = ''
            totalDiscs = ''
        
        # Use the normal file interface for getting the nonstandard Mp3 tags
        mutagenInterface = mutagen.File(self.audioFilepath)

        # These TXXX tags will be set if tracknumber is not set but totaltracks is, or if discnumber
        # is not set and totaldiscs is
        if (not totalTracks):
            totalTracks = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:TOTALTRACKS')
        if (not totalDiscs):
            totalDiscs = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:TOTALDISCS')

        lyrics = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:LYRICS')
        dateAdded = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:DATE_ADDED')
        dateFileCreated = self._getTagValueFromMutagenInterfaceMp3(mutagenInterface, 'TXXX:DATE_FILE_CREATED') 
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
            date=date, 
            genre=genre, 
            trackNumber=trackNumber,
            totalTracks=totalTracks, 
            discNumber=discNumber, 
            totalDiscs=totalDiscs, 
            lyrics=lyrics, 
            bpm=bpm, 
            dateAdded=dateAdded, 
            dateFileCreated=dateFileCreated, 
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
        date = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9day')
        genre = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9gen')
        lyrics = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '\xa9lyr')

        # Extra work needed to unpack the track and disc number/total, which are tuple data
        trackNumberTotal = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, 'trkn')
        discNumberTotal = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, 'disk')

        if (trackNumberTotal):
            if (trackNumberTotal[0] == 0):
                trackNumber = ''
            else: 
                trackNumber = str(trackNumberTotal[0])

            if (trackNumberTotal[1] == 0):
                totalTracks = ''
            else: 
                totalTracks = str(trackNumberTotal[1]) 

        else:
            print("WARNING: M4A tag 'trkn' not found, the value returned for TOTALTRACKS tag could possibly be incorrectly empty")
            trackNumber = ''
            totalTracks = ''

        if (discNumberTotal):
            if (discNumberTotal[0] == 0):
                discNumber = ''
            else: 
                discNumber = str(discNumberTotal[0]) 

            if (discNumberTotal[1] == 0):
                totalDiscs = ''
            else: 
                totalDiscs = str(discNumberTotal[1]) 

        else:
            print("WARNING: M4A tag 'disk' not found, the value returned for TOTALDISCS tag could possibly be incorrectly empty")
            discNumber = ''
            totalDiscs = ''       

        # Nonstandard (custom) M4A tags
        bpm = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:BPM')
        dateAdded = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:DATE_ADDED')
        dateFileCreated = self._getTagValueFromMutagenInterfaceM4A(mutagenInterface, '----:com.apple.iTunes:DATE_FILE_CREATED') 
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
            date=date, 
            genre=genre, 
            trackNumber=trackNumber,
            totalTracks=totalTracks, 
            discNumber=discNumber, 
            totalDiscs=totalDiscs, 
            lyrics=lyrics, 
            bpm=bpm, 
            dateAdded=dateAdded, 
            dateFileCreated=dateFileCreated, 
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
        mutagenInterface['date'] = audioFileTags.date
        mutagenInterface['genre'] = audioFileTags.genre
        mutagenInterface['tracknumber'] = audioFileTags.trackNumber
        mutagenInterface['tracktotal'] = audioFileTags.totalTracks
        mutagenInterface['discnumber'] = audioFileTags.discNumber
        mutagenInterface['disctotal'] = audioFileTags.totalDiscs
        mutagenInterface['lyrics'] = audioFileTags.lyrics
        mutagenInterface['bpm'] = audioFileTags.bpm
        mutagenInterface['date_added'] = audioFileTags.dateAdded
        mutagenInterface['date_file_created'] = audioFileTags.dateFileCreated
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
        mutagenInterface['date'] = audioFileTags.date
        mutagenInterface['genre'] = audioFileTags.genre
        mutagenInterface['bpm'] = audioFileTags.bpm

        # Extra work required to set the track/disc number/total tag values
        if (audioFileTags.trackNumber):
            trackNumberOverTotal = "{}/{}".format(audioFileTags.trackNumber, audioFileTags.totalTracks)
        else:
            trackNumberOverTotal = ''

        if (audioFileTags.discNumber):
            discNumberOverTotal = "{}/{}".format(audioFileTags.discNumber, audioFileTags.totalDiscs)
        else:
            discNumberOverTotal = ''

        mutagenInterface['tracknumber'] = trackNumberOverTotal
        mutagenInterface['discnumber'] = discNumberOverTotal

        mutagenInterface.save()
        
        # Use the ID3 interface for setting the nonstandard Mp3 tags
        mutagenInterface = ID3(self.audioFilepath, v2_version=3)

        mutagenInterface['TXXX:LYRICS'] = TXXX(3, desc='LYRICS', text=audioFileTags.lyrics)
        mutagenInterface['TXXX:DATE_ADDED'] = TXXX(3, desc='DATE_ADDED', text=audioFileTags.dateAdded)
        mutagenInterface['TXXX:DATE_FILE_CREATED'] = TXXX(3, desc='DATE_FILE_CREATED', text=audioFileTags.dateFileCreated)
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
        mutagenInterface['\xa9day'] = audioFileTags.date
        mutagenInterface['\xa9gen'] = audioFileTags.genre
        mutagenInterface['\xa9lyr'] = audioFileTags.lyrics

        # Extra work needed to save the track and disc number/total, which are tuple data
        mutagenInterface['trkn'][0] = (int(audioFileTags.trackNumber), int(audioFileTags.totalTracks))
        mutagenInterface['disk'][0] = (int(audioFileTags.discNumber), int(audioFileTags.totalDiscs))

        # Nonstandard (custom) M4A tags
        mutagenInterface['----:com.apple.iTunes:BPM'] = (audioFileTags.bpm).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:DATE_ADDED'] = (audioFileTags.dateAdded).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:DATE_FILE_CREATED'] = (audioFileTags.dateFileCreated).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:DATE_ALL_PLAYS'] = (audioFileTags.dateAllPlays).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:DATE_LAST_PLAYED'] = (audioFileTags.dateLastPlayed).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:PLAY_COUNT'] = (audioFileTags.playCount).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:VOTES'] = (audioFileTags.votes).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:RATING'] = (audioFileTags.rating).encode('utf-8')

        mutagenInterface.save()