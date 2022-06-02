'''
mlu.tags.values

Author:   Nick Wrobel
Created:  2021-12-11
Modified: 2021-12-17

Module containing the data structures used to hold audio file tags and properties values.
'''

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
        comment,
        dateAdded,
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
        self.comment = comment
        self.dateAdded = dateAdded
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
            self.composer == otherAudioFileTags.composer and
            self.date == otherAudioFileTags.date and
            self.genre == otherAudioFileTags.genre and
            self.trackNumber == otherAudioFileTags.trackNumber and
            self.totalTracks == otherAudioFileTags.totalTracks and
            self.discNumber == otherAudioFileTags.discNumber and
            self.totalDiscs == otherAudioFileTags.totalDiscs and
            self.bpm == otherAudioFileTags.bpm and
            self.key == otherAudioFileTags.key and
            self.lyrics == otherAudioFileTags.lyrics and
            self.comment == otherAudioFileTags.comment and
            self.dateAdded == otherAudioFileTags.dateAdded and
            self.dateAllPlays == otherAudioFileTags.dateAllPlays and
            self.dateLastPlayed == otherAudioFileTags.dateLastPlayed and
            self.playCount == otherAudioFileTags.playCount and
            self.votes == otherAudioFileTags.votes and
            self.rating == otherAudioFileTags.rating and
            self.OTHER_TAGS == otherAudioFileTags.OTHER_TAGS
        )

        return tagsAreEqual

class AudioFileProperties:
    '''
    Data structure holding the values for a single audio file of all the file properties supported 
    by MLU.
    '''
    def __init__(
        self,
        fileSize,
        fileDateModified,
        duration,
        format,
        bitRate,
        sampleRate,
        numChannels,
        replayGain,
        bitDepth,
        encoder,
        bitRateMode,
        codec
    ):
        self.fileSize = fileSize
        self.fileDateModified = fileDateModified
        self.duration = duration
        self.format = format
        self.bitRate = bitRate
        self.sampleRate = sampleRate
        self.numChannels = numChannels
        self.replayGain = replayGain
        self.bitDepth = bitDepth
        self.encoder = encoder
        self.bitRateMode = bitRateMode
        self.codec = codec