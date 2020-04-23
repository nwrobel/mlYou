import unittest

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import mlu.tags.io_new

class TestTagsIOModuleNew(unittest.TestCase):
    def setUp(self):
        self.testAudioFileFLAC = "D:\\Temp\\mlu-test\\test-audio-filetypes\\test.flac"
        self.testAudioFileMp3 = "D:\\Temp\\mlu-test\\test-audio-filetypes\\test.mp3"
        self.testAudioFileM4A = "D:\\Temp\\mlu-test\\test-audio-filetypes\\test.m4a"

 
    def testAudioFileTagIOHandlerFLAC(self):
        '''
        Tests tag reading/writing for a test FLAC file.
        '''
        handler = mlu.tags.io_new.AudioFileTagIOHandler(self.testAudioFileFLAC)
        tags = handler.getTags()

        self.assertIsNotNone(tags)

    def testAudioFileTagIOHandlerMp3(self):
        '''
        Tests tag reading/writing for a test Mp3 file.
        '''
        handler = mlu.tags.io_new.AudioFileTagIOHandler(self.testAudioFileMp3)
        tags = handler.getTags()

        self.assertIsNotNone(tags)

    def testAudioFileTagIOHandlerM4A(self):
        '''
        Tests tag reading/writing for a test M4A file.
        '''
        handler = mlu.tags.io_new.AudioFileTagIOHandler(self.testAudioFileM4A)
        tags = handler.getTags()

        self.assertIsNotNone(tags)