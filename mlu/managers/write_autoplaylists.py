from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import mlu.tags.io
import mlu.tags.values
import mlu.tags.common
import mlu.library.audiolib
from mlu.settings import MLUSettings
import re


class AutoplaylistQueryResult:
    def __init__(self, filepath, tags, genresQuery, fileHasGenresQuery, originalQuery):
        self.filepath = filepath
        self.tags = tags
        self.genresQuery = genresQuery # ex ['Industrial', 'Industrial Rock', 'Industrial Metal']
        self.fileHasGenresQuery = fileHasGenresQuery  # ex: [False, True, True]

        logicalQuery = originalQuery.replace("'", "")
        counter = 0
        for genre in genresQuery:
            logicalQuery = logicalQuery.replace(genre, str(self.fileHasGenresQuery[counter]), 1)
            counter += 1

        self.expression = logicalQuery

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

        if (not mypycommons.file.pathExists(self._settings.userConfig.autoplaylistsConfig.outputDir)):
            mypycommons.file.createDirectory(self._settings.userConfig.autoplaylistsConfig.outputDir)

    def _clearPreviousAutoplaylists(self):
        # Clear rating autoplaylists
        # for ratingPlaylistCfg in self._settings.userConfig.autoplaylistsConfig.ratingConfigs:
        #     playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, ratingPlaylistCfg.filename)
        #     mypycommons.file.deletePath(playlistFilepath)

        # Clear 

        # for playlistCfg in self._settings.userConfig.autoplaylistsConfig.unratedConfig.simpleCfg.:
        #     playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, ratingPlaylistCfg.filename)
        #     mypycommons.file.deletePath(playlistFilepath)

        # for playlistCfg in self._settings.userConfig.autoplaylistsConfig.ratingConfigs:
        #     playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, playlistCfg.filename)
        #     mypycommons.file.deletePath(playlistFilepath)
        pass

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
            # Rating descending, then by albumArtist - album 
            playlistItems.sort(key=lambda x: (x['tags'].albumArtist, x['tags'].album))
            playlistItems.sort(key=lambda x: (float(x['tags'].rating)), reverse=True)

            playlistItemsSorted = []
            for playlistItem in playlistItems:
                playlistItemsSorted.append(playlistItem['filepath'])

            mypycommons.file.writeToFile(filepath=playlistFilepath, content=playlistItemsSorted) 

    def writeUnratedAutoplaylists(self):
        for advancedCfg in self._settings.userConfig.autoplaylistsConfig.unratedConfig.advancedConfigs:
            playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, advancedCfg.filename)
            playlistItems = []

            query = advancedCfg.query
            theGenres = re.findall(r"'(.*?)'", query, re.DOTALL)
            queryResults = []

            for audioFileTags in self._tagsJson:
                filepath = audioFileTags['filepath']
                tags = mlu.tags.values.AudioFileTags.fromJsonDict(audioFileTags['tags'])
                fileHasGenresQuery = []

                for genre in theGenres:
                    if (genre in tags.genre):
                        fileHasGenresQuery.append(True)
                    else:
                        fileHasGenresQuery.append(False)

                queryResults.append(
                    AutoplaylistQueryResult(filepath, tags, theGenres, fileHasGenresQuery, query)
                )

            # Take AutoplaylistQueryResult and feed it to the python eval
            for result in queryResults:
                shouldBeInAutoplaylist = (eval(result.expression) and result.tags.rating == 0)
                if (shouldBeInAutoplaylist):
                    playlistItems.append(
                    {
                            'filepath': result.filepath,
                            'tags': result.tags
                        }
                    )

            playlistItems.sort(key=lambda x: (x['tags'].albumArtist, x['tags'].album))
            playlistFilepaths = [x['filepath'] for x in playlistItems]

            mypycommons.file.writeToFile(filepath=playlistFilepath, content=playlistFilepaths) 


    def _audioFileHasThisGenre(self, filepath, theGenre):

        item = [audioFileTags for audioFileTags in self._tagsJson if audioFileTags[filepath] == filepath]
        tags = mlu.tags.values.AudioFileTags.fromJsonDict(item[0]['tags'])

        if (theGenre in tags.genre):
            return True

        return False

    def writeUnratedSimpleGenreAutoplaylists(self):
        filenamePattern = self._settings.userConfig.autoplaylistsConfig.unratedConfig.simpleCfg.filenamePattern
        genresToDo = self._settings.userConfig.autoplaylistsConfig.unratedConfig.simpleCfg.genres

        for givenGenre in genresToDo:
            filename = filenamePattern.format(givenGenre)
            playlistFilepath = mypycommons.file.joinPaths(self._settings.userConfig.autoplaylistsConfig.outputDir, filename)

            itemsMatching = self._getFilesMatchingGenre(givenGenre)
            itemsMatching.sort(key=lambda x: (x['tags'].albumArtist, x['tags'].album))
            playlistFilepaths = [x['filepath'] for x in itemsMatching]

            mypycommons.file.writeToFile(filepath=playlistFilepath, content=playlistFilepaths) 

    
    def _getFilesMatchingGenre(self, genre):
        playlistItems = []
        for audioFileTags in self._tagsJson:
            filepath = audioFileTags['filepath']
            tags = mlu.tags.values.AudioFileTags.fromJsonDict(audioFileTags['tags'])

            if (genre in tags.genre and
                tags.rating == 0):
                    playlistItems.append(
                        {
                            'filepath': filepath,
                            'tags': tags
                        }
                    )           

        return playlistItems

    

  
    
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



