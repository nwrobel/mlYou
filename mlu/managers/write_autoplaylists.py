from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import mlu.tags.io
import mlu.tags.values
import mlu.tags.common
import mlu.library.audiolib
from mlu.settings import MLUSettings

class WriteAutoplaylistsManager:
    def __init__(self, mluSettings: MLUSettings, commonLogger: mypycommons.logger.CommonLogger):
        if (mluSettings is None):
            raise TypeError("MLUSettings not passed to RatestatTagsUpdater")
        if (commonLogger is None):
            raise TypeError("CommonLogger not passed to RatestatTagsUpdater")

        self._settings = mluSettings
        self._logger = commonLogger.getLogger()
        
        tagFile = self._settings.userConfig.tagBackupFilepath
        self._tagsJson = mypycommons.file.readJsonFile(tagFile)

        self._clearPreviousAutoplaylists()

    def _clearPreviousAutoplaylists(self):
        for ratingPlaylistCfg in self._settings.userConfig.autoplaylistsConfig.ratingConfigs:
            playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, ratingPlaylistCfg.filename)
            mypycommons.file.deletePath(playlistFilepath)

        for playlistCfg in self._settings.userConfig.autoplaylistsConfig.unratedConfigs:
            playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, playlistCfg.filename)
            mypycommons.file.deletePath(playlistFilepath)

    def writeRatingAutoplaylists(self):
        for ratingPlaylistCfg in self._settings.userConfig.autoplaylistsConfig.ratingConfigs:
            playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, ratingPlaylistCfg.filename)
            playlistItems = []
           
            for audioFileTags in self._tagsJson:
                filepath = audioFileTags['filepath']
                tags = mlu.tags.values.AudioFileTags.fromJsonDict(audioFileTags['tags'])

                if (tags.rating >= ratingPlaylistCfg.minValue and tags.rating <= ratingPlaylistCfg.maxValue):
                    playlistItems.append(
                        {
                            'filepath': filepath,
                            'tags': tags
                        }
                    )

            # sort by multiple attributes
            # Rating descending, then by albumArtist - album - trackNumber
            playlistItems.sort(key=lambda x: (x['tags'].albumArtist, x['tags'].album))
            playlistItems.sort(key=lambda x: (float(x['tags'].rating)), reverse=True)

            playlistItemsSorted = []
            for playlistItem in playlistItems:
                playlistItemsSorted.append(playlistItem['filepath'])

            mypycommons.file.writeToFile(filepath=playlistFilepath, content=playlistItemsSorted) 

    def writeUnratedAutoplaylists(self):
        for playlistCfg in self._settings.userConfig.autoplaylistsConfig.unratedConfigs:
            playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, playlistCfg.filename)
            playlistItems = []

            if (playlistCfg.genreOperator == "OR"):
                playlistItems = self._getPlaylistItemsOR(playlistCfg)
            else:
                playlistItems = self._getPlaylistItemsAND(playlistCfg)


            if (playlistCfg.fileOperator == "a" and mypycommons.file.pathExists(playlistFilepath)):
                existingPlaylistFilepaths = mypycommons.file.readFile(playlistFilepath)
                existingPlaylistItems = self._getPlaylistItems(existingPlaylistFilepaths)
                playlistItems = self._removeDupes(existingPlaylistItems + playlistItems)

            playlistItems.sort(key=lambda x: (x['tags'].albumArtist, x['tags'].album))
            playlistItemFilepaths = [x['filepath'] for x in playlistItems]
            mypycommons.file.writeToFile(filepath=playlistFilepath, content=playlistItemFilepaths)   

  
    
    def _removeDupes(self, playlistItems):
        unique = {}
        for item in playlistItems:
            unique[item['filepath']] = item['tags']

        newList = []
        for filepath, tags in unique.items():
            newList.append(
            {
                'filepath': filepath,
                'tags': tags
            }
        )
        return newList

    def _getPlaylistItems(self, filepaths):
        items = [x for x in self._tagsJson if (x['filepath'] in filepaths)]
        return items

    def _sortPlaylistItems(self, playlistItems):
        # sort by albumArtist - album 
        playlistItems.sort(key=lambda x: (x['tags'].albumArtist, x['tags'].album))

    def _removeDupesFromList(self, inputList):
        return list(dict.fromkeys(inputList))

    def _getPlaylistItemsOR(self, unratedCfg):
        playlistItems = []
        for audioFileTags in self._tagsJson:
            filepath = audioFileTags['filepath']
            tags = mlu.tags.values.AudioFileTags.fromJsonDict(audioFileTags['tags'])

            # if the configured genre is in the list of genres for this song
            for genreCfg in unratedCfg.genres:
                if (genreCfg in tags.genre and 
                    tags.rating == 0 and 
                    not self._isFilepathIsInList(playlistItems, filepath)
                ):
                    playlistItems.append(
                        {
                            'filepath': filepath,
                            'tags': tags
                        }
                    )   
        return playlistItems

    def _getPlaylistItemsAND(self, unratedCfg):
        playlistItems = []
        for audioFileTags in self._tagsJson:
            filepath = audioFileTags['filepath']
            tags = mlu.tags.values.AudioFileTags.fromJsonDict(audioFileTags['tags'])

            hasAllGenres = True
            for genreCfg in unratedCfg.genres:
                if (not genreCfg in tags.genre):
                    hasAllGenres = False

            if (hasAllGenres and tags.rating == 0):
                playlistItems.append(
                    {
                        'filepath': filepath,
                        'tags': tags
                    }
                )   
        return playlistItems

    def _isFilepathIsInList(self, inputList, filepath):
        found = [x for x in inputList if x['filepath'] == filepath]
        if (found):
            return True
        else:
            return False



