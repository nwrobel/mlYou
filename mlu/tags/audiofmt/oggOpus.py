'''
mlu.tags.audiofmt.oggOpus

Module containing class which reads data for a single ogg OPUS audio file.
'''

import mutagen

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.convert

from mlu.tags import values

class AudioFormatHandlerOggOpus:
    def __init__(self, audioFilepath):
        self.audioFilepath = audioFilepath

    def getEmbeddedArtwork(self):
        '''
        '''
        # mutagenInterface = mutagen.File(self.audioFilepath)

        # try:
        #     picturesStrList = mutagenInterface['metadata_block_picture']
        # except KeyError:
        #     picturesStrList = None

        # artworksBinaryData = []
        # if (picturesStrList):
        #     for pictureStr in picturesStrList:
        #         artworksBinaryData.append(pictureStr.encode('utf-8'))
        #     return artworksBinaryData

        # else:
        #     return None
        raise NotImplementedError("Getting album artwork is not implemented yet (this will require use of an external program)")

    def getProperties(self):
        '''
        '''
        mutagenInterface = mutagen.File(self.audioFilepath)

        fileSize = mypycommons.file.getFileSizeBytes(self.audioFilepath)
        fileDateModified = mypycommons.time.formatTimestampForDisplay(mypycommons.file.getFileDateModifiedTimestamp(self.audioFilepath))
        duration = mutagenInterface.info.length
        format = 'OGG Opus'
        #bitRate = mypycommons.convert.bitsToKilobits(mutagenInterface.info.bitrate)
        #bitDepth = mutagenInterface.info.bits_per_sample
        numChannels = mutagenInterface.info.channels
        #sampleRate = mutagenInterface.info.sample_rate
        # replayGain = {
        #     'albumGain': self._getTagValueFromMutagenInterface(mutagenInterface, 'replaygain_album_gain'),
        #     'albumPeak': self._getTagValueFromMutagenInterface(mutagenInterface, 'replaygain_album_peak'),
        #     'trackGain': self._getTagValueFromMutagenInterface(mutagenInterface, 'replaygain_track_gain'),
        #     'trackPeak': self._getTagValueFromMutagenInterface(mutagenInterface, 'replaygain_track_peak')
        # }

        audioProperties = values.AudioFileProperties(
            fileSize=fileSize,
            fileDateModified=fileDateModified,
            duration=duration,
            format=format,
            bitRate=None,
            sampleRate=None,
            numChannels=numChannels,
            replayGain=None,
            bitDepth=None,
            encoder=None,
            bitRateMode=None,
            codec=None
        )
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
        composer = self._getTagValueFromMutagenInterface(mutagenInterface, 'composer')
        date = self._getTagValueFromMutagenInterface(mutagenInterface, 'date')
        genre = self._getTagValueFromMutagenInterface(mutagenInterface, 'genre')
        trackNumber = self._getTagValueFromMutagenInterface(mutagenInterface, 'tracknumber')
        totalTracks = self._getTagValueFromMutagenInterface(mutagenInterface, 'tracktotal')
        discNumber = self._getTagValueFromMutagenInterface(mutagenInterface, 'discnumber')
        totalDiscs = self._getTagValueFromMutagenInterface(mutagenInterface, 'disctotal')
        bpm = self._getTagValueFromMutagenInterface(mutagenInterface, 'bpm')
        key = self._getTagValueFromMutagenInterface(mutagenInterface, 'key')
        lyrics = self._getTagValueFromMutagenInterface(mutagenInterface, 'lyrics')
        comment = self._getTagValueFromMutagenInterface(mutagenInterface, 'comment')
        dateAdded = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_added')
        dateAllPlays = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_all_plays')
        dateLastPlayed = self._getTagValueFromMutagenInterface(mutagenInterface, 'date_last_played') 
        playCount = self._getTagValueFromMutagenInterface(mutagenInterface, 'play_count')
        votes = self._getTagValueFromMutagenInterface(mutagenInterface, 'votes')
        rating = self._getTagValueFromMutagenInterface(mutagenInterface, 'rating')
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
            'comment', 
            'date_added', 
            'date_all_plays', 
            'date_last_played',
            'play_count',
            'votes', 
            'rating'
        ]

        mutagenTagKeys = mutagenInterface.tags.keys()
        relevantTagKeys = self._removeUnneededTagKeysFromTagKeysList(mutagenTagKeys)

        otherTagNames = []
        for tagKey in relevantTagKeys:
            if (tagKey.lower() not in tagFieldKeysFlac):
                otherTagNames.append(tagKey.lower())

        for tagNameKey in otherTagNames:
            tagValue = self._getTagValueFromMutagenInterface(mutagenInterface, tagNameKey)
            otherTags[tagNameKey] = tagValue

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
        mutagenInterface = mutagen.File(self.audioFilepath)

        mutagenInterface['date_all_plays'] = audioFileTags.dateAllPlays
        mutagenInterface['date_last_played'] = audioFileTags.dateLastPlayed
        mutagenInterface['play_count'] = audioFileTags.playCount
        mutagenInterface['votes'] = audioFileTags.votes
        mutagenInterface['rating'] = audioFileTags.rating

        mutagenInterface.save()

    def _removeUnneededTagKeysFromTagKeysList(self, flacKeys):
        keysToRemove = [
            'replaygain_album_gain',
            'replaygain_album_peak',
            'replaygain_track_gain',
            'replaygain_track_peak'
        ]

        for removeKey in keysToRemove:
            try:
                flacKeys.remove(removeKey)
            except:
                pass

        return flacKeys

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

    def setCustomTag(self, tagName, value):
        mutagenInterface = mutagen.File(self.audioFilepath)

        tagName = tagName.lower()
        mutagenInterface[tagName] = value

        mutagenInterface.save() 