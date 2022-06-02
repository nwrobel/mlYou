'''
mlu.tags.audiofmt.mp3

Module containing class which reads data for a single mp3 audio file.
'''

import mutagen
from mutagen.mp3 import BitrateMode
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.convert

from mlu.tags import values

class AudioFormatHandlerMP3:
    def __init__(self, audioFilepath):
        self.audioFilepath = audioFilepath

    def getEmbeddedArtwork(self):
        # mutagenInterface = mutagen.File(self.audioFilepath)

        # pictureTags = []
        # mutagenTagKeys = list(mutagenInterface.keys())

        # for tagKey in mutagenTagKeys:
        #     if ("APIC:" in tagKey):
        #         pictureTags.append(tagKey)

        # if (pictureTags):
        #     artworksBinaryData = []
        #     for picTag in pictureTags:
        #         picData = mutagenInterface[picTag].data
        #         artworksBinaryData.append(picData)
                
        #     return artworksBinaryData

        # else:
        #     return None
        raise NotImplementedError("Getting album artwork is not implemented yet (this will require use of an external program)")


    def getProperties(self):
        mutagenInterface = mutagen.File(self.audioFilepath)

        fileSize = mypycommons.file.getFileSizeBytes(self.audioFilepath)
        fileDateModified = mypycommons.time.formatTimestampForDisplay(mypycommons.file.getFileDateModifiedTimestamp(self.audioFilepath))
        duration = mutagenInterface.info.length
        format = 'MP3'

        bitRateModeType = mutagenInterface.info.bitrate_mode
        if (bitRateModeType == BitrateMode.CBR):
            bitRateMode = 'CBR'
        elif (bitRateModeType == BitrateMode.VBR):
            bitRateMode = 'VBR'
        elif (bitRateModeType == BitrateMode.ABR):
            bitRateMode = 'ABR'
        else:
            bitRateMode = ''

        encoder = "{} ({})".format(mutagenInterface.info.encoder_info, mutagenInterface.info.encoder_settings)
        bitRate = mypycommons.convert.bitsToKilobits(mutagenInterface.info.bitrate)
        numChannels = mutagenInterface.info.channels
        sampleRate = mutagenInterface.info.sample_rate
        replayGain = {
            'albumGain': self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:replaygain_album_gain'),
            'albumPeak': self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:replaygain_album_peak'),
            'trackGain': self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:replaygain_track_gain'),
            'trackPeak': self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:replaygain_track_peak')
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
            bitDepth='',
            encoder=encoder,
            bitRateMode=bitRateMode,
            codec=''
        )
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
        bpm = self._getTagValueFromMutagenInterface(mutagenInterface, 'TBPM')
        date = self._getTagValueFromMutagenInterface(mutagenInterface, 'TDRC')

        trackNumOfTotal = self._getTagValueFromMutagenInterface(mutagenInterface, 'TRCK')
        discNumOfTotal = self._getTagValueFromMutagenInterface(mutagenInterface, 'TPOS')

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

        composer = self._getTagValueFromMutagenInterface(mutagenInterface, 'TCOM')
        key = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:Key')
        lyrics = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:LYRICS')
        comment = self._getTagValueFromMutagenInterface(mutagenInterface, 'COMM::eng')
        dateAdded = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:DATE_ADDED')
        dateAllPlays = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:DATE_ALL_PLAYS')
        dateLastPlayed = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:DATE_LAST_PLAYED') 
        playCount = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:PLAY_COUNT')
        votes = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:VOTES')
        rating = self._getTagValueFromMutagenInterface(mutagenInterface, 'TXXX:RATING')
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
            'COMM::eng', 
            'TXXX:DATE_ADDED', 
            'TXXX:DATE_ALL_PLAYS', 
            'TXXX:DATE_LAST_PLAYED',
            'TXXX:PLAY_COUNT', 
            'TXXX:VOTES', 
            'TXXX:RATING'
        ]

        mutagenTagKeys = list(mutagenInterface.keys())
        relevantTagKeys = self._removeUnneededTagKeysFromTagKeysList(mutagenTagKeys)

        otherTagKeys = []
        for tagKey in relevantTagKeys:
            if (tagKey not in tagFieldKeysMp3):
                otherTagKeys.append(tagKey)

        for tagKey in otherTagKeys:
            tagValue = self._getTagValueFromMutagenInterface(mutagenInterface, tagKey)
            tagNameFormatted = self._formatMp3KeyToTagName(tagKey)
            otherTags[tagNameFormatted] = tagValue

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

        mutagenInterface['TXXX:DATE_ALL_PLAYS'] = TXXX(3, desc='DATE_ALL_PLAYS', text=audioFileTags.dateAllPlays)
        mutagenInterface['TXXX:DATE_LAST_PLAYED'] = TXXX(3, desc='DATE_LAST_PLAYED', text=audioFileTags.dateLastPlayed)
        mutagenInterface['TXXX:PLAY_COUNT'] = TXXX(3, desc='PLAY_COUNT', text=audioFileTags.playCount)
        mutagenInterface['TXXX:VOTES'] = TXXX(3, desc='VOTES', text=audioFileTags.votes)
        mutagenInterface['TXXX:RATING'] = TXXX(3, desc='RATING', text=audioFileTags.rating)

        mutagenInterface.save(v2_version=3)

    def _removeUnneededTagKeysFromTagKeysList(self, mp3TagKeys):
        keysToRemove = [
            'COMM:ID3v1 Comment:eng',
            'TXXX:replaygain_album_gain',
            'TXXX:replaygain_album_peak',
            'TXXX:replaygain_track_gain',
            'TXXX:replaygain_track_peak'
        ]

        for removeKey in keysToRemove:
            try:
                mp3TagKeys.remove(removeKey)
            except:
                pass
        
        # Also remove the 'APIC:' tag, which could be named like 'APIC:xxxxx'
        relevantKeys = []
        for tagKey in mp3TagKeys:
            if ("APIC:" not in tagKey):
                relevantKeys.append(tagKey)

        return relevantKeys

    def _formatMp3KeyToTagName(self, mp3Key):
        if ("TXXX:" in mp3Key):
            tagName = mp3Key[5:]
        else:
            tagName = mp3Key

        return tagName.lower()

    def _getTagValueFromMutagenInterface(self, mutagenInterface, mutagenKey):
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

        return str(tagValue) 

    def setCustomTag(self, tagName, value):
        mutagenInterface = ID3(self.audioFilepath, v2_version=3)

        tagName = tagName.upper()
        tagKey = "TXXX:{}".format(tagName)

        mutagenInterface[tagKey] = TXXX(3, desc=tagName, text=value)

        mutagenInterface.save(v2_version=3)