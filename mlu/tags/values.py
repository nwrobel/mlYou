'''
mlu.tags.values

Author:   Nick Wrobel
Created:  2021-12-11
Modified: 2021-12-17

Module containing the data structures used to hold audio file tags and properties values.
'''
import json
import mlu.tags.common
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
        genre,
        dateLastPlayed, 
        playCount, 
        rating
    ):
        self.title = title
        self.artist = artist
        self.albumArtist = albumArtist
        self.album = album
        self.dateLastPlayed = dateLastPlayed

        if (isinstance(genre, list)):
            self.genre = genre
        elif (genre):
            self.genre = mlu.tags.common.formatAudioTagToValuesList(genre)
        else:
            self.genre = genre

        if (playCount):
            self.playCount = int(playCount)
        else:
            self.playCount = 0
        
        if (rating):
            self.rating = float(rating)
        else:
            self.rating = 0

    @classmethod
    def fromJsonDict(cls, jsonDict):
        return cls(**jsonDict)

    def equals(self, otherAudioFileTags):
        tagsAreEqual = (
            self.title == otherAudioFileTags.title and
            self.artist == otherAudioFileTags.artist and
            self.album == otherAudioFileTags.album and
            self.albumArtist == otherAudioFileTags.albumArtist and
            self.genre == otherAudioFileTags.genre and
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