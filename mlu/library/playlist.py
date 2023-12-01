'''
mlu.file.playlist

Module containing functionality related to working with audio playlists.
'''
from typing import List
from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

import mlu.library.audiolib
import mlu.tags.io
from mlu.tags.values import AudioFileTags
from mlu.settings import MLUSettings


def getAllPlaylistLines(playlistFilepath):
    '''
    Returns a list of all the audio filepaths contained within a playlist.
    '''
    with open(playlistFilepath, mode='r', encoding='utf-8-sig') as file:
        lines = file.readlines()

    playlistLines = []
    for line in lines:
        lineFixed = line.replace('\n', '') # remove newline char from end of each line

        if (lineFixed):
            playlistLines.append(lineFixed) # only add the line if it isn't empty

    return playlistLines

class RatingAutoplaylistProvider:
    def __init__(self, mluSettings: MLUSettings, commonLogger: mypycommons.logger.CommonLogger) -> None:
        if (mluSettings is None):
            raise TypeError("mluSettings not passed")
        if (commonLogger is None):
            raise TypeError("commonLogger not passed")

        self._settings = mluSettings
        self._logger = commonLogger.getLogger()
        self._allAudioFilesTags = self._loadTags()

    def createRatingAutoplaylists(self):
        for ratingPlaylistCfg in self._settings.userConfig.autoplaylistsConfig.ratingConfigs:
            playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, ratingPlaylistCfg.filename)
            playlistItems = []

            for audioFileTags in self._allAudioFilesTags:
                if (audioFileTags['tags'].rating):
                    rating = float(audioFileTags['tags'].rating)
                    if (rating >= ratingPlaylistCfg.minValue and rating <= ratingPlaylistCfg.maxValue):
                        playlistItems.append(audioFileTags)

            # sort by multiple attributes
            # Rating descending, then by albumArtist - album - trackNumber
            playlistItems.sort(key=lambda x: (x['tags'].albumArtist, x['tags'].album, x['tags'].trackNumber))
            playlistItems.sort(key=lambda x: (float(x['tags'].rating)), reverse=True)

            playlistItemsSorted = []
            for playlistItem in playlistItems:
                playlistItemsSorted.append(playlistItem['filepath'])

            self._createPlaylist(playlistFilepath, playlistItemsSorted)
                    
    def _loadTags(self) -> List[dict]:
        allAudioFilepaths = mlu.library.audiolib.getAllLibraryAudioFilepaths(self._settings.userConfig.audioLibraryRootDir)
        allAudioFilesTags = []

        for audioFilepath in allAudioFilepaths:
            tagHandler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
            currentTags = tagHandler.getTags()  
            allAudioFilesTags.append(
                {
                    'filepath': audioFilepath,
                    'tags': currentTags
                }
            )  

        return allAudioFilesTags  

    def _createPlaylist(self, playlistFilepath, audioFilepaths):
        '''
        Creates a new playlist file from the given list of audio filepaths.
        '''
        mypycommons.file.writeToFile(filepath=playlistFilepath, content=audioFilepaths)  
