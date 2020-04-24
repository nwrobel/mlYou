import unittest

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import mlu.tags.io

class TestAudioFile:
    '''
    Class representing a test audio file and the 'actual' tag values that it has. This is a data
    structure used by the TestData class.
    '''
    def __init__(self, filepath, tagValues):
        self.filepath = filepath
        self.tagValues = tagValues

class TestData:
    '''
    Class representing the test data that will be used for a single test run of the tags.io module.
    This data consists of the test audio filepaths and the 'actual' tag values for each of these
    files.

    These audio files are predefined, static files which have had their tags set through some 
    external methods (not set using MLU), and the tags.json file defines these tags for the files.
    '''
    def __init__(self, testAudioFileDir):

        testAudioFilesTagDataFilepath = mlu.common.file.JoinPaths(testAudioFileDir, 'tags.json')
        testAudioFilesTagData = mlu.common.file.getDictFromJsonFile(testAudioFilesTagDataFilepath)

        flacTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'flac']
        mp3TestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'mp3']
        m4aTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'm4a']

        self.testAudioFilesFLAC = []
        self.testAudioFilesMp3 = []
        self.testAudioFilesM4A = []

        for flacTestFile in flacTestFilesData:
            testAudioFile = TestAudioFile(
                filepath=mlu.common.file.JoinPaths(testAudioFileDir, flacTestFile['filename']),
                tagValues=flacTestFile['tagValues']
            )
            self.testAudioFilesFLAC.append(testAudioFile)

        for mp3TestFile in mp3TestFilesData:
            testAudioFile = TestAudioFile(
                filepath=mlu.common.file.JoinPaths(testAudioFileDir, mp3TestFile['filename']),
                tagValues=mp3TestFile['tagValues']
            )
            self.testAudioFilesMp3.append(testAudioFile)

        for m4aTestFile in m4aTestFilesData:
            testAudioFile = TestAudioFile(
                filepath=mlu.common.file.JoinPaths(testAudioFileDir, m4aTestFile['filename']),
                tagValues=m4aTestFile['tagValues']
            )
            self.testAudioFilesM4A.append(testAudioFile)


        self.notSupportedAudioFile = "{}.ogg".format(mlutest.common.getRandomFilepath())
        self.notExistFile = mlutest.common.getRandomFilepath()



class TestTagsIOModuleNew(unittest.TestCase):
    def setUp(self):
        '''
        Sets up the test data for the tests of the tags.io module. The test audio files are copied
        from the test resource dir to the mlu cache dir, where they will be manipulated by the tests
        while preserving the original test data files.
        '''
        testResDir = mlu.common.file.getTestResourceFilesDirectory()
        testAudioFilesResDir = mlu.common.file.JoinPaths(testResDir, 'test-audio-filetypes')
        cacheDir = mlu.common.file.getMLUCacheDirectory()

        testDataFiles = mlu.common.file.GetAllFilesDepth1(rootPath=testAudioFilesResDir)
        mlu.common.file.CopyFilesToDirectory(srcFiles=testDataFiles, destDir=cacheDir)

        self.testData = TestData(testAudioFileDir=cacheDir)

    def tearDown(self):
        cacheDir = mlu.common.file.getMLUCacheDirectory()
        mlu.common.file.DeleteDirectory(cacheDir)

    def testAudioFileTagIOHandlerConstructor(self):
        '''
        Tests the constructor of the AudioFileTagIOHandler class to ensure only supported audio
        formats are accepted and that only existing files are accepted.
        '''
        # Test nonexisting file given
        self.assertRaises(ValueError, mlu.tags.io.AudioFileTagIOHandler, self.testData.notExistFile)

        # Test FLAC file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFilesFLAC.filepath)
        self.assertEqual(handler._audioFileType, 'flac')

        # Test MP3 file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileMP3.filepath)
        self.assertEqual(handler._audioFileType, 'mp3')

        # Test M4A file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileM4A.filepath)
        self.assertEqual(handler._audioFileType, 'm4a')

        # Test non-supported filetype given
        self.assertRaises(Exception, mlu.tags.io.AudioFileTagIOHandler, self.testData.notSupportedAudioFile)

 
    def testAudioFileTagIOHandlerFLAC(self):
        '''
        Tests tag reading/writing for a test FLAC file.
        '''
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testAudioFileFLAC)
        tags = handler.getTags()

        self.assertIsNotNone(tags)

    def testAudioFileTagIOHandlerMp3(self):
        '''
        Tests tag reading/writing for a test Mp3 file.
        '''
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testAudioFileMp3)
        tags = handler.getTags()

        self.assertIsNotNone(tags)

    def testAudioFileTagIOHandlerM4A(self):
        '''
        Tests tag reading/writing for a test M4A file.
        '''
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testAudioFileM4A)
        tags = handler.getTags()

        self.assertIsNotNone(tags)