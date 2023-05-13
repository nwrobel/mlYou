import traceback
from typing import List

from mlu.tags.io import AudioFileMetadataHandler, AudioFileFormatNotSupportedError, AudioFileNonExistentError

class AudioFileError:
    ''' 
    '''
    NOT_FOUND = "Audio file path cannot be found or is invalid"
    NOT_SUPPORTED = "Audio file format is not supported"

    def __init__(self, audioFilepath: str, exceptionMessage: str) -> None:
        self.audioFilepath = audioFilepath
        self.exceptionMessage = exceptionMessage

def testAudioFilesForErrors(audioFilepaths: List[str]):
    ''' 
    '''
    audioFileErrorList = []

    for audioFilepath in audioFilepaths:
        try:
            handler = AudioFileMetadataHandler(audioFilepath)
            handler.getTags()
            handler.getProperties()

        except AudioFileNonExistentError:
            audioFileErrorList.append(AudioFileError(audioFilepath, AudioFileError.NOT_FOUND))

        except AudioFileFormatNotSupportedError:
            audioFileErrorList.append(AudioFileError(audioFilepath, AudioFileError.NOT_SUPPORTED))

        # catch all other exceptions
        except Exception as e:
            excStr = traceback.format_exc()
            audioFileErrorList.append(AudioFileError(audioFilepath, excStr))

    return audioFileErrorList
