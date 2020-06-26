import envsetup
envsetup.PreparePythonProjectEnvironment()

# setup logging for this script using MLU preconfigured logger
import mlu.common.logger
mlu.common.logger.initMLULogger()
logger = mlu.common.logger.getMLULogger()

import mlu.tags.backup

tagsBackupFilepath = "C:\\Nick-Local-Data\\Development\\mlYou\\~cache\\audio-tag-backups\\[2020-05-22 04_12_23] Music Library Audio Tags Full Backup.json"
mlu.tags.backup.restoreMusicLibraryAudioTagsFromBackup(tagsBackupFilepath)
