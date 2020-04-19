import unittest

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import mlu.tags.io
import mlu.common.file
import mlutest.common

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

        tagValuesFlac = [tagData['tagValues'] for tagData in testAudioFilesTagData if tagData['file'] == 'test.flac'][0]
        tagValuesMp3 = [tagData['tagValues'] for tagData in testAudioFilesTagData if tagData['file'] == 'test.mp3'][0]
        tagValuesM4A = [tagData['tagValues'] for tagData in testAudioFilesTagData if tagData['file'] == 'test.m4a'][0]

        self.testAudioFileFLAC = TestAudioFile(
            filepath=mlu.common.file.JoinPaths(testAudioFileDir, 'test.flac'),
            tagValues=tagValuesFlac
        )

        self.testAudioFileMP3 = TestAudioFile(
            filepath=mlu.common.file.JoinPaths(testAudioFileDir, 'test.mp3'),
            tagValues=tagValuesMp3
        )

        self.testAudioFileM4A = TestAudioFile(
            filepath=mlu.common.file.JoinPaths(testAudioFileDir, 'test.m4a'),
            tagValues=tagValuesM4A
        )   

        self.notSupportedAudioFile = "{}.ogg".format(mlutest.common.getRandomFilepath())
        self.notExistFile = mlutest.common.getRandomFilepath()

class TestTagsIOModule(unittest.TestCase):
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
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileFLAC.filepath)
        self.assertEqual(handler.audioFileType, 'flac')

        # Test MP3 file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileMP3.filepath)
        self.assertEqual(handler.audioFileType, 'mp3')

        # Test M4A file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileM4A.filepath)
        self.assertEqual(handler.audioFileType, 'm4a')

        # Test non-supported filetype given
        self.assertRaises(ValueError, mlu.tags.io.AudioFileTagIOHandler, self.testData.notSupportedAudioFile)

    def testAudioFileTagIOHandlerReadWrite(self, audioFileTagIOHandler, expectedTagValues):
        '''
        Tests tag reading/writing for any given test AudioFileTagIOHandler instance. Used as a 
        helper function.

        The test will check that the given expected tag values match those that are read using the
        handler. Then it will check to ensure that reading undefined tags results in an empty value
        being returned.

        To test writing, the test will write new values for all of the expected (existing) tag values,
        using the handler, then read them back to ensure the new value is set. It will also check
        to ensure that writing a new, undefined tag is successful.

        Params:
            audioFileTagIOHandler: the handler instance to test (is defined with a test audio file type)
            expectedTagValues: dict of the expected tag names and values that this handler should 
                be expected to read
        '''
        # Test tag reading: defined, existing tags
        for tagName in expectedTagValues:
            expectedTagValue = expectedTagValues[tagName]
            actualTagValue = audioFileTagIOHandler.getAudioTagValue(tagName)

            self.assertEqual(actualTagValue, expectedTagValue)

        # Test tag reading: undefined tags
        for x in range(100):
            testUndefinedTagName = mlutest.common.getRandomString(length=30, allowSpace=True)
            actualTagValue = audioFileTagIOHandler.getAudioTagValue(testUndefinedTagName)
            self.assertEqual(actualTagValue, '')

        # Test tag writing: defined, existing tags
        for tagName in expectedTagValues:
            testTagValue = mlutest.common.getRandomString(allowDigits=True, allowSpecial=True, allowSpace=True, allowUppercase=True)
            audioFileTagIOHandler.setAudioTagValue(tagName, testTagValue)
            actualTagValue = audioFileTagIOHandler.getAudioTagValue(tagName)

            self.assertEqual(actualTagValue, testTagValue)
        
        # Test tag writing: new tags
        for x in range(100):
            testUndefinedTagName = mlutest.common.getRandomString(length=30, allowSpace=True)
            testTagValue = mlutest.common.getRandomString(allowDigits=True, allowSpecial=True, allowSpace=True, allowUppercase=True)

            audioFileTagIOHandler.setAudioTagValue(testUndefinedTagName, testTagValue)
            actualTagValue = audioFileTagIOHandler.getAudioTagValue(testUndefinedTagName)

            self.assertEqual(actualTagValue, testTagValue)

    def testAudioFileTagIOHandlerFLAC(self):
        '''
        Tests tag reading/writing for a test FLAC file.
        '''
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileFLAC.filepath)
        self.testAudioFileTagIOHandlerReadWrite(handler, self.testData.testAudioFileFLAC.tagValues)

    def testAudioFileTagIOHandlerMp3(self):
        '''
        Tests tag reading/writing for a test MP3 file.
        '''
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileMP3.filepath)
        self.testAudioFileTagIOHandlerReadWrite(handler, self.testData.testAudioFileMP3.tagValues)

    def testAudioFileTagIOHandlerAAC(self):
        '''
        Tests tag reading/writing for a test M4A file.
        '''
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileM4A.filepath)
        self.testAudioFileTagIOHandlerReadWrite(handler, self.testData.testAudioFileM4A.tagValues)
