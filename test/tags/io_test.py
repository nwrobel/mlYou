'''
Tests for mlu.tags.io, which also tests the mlu.tags.audiofmt modules.

'''

#from email.mime import audio
import unittest
import sys
import os
from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

# Add project root to PYTHONPATH so MLU modules can be imported
scriptPath = os.path.dirname(os.path.realpath(__file__))
projectRoot = os.path.abspath(os.path.join(scriptPath ,"../.."))
sys.path.insert(0, projectRoot)

from mlu.settings import MLUSettings
import mlu.tags.io
import mlu.tags.values
import mlu.tags.audiofmt.flac
import mlu.tags.audiofmt.mp3
import mlu.tags.audiofmt.m4a
import test.helpers.common

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
    def __init__(self, testAudioFilesDir, testAudioTagsFile):

        testAudioFilesTagData = mypycommons.file.readJsonFile(testAudioTagsFile)

        flacTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'flac'][0]
        mp3TestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'mp3'][0]
        m4aTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'm4a'][0]
        opusTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'opus'][0]

        self.testAudioFilesFLAC = self.getTestFilesFromData(testAudioFilesDir, flacTestFilesData)
        self.testAudioFilesMp3 = self.getTestFilesFromData(testAudioFilesDir, mp3TestFilesData)
        self.testAudioFilesM4A = self.getTestFilesFromData(testAudioFilesDir, m4aTestFilesData)
        self.testAudioFilesOggOpus = self.getTestFilesFromData(testAudioFilesDir, opusTestFilesData)

        self.notSupportedAudioFile = "{}.wav".format(test.helpers.common.getRandomFilepath())
        self.notExistFile = test.helpers.common.getRandomFilepath()

    def getTestFilesFromData(self, testAudioFilesDir, testFilesData):
        testFiles = []
        for testFile in testFilesData:
            testAudioFile = TestAudioFile(
                filepath=mypycommons.file.joinPaths(testAudioFilesDir, testFile['filename']),
                tagValues=testFile['tagValues']
            )
            testFiles.append(testAudioFile)

        return testFiles


class TestTagsIOModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        '''
        Sets up the test data for the tests of the tags.io module. The test audio files are copied
        from the test resource dir to the mlu cache dir, where they will be manipulated by the tests
        while preserving the original test data files.
        '''
        super(TestTagsIOModule, self).setUpClass

        testAudioFilesDir = mypycommons.file.joinPaths(MLUSettings.testDataDir, 'test-audio-files')
        testAudioTagsFile = mypycommons.file.joinPaths(MLUSettings.testDataDir, 'test-audio-files-tags.json')
        tempTestAudioFilesDir = mypycommons.file.joinPaths(MLUSettings.tempDir, 'test-audio-files')

        mypycommons.file.createDirectory(tempTestAudioFilesDir)

        # copy the test audio files from the static test files dir to the temp cache test files dir
        # also copy the tags.json file
        testAudioFilesSrc = mypycommons.file.getChildPathsRecursive(rootDirPath=testAudioFilesDir, pathType='file')
        for testAudioFile in testAudioFilesSrc:
            mypycommons.file.copyToDirectory(path=testAudioFile, destDir=tempTestAudioFilesDir)

        self.testData = TestData(tempTestAudioFilesDir, testAudioTagsFile)


    @classmethod
    def tearDownClass(self):  
        super(TestTagsIOModule, self).tearDownClass      
        mypycommons.file.deletePath(MLUSettings.tempDir)

    def test_AudioFileMetadataHandler_Constructor(self):
        '''
        Tests the constructor of the AudioFileTagIOHandler class to ensure only supported audio
        formats are accepted and that only existing files are accepted.
        '''
        # Test nonexisting file given
        self.assertRaises(ValueError, mlu.tags.io.AudioFileMetadataHandler, self.testData.notExistFile)

        # Test FLAC file given
        handler = mlu.tags.io.AudioFileMetadataHandler(self.testData.testAudioFilesFLAC[0].filepath)
        self.assertEqual(handler._audioFileType, 'flac')
        self.assertTrue(isinstance(handler._audioFmtHandler, mlu.tags.audiofmt.flac.AudioFormatHandlerFLAC))

        # Test MP3 file given
        handler = mlu.tags.io.AudioFileMetadataHandler(self.testData.testAudioFilesMp3[0].filepath)
        self.assertEqual(handler._audioFileType, 'mp3')
        self.assertTrue(isinstance(handler._audioFmtHandler, mlu.tags.audiofmt.mp3.AudioFormatHandlerMP3))


        # Test M4A file given
        handler = mlu.tags.io.AudioFileMetadataHandler(self.testData.testAudioFilesM4A[0].filepath)
        self.assertEqual(handler._audioFileType, 'm4a')
        self.assertTrue(isinstance(handler._audioFmtHandler, mlu.tags.audiofmt.m4a.AudioFormatHandlerM4A))

        # Test non-supported filetype given
        self.assertRaises(Exception, mlu.tags.io.AudioFileMetadataHandler, self.testData.notSupportedAudioFile)

    def test_AudioFileMetadataHandler_FLAC(self):
        '''
        Tests tag reading/writing for a test FLAC file.
        '''
        for testAudioFile in self.testData.testAudioFilesFLAC:
            handler = mlu.tags.io.AudioFileMetadataHandler(testAudioFile.filepath)
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)

            self.writeCustomTag_Test(handler)

    def test_AudioFileMetadataHandler_MP3(self):
        '''
        Tests tag reading/writing for a test Mp3 file.
        '''
        for testAudioFile in self.testData.testAudioFilesMp3:
            handler = mlu.tags.io.AudioFileMetadataHandler(testAudioFile.filepath)
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)

            self.writeCustomTag_Test(handler)

    def test_AudioFileMetadataHandler_M4A(self):
        '''
        Tests tag reading/writing for a test M4A file.
        '''
        for testAudioFile in self.testData.testAudioFilesM4A:
            handler = mlu.tags.io.AudioFileMetadataHandler(testAudioFile.filepath)
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)

            self.writeCustomTag_Test(handler)

    def test_AudioFileMetadataHandler_OggOpus(self):
        '''
        Tests tag reading/writing for a test Ogg Opus file.
        '''
        testFileData = self.testData.testAudioFilesOggOpus[0]
        handler = mlu.tags.io.AudioFileMetadataHandler(testFileData.filepath)
        tags = handler.getTags()

        self.writeCustomTag_Test(handler)
        
        # for testAudioFile in self.testData.testAudioFilesOggOpus:
        #     handler = mlu.tags.io.AudioFileMetadataHandler(testAudioFile.filepath)
        #     self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
        #     self._checkAudioFileTagIOHandlerWrite(handler)

    def _checkAudioFileTagIOHandlerRead(self, audioFileMetadataHandler, expectedTagValues):
        '''
        Tests tag reading for any given test AudioFileTagIOHandler instance. Used as a 
        helper function.

        The test will check that the given expected tag values match those that are read using the
        handler.

        Params:
            audioFileTagIOHandler: the handler instance to test (is defined with a test audio file type)
            expectedTagValues: dict of the expected tag names and values that this handler should 
                be expected to read out
        '''
        tags = audioFileMetadataHandler.getTags()
        actualTagValues = tags.__dict__        

        # Remove the otherTags value from expected tags (we will check this later)
        try:
            expectedOtherTags = expectedTagValues['OTHER_TAGS']
            del expectedTagValues['OTHER_TAGS']
        except KeyError:
            expectedOtherTags = {}

        # Check that all the expected tags are in the returned tags
        for tagName in expectedTagValues:
            self.assertIn(tagName, actualTagValues)

        # Check that the expected and actual tags values match
        for tagName in expectedTagValues:
            expectedTagValue = expectedTagValues[tagName]
            actualTagValue = actualTagValues[tagName]
            self.assertEqual(expectedTagValue, actualTagValue)

        # Check the other tags values
        for expectedOtherTag in expectedOtherTags:
            expectedTagName = expectedOtherTag['name']
            expectedTagValue = expectedOtherTag['value']

            # test that the other_tags contains each other tag name
            self.assertIn(expectedTagName, actualTagValues['OTHER_TAGS'])

            self.assertEqual(expectedTagValue, actualTagValues['OTHER_TAGS'][expectedTagName])


    def _checkAudioFileTagIOHandlerWrite(self, audioFileMetadataHandler):
        '''
        Tests tag writing for any given test AudioFileMetadataHandler instance. Used as a 
        helper function.

        The test will check that new tag values can be written via the handler.

        Params:
            audioFileMetadataHandler: the handler instance to test (is defined with a test audio file type)
        '''
        tags = audioFileMetadataHandler.getTags()
        newTagValues = {}

        newTagValues['dateAllPlays'] = test.helpers.common.getRandomString(length=20, allowSpecial=False)
        newTagValues['dateLastPlayed'] = test.helpers.common.getRandomString(length=20, allowSpecial=False)
        newTagValues['playCount'] = test.helpers.common.getRandomString(length=20, allowSpecial=False)
        newTagValues['votes'] = test.helpers.common.getRandomString(length=20, allowSpecial=False)
        newTagValues['rating']  = test.helpers.common.getRandomString(length=20, allowSpecial=False)

        tags.dateAllPlays = newTagValues['dateAllPlays']
        tags.dateLastPlayed = newTagValues['dateLastPlayed']
        tags.playCount = newTagValues['playCount']
        tags.votes = newTagValues['votes']
        tags.rating = newTagValues['rating']

        audioFileMetadataHandler.setTags(tags)

        # Use the read test function to ensure the tags are now set to the new tag values 
        self._checkAudioFileTagIOHandlerRead(audioFileMetadataHandler, expectedTagValues=newTagValues)

    def writeCustomTag_Test(self, audioFileMetadataHandler):
        testTagName = "test123"
        testTagValue = "hello hello 123"
        
        audioFileMetadataHandler.setCustomTag(testTagName, testTagValue)

        actualTags = audioFileMetadataHandler.getTags()
        self.assertEqual(testTagValue, actualTags.OTHER_TAGS[testTagName])

if __name__ == '__main__':
    unittest.main()