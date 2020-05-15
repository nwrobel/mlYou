'''
mlu.tags.backup

This module handles operations related to making sure the tag values for songs are backed up (cached)
before any changes are made and that the original tag values can be restored in case of errors.
'''

import mlu.cache.io
import mlu.common.display
import mlu.common.time
import mlu.library.musiclib
import mlu.tags.io
from mlu.common.settings import MLUSettings


def _getNewAudioTagsBackupFilepath():
    timeForFilename = (mlu.common.time.getCurrentFormattedTime()).replace(':', '_')
    backupFilename = "[{}] Music Library Audio Tags Full Backup.json".format(timeForFilename)
    filepath = mlu.common.file.JoinPaths(MLUSettings.tagBackupsDir, backupFilename)

    return filepath


def backupMusicLibraryAudioTags():
    backupFilepath = _getNewAudioTagsBackupFilepath()
    allAudioFilepaths = mlu.library.musiclib.getAllMusicLibraryAudioFilepaths()
    audioFilesCount = len(allAudioFilepaths)
    allAudioTags = []
    
    for i, audioFilepath in enumerate(allAudioFilepaths):
        tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFilepath)
        tags = tagHandler.getTags()

        tagsForAudioFile = {}
        tagsForAudioFile['filepath'] = audioFilepath
        tagsForAudioFile['tags'] = tags
        allAudioTags.append(tagsForAudioFile)

        mlu.common.display.printProgressBar(i + 1, audioFilesCount, prefix='Music library tags backup - Loading data:', suffix='Complete', length=100)

    mlu.cache.io.WriteMLUObjectsToJSONFile(mluObjects=allAudioTags, outputFilepath=backupFilepath)

    return backupFilepath

def restoreMusicLibraryAudioTagsFromBackup(backupFilepath):
    backupData = mlu.cache.io.getDictFromJsonFile(backupFilepath)

    for audioFileTagData in backupData:
        audioFilepath = audioFileTagData['filepath']
        tagsDict = audioFileTagData['tags']
        audioFileTags = mlu.tags.io.AudioFileTags(**tagsDict)

        tagHandler = mlu.tags.io.AudioFileTagIOHandler(audioFilepath)
        tagHandler.setTags(audioFileTags)


