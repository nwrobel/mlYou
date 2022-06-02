'''
mlu.tags.audiofmt.m4a

Module containing class which reads data for a single m4a audio file.
'''

import mutagen
from mutagen.mp4 import MP4

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.convert

from mlu.tags import values

class AudioFormatHandlerM4A:
    def __init__(self, audioFilepath):
        self.audioFilepath = audioFilepath

    def getEmbeddedArtwork(self):
        '''
        '''
        # mutagenInterface = mutagen.File(self.audioFilepath)

        # artworkBinaryData = []
        # try:
        #     picsData = mutagenInterface.tags['covr']
        #     if (isinstance(picsData, list)):
        #         for picData in picsData:
        #             artworkBinaryData.append(bytes(picData))
            
        #     else:
        #         artworkBinaryData.append(bytes(picsData))

        #     return artworkBinaryData

        # except KeyError:
        #     return None
        raise NotImplementedError("Getting album artwork is not implemented yet (this will require use of an external program)")


    def getProperties(self):
        '''
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)

        fileSize = mypycommons.file.getFileSizeBytes(self.audioFilepath)
        fileDateModified = mypycommons.time.formatTimestampForDisplay(mypycommons.file.getFileDateModifiedTimestamp(self.audioFilepath))
        duration = mutagenInterface.info.length
        format = 'M4A'
        codec = mutagenInterface.info.codec_description
        bitRate = mypycommons.convert.bitsToKilobits(mutagenInterface.info.bitrate)
        bitDepth = mutagenInterface.info.bits_per_sample
        numChannels = mutagenInterface.info.channels
        sampleRate = mutagenInterface.info.sample_rate
        replayGain = {
            'albumGain': self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:replaygain_album_gain'),
            'albumPeak': self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:replaygain_album_peak'),
            'trackGain': self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:replaygain_track_gain'),
            'trackPeak': self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:replaygain_track_peak')
        }

        audioProperties = values.AudioFileProperties(
            fileSize=fileSize,
            fileDateModified=fileDateModified,
            duration=duration,
            format=format,
            bitRate=bitRate,
            sampleRate=sampleRate,
            numChannels=numChannels,
            replayGain=replayGain,
            bitDepth=bitDepth,
            encoder='',
            bitRateMode='',
            codec=codec
        )
        return audioProperties


    def getTags(self):
        '''
        Returns an AudioFileTags object for the tag values for the M4A audio file
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)

        # Standard M4A tags
        title = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9nam')
        artist = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9ART')
        album = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9alb')
        albumArtist = self._getTagValueFromMutagenInterface(mutagenInterface, 'aART')
        composer = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9wrt')
        date = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9day')
        genre = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9gen')
        lyrics = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9lyr')
        comment = self._getTagValueFromMutagenInterface(mutagenInterface, '\xa9cmt')
        trackNumOfTotal = self._getTagValueFromMutagenInterface(mutagenInterface, 'trkn')
        discNumOfTotal = self._getTagValueFromMutagenInterface(mutagenInterface, 'disk')

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
        key = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:key')
        bpm = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:BPM')
        dateAdded = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:DATE_ADDED')
        dateAllPlays = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:DATE_ALL_PLAYS')
        dateLastPlayed = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:PLAY_COUNT')
        votes = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:VOTES')
        rating = self._getTagValueFromMutagenInterface(mutagenInterface, '----:com.apple.iTunes:RATING')
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
            '----:com.apple.iTunes:DATE_ADDED', 
            '----:com.apple.iTunes:DATE_ALL_PLAYS', 
            '----:com.apple.iTunes:DATE_LAST_PLAYED',
            '----:com.apple.iTunes:PLAY_COUNT', 
            '----:com.apple.iTunes:VOTES', 
            '----:com.apple.iTunes:RATING'
        ]

        mutagenTagKeys = list(mutagenInterface.keys())
        relevantTagKeys = self._removeUnneededTagKeysFromTagKeysList(mutagenTagKeys)

        otherTagKeys = []
        for tagKey in relevantTagKeys:
            if (tagKey not in tagFieldKeysM4A):
                otherTagKeys.append(tagKey)

        for tagKey in otherTagKeys:
            tagValue = self._getTagValueFromMutagenInterface(mutagenInterface, tagKey)
            tagNameFormatted = self._formatM4AKeyToTagName(tagKey)
            otherTags[tagNameFormatted] = tagValue

        audioFileTags = values.AudioFileTags(
            title=title,
            artist=artist,
            album=album,
            albumArtist=albumArtist,
            composer=composer,
            date=date,
            genre=genre, 
            trackNumber=str(trackNumber),
            totalTracks=str(totalTracks),
            discNumber=str(discNumber),
            totalDiscs=str(totalDiscs),
            bpm=bpm,
            key=key,
            lyrics=lyrics,
            comment=comment,
            dateAdded=dateAdded,
            dateAllPlays=dateAllPlays, 
            dateLastPlayed=dateLastPlayed, 
            playCount=playCount, 
            votes=votes, 
            rating=rating,
            OTHER_TAGS=otherTags
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
        mutagenInterface['----:com.apple.iTunes:DATE_ALL_PLAYS'] = (audioFileTags.dateAllPlays).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:DATE_LAST_PLAYED'] = (audioFileTags.dateLastPlayed).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:PLAY_COUNT'] = (audioFileTags.playCount).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:VOTES'] = (audioFileTags.votes).encode('utf-8')
        mutagenInterface['----:com.apple.iTunes:RATING'] = (audioFileTags.rating).encode('utf-8')

        mutagenInterface.save()

    def _removeUnneededTagKeysFromTagKeysList(self, m4aKeys):
        keysToRemove = [
            'covr',
            '----:com.apple.iTunes:replaygain_album_gain',
            '----:com.apple.iTunes:replaygain_album_peak',
            '----:com.apple.iTunes:replaygain_track_gain',
            '----:com.apple.iTunes:replaygain_track_peak',
            'itunsmpb',
            'itunnorm'
        ]

        for removeKey in keysToRemove:
            try:
                m4aKeys.remove(removeKey)
            except:
                pass

        return m4aKeys

    def _formatM4AKeyToTagName(self, m4aKey):
        if ("----:com.apple.iTunes:" in m4aKey):
            tagName = m4aKey[22:]
        else:
            tagName = m4aKey

        return tagName.lower()

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

    def setCustomTag(self, tagName, value):
        mutagenInterface = MP4(self.audioFilepath)

        tagName = tagName.upper()
        tagKey = "----:com.apple.iTunes:{}".format(tagName)
        mutagenInterface[tagKey] = (value).encode('utf-8')

        mutagenInterface.save()