import traceback
from mlu.tags.io import AudioFileMetadataHandler, AudioFileFormatNotSupportedError, AudioFileNonExistentError
from mlu.settings import MLUSettings

class AudioFileError:
    NOT_FOUND = "Audio file path cannot be found or is invalid"
    NOT_SUPPORTED = "Audio file format is not supported"
    def __init__(self, audioFilepath, exceptionMessage):
        self.audioFilepath = audioFilepath
        self.exceptionMessage = exceptionMessage

def testAudioFilesForErrors(audioFilepathList):
    audioFileErrorList = []

    # audioFilepath:'Z:\\Music Library\\Content\\Music\\Garbage\\Garbage\\07. Garbage - Vow.mp3'
    # audioFilepath:"Z:\\Music Library\\Content\\Music\\Various Artists\\_no-album\\Limp Bizkit 'Nookie' vs. Nine inch nails 'Closer'_28527501 - la_croche_remix.mp3"
    # audioFilepathList = [
    #     'Z:\\Music Library\\Content\\Music\\Garbage\\Garbage\\07. Garbage - Vow.mp3',
    #     "Z:\\Music Library\\Content\\Music\\Various Artists\\_no-album\\Limp Bizkit 'Nookie' vs. Nine inch nails 'Closer'_28527501 - la_croche_remix.mp3"
    # ]

    for audioFilepath in audioFilepathList:
        try:
            handler = AudioFileMetadataHandler(audioFilepath)
            handler.getTags()

        except AudioFileNonExistentError:
            audioFileErrorList.append(AudioFileError(audioFilepath, AudioFileError.NOT_FOUND))

        except AudioFileFormatNotSupportedError:
            audioFileErrorList.append(AudioFileError(audioFilepath, AudioFileError.NOT_SUPPORTED))

        # catch all other exceptions
        except Exception as e:
            excStr = traceback.format_exc()
            audioFileErrorList.append(AudioFileError(audioFilepath, excStr))

    return audioFileErrorList

# Todo: move to mypycommons
def removeTrailingSlashFromPath(path):
    while (path[-1] == '/' or path[-1] == '\\'):
        path = path[:-1] # remove last char. from string
        
    return path

# Todo: move to mypycommons
def addTrailingSlashToPath(path):
    if (path[-1] != '/' and path[-1] != '\\'):
        if ('/' in path):
            path += '/'
        elif ('\\' in path):
            path += '\\'
        
    return path

def getAudioFilepathWithoutMusicLibraryDir(audioFilepath):
    musicLibRootDir = addTrailingSlashToPath(MLUSettings.userConfig.audioLibraryRootDirectory)
    newAudioPath = audioFilepath.replace(musicLibRootDir, "")
    return newAudioPath

