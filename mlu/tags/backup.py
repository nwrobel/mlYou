'''
mlu.tags.backup

This module handles operations related to making sure the tag values for songs are backed up (cached)
before any changes are made and that the original tag values can be restored in case of errors.
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.display

import mlu.cache.io
import mlu.library.musiclib
import mlu.tags.io
from mlu.settings import MLUSettings


def _getNewAudioTagsBackupFilepath():
    timeForFilename = (mypycommons.time.getCurrentFormattedTime()).replace(':', '_')
    backupFilename = "[{}] Music Library Audio Tags Full Backup.json".format(timeForFilename)
    filepath = mypycommons.file.JoinPaths(MLUSettings.tagBackupsDir, backupFilename)

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

        mypycommons.display.printProgressBar(i + 1, audioFilesCount, prefix='Music library ({} files) tags backup progress:'.format(audioFilesCount), suffix='Complete', length=100)

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


