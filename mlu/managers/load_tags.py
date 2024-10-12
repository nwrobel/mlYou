from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import mlu.tags.io
import mlu.tags.common
import mlu.library.audiolib
from mlu.settings import MLUSettings

class AudioFileTagsJson:
    def __init__(self, filepath, tags):
        self.filepath = filepath
        self.tags = tags.__dict__

class LoadLibraryTagsManager:
    def __init__(self, mluSettings: MLUSettings, commonLogger: mypycommons.logger.CommonLogger):
        if (mluSettings is None):
            raise TypeError("MLUSettings not passed to RatestatTagsUpdater")
        if (commonLogger is None):
            raise TypeError("CommonLogger not passed to RatestatTagsUpdater")

        self.settings = mluSettings
        self.logger = commonLogger.getLogger()

    
    def saveLibraryTagsSnapshot(self):
        allAudioFilepaths = mlu.library.audiolib.getAllLibraryAudioFilepaths(self.settings.userConfig.audioLibraryRootDir)

        allTags = []
        for audioFilepath in allAudioFilepaths:
            tagHandler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
            currentTags = tagHandler.getTags()

            allTags.append(
                AudioFileTagsJson(audioFilepath, currentTags)
            )
        
        if (mypycommons.file.pathExists(self.settings.userConfig.tagBackupFilepath)):
            mypycommons.file.deletePath(self.settings.userConfig.tagBackupFilepath)

        allTagsJson = [tags.__dict__ for tags in allTags]
        mypycommons.file.writeJsonFile(self.settings.userConfig.tagBackupFilepath, allTagsJson)