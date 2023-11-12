'''
mlu.tags.values

Author:   Nick Wrobel
Created:  2021-12-11
Modified: 2021-12-17

Module containing the data structures used to hold audio file tags and properties values.
'''
from datetime import timedelta

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
        dateAdded,
        dateAllPlays, 
        dateLastPlayed, 
        playCount, 
        rating
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
        self.dateAdded = dateAdded
        self.dateAllPlays = dateAllPlays
        self.dateLastPlayed = dateLastPlayed
        self.playCount = playCount
        self.rating = rating

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
            self.dateAdded == otherAudioFileTags.dateAdded and
            self.dateAllPlays == otherAudioFileTags.dateAllPlays and
            self.dateLastPlayed == otherAudioFileTags.dateLastPlayed and
            self.playCount == otherAudioFileTags.playCount and
            self.rating == otherAudioFileTags.rating
        )

        return tagsAreEqual

class AudioFileProperties:
    '''
    Data structure holding the values for a single audio file of all the file properties supported 
    by MLU.
    '''
    def __init__(self, duration: timedelta):
        self.duration = duration