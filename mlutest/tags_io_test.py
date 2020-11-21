# NOTE: FILE IS BROKEN, NEEDS FIX

import unittest

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import mlutest.common
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

        flacTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'flac'][0]
        mp3TestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'mp3'][0]
        m4aTestFilesData = [tagData['testfiles'] for tagData in testAudioFilesTagData if tagData['filetype'] == 'm4a'][0]

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



class TestTagsIOModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        '''
        Sets up the test data for the tests of the tags.io module. The test audio files are copied
        from the test resource dir to the mlu cache dir, where they will be manipulated by the tests
        while preserving the original test data files.
        '''
        super(TestTagsIOModule, self).setUpClass

        testResDir = mlu.common.file.getTestResourceFilesDirectory()
        testAudioFilesResDir = mlu.common.file.JoinPaths(testResDir, 'test-audio-filetypes')
        cacheDir = mlu.common.file.getMLUCacheDirectory()

        testDataFiles = mlu.common.file.GetAllFilesDepth1(rootPath=testAudioFilesResDir)
        mlu.common.file.CopyFilesToDirectory(srcFiles=testDataFiles, destDir=cacheDir)

        self.testData = TestData(testAudioFileDir=cacheDir)

    @classmethod
    def tearDownClass(self):
        # super(TestTagsIOModule, self).tearDownClass
        
        # cacheDir = mlu.common.file.getMLUCacheDirectory()
        # mlu.common.file.DeleteDirectory(cacheDir)

    def testAudioFileTagIOHandlerConstructor(self):
        '''
        Tests the constructor of the AudioFileTagIOHandler class to ensure only supported audio
        formats are accepted and that only existing files are accepted.
        '''
        # Test nonexisting file given
        self.assertRaises(ValueError, mlu.tags.io.AudioFileTagIOHandler, self.testData.notExistFile)

        # Test FLAC file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFilesFLAC[0].filepath)
        self.assertEqual(handler._audioFileType, 'flac')

        # Test MP3 file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFilesMp3[0].filepath)
        self.assertEqual(handler._audioFileType, 'mp3')

        # Test M4A file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFilesM4A[0].filepath)
        self.assertEqual(handler._audioFileType, 'm4a')

        # Test non-supported filetype given
        self.assertRaises(Exception, mlu.tags.io.AudioFileTagIOHandler, self.testData.notSupportedAudioFile)

    def testAudioFileTagIOHandlerFLAC(self):
        '''
        Tests tag reading/writing for a test FLAC file.
        '''
        for testAudioFile in self.testData.testAudioFilesFLAC:
            handler = mlu.tags.io.AudioFileTagIOHandler(testAudioFile.filepath)
            
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)
            
    def testAudioFileTagIOHandlerMp3(self):
        '''
        Tests tag reading/writing for a test Mp3 file.
        '''
        for testAudioFile in self.testData.testAudioFilesMp3:
            handler = mlu.tags.io.AudioFileTagIOHandler(testAudioFile.filepath)
            
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)

    def testAudioFileTagIOHandlerM4A(self):
        '''
        Tests tag reading/writing for a test M4A file.
        '''
        for testAudioFile in self.testData.testAudioFilesM4A:
            handler = mlu.tags.io.AudioFileTagIOHandler(testAudioFile.filepath)
            
            self._checkAudioFileTagIOHandlerRead(handler, testAudioFile.tagValues)
            self._checkAudioFileTagIOHandlerWrite(handler)

    def _checkAudioFileTagIOHandlerRead(self, audioFileTagIOHandler, expectedTagValues):
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
        tags = audioFileTagIOHandler.getTags()
        actualTagValues = tags.__dict__        

        # Check that the expected and actual tags data dictionaries are the same length
        self.assertEqual(len(expectedTagValues), len(actualTagValues))

        # Check that all the expected tags are in the returned tags
        for tagName in expectedTagValues:
            self.assertIn(tagName, actualTagValues)

        # Check that the expected and actual tags values match
        for tagName in expectedTagValues:
            expectedTagValue = expectedTagValues[tagName]
            actualTagValue = actualTagValues[tagName]

            if ((audioFileTagIOHandler._audioFileType == 'm4a') and (tagName == 'trackNumber' or tagName == 'totalTracks' or tagName == 'discNumber' or tagName == 'totalDiscs')):
                print('Skipping read test for unsupported tag for m4a file: {}'.format(tagName))
            else:
                self.assertEqual(expectedTagValue, actualTagValue)

    def _checkAudioFileTagIOHandlerWrite(self, audioFileTagIOHandler):
        '''
        Tests tag writing for any given test AudioFileTagIOHandler instance. Used as a 
        helper function.

        The test will check that new tag values can be written via the handler.

        Params:
            audioFileTagIOHandler: the handler instance to test (is defined with a test audio file type)
        '''
        tags = audioFileTagIOHandler.getTags()
        tagNames = tags.__dict__ 
        newTagValues = {}

        # Write the new tags
        for tagName in tagNames:
            if (tagName == 'date'):
                newTagValue = '2001'
            elif (tagName == 'trackNumber'):
                newTagValue = '4'
            elif (tagName == 'totalTracks'):
                newTagValue = '33'
            elif (tagName == 'discNumber'):
                newTagValue = '1'
            elif (tagName == 'totalDiscs'):
                newTagValue = '2'
            else:
                newTagValue = mlutest.common.getRandomString(length=100, allowDigits=True, allowUppercase=True, allowSpecial=True, allowSpace=True)
                newTagValue = newTagValue.replace('/', '')

            newTagValues[tagName] = newTagValue

        newAudioFileTags = mlu.tags.io.AudioFileTags(**newTagValues)
        audioFileTagIOHandler.setTags(newAudioFileTags)

        # Use the read test function to ensure the tags are now set to the new tag values 
        self._checkAudioFileTagIOHandlerRead(audioFileTagIOHandler, expectedTagValues=newTagValues)

