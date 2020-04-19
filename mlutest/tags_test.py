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
    This data consists of the test audio filepaths and the important 'actual' tag values for each
    file.
    '''
    def __init__(self, testAudioFileDir):
        self.testAudioFileFLAC = TestAudioFile(
            filepath=mlu.common.file.JoinPaths(testAudioFileDir, 'test.flac'),
            tagValues={
                'TITLE': 'Suck It Up',
                'ARTIST': '(hed) Planet Earth',
                'ALBUMARTIST': '(hed) Planet Earth',
                'ALBUM': 'The Best Of (Hed) Planet Earth',
                'DATE': '2006',
                'GENRE': 'Hip Hop;Rock;Reggae;Alternative Rock;Nu Metal',
                'TRACKNUMBER': '01',
                'TOTALTRACKS': '15',
                'DISCNUMBER': '1',
                'TOTALDISCS': '1',
                'DATE_ADDED': '2018-02-01 21:11:19',
                'BPM': '91',
                'RATING': '5'
            }
        )

        self.testAudioFileMP3 = TestAudioFile(
            filepath=mlu.common.file.JoinPaths(testAudioFileDir, 'test.mp3'),
            tagValues={
                'TITLE': 'Sarod',
                'ARTIST': 'The Derek Trucks Band',
                'ALBUMARTIST': 'The Derek Trucks Band',
                'ALBUM': 'The Derek Trucks Band',
                'DATE': '1997',
                'GENRE': 'Rock;Jazz',
                'TRACKNUMBER': '1',
                'TOTALTRACKS': '12',
                'DISCNUMBER': '1',
                'TOTALDISCS': '2',
                'DATE_ADDED': '2019-02-21 16:06:02',
                'BPM': '120',
                'RATING': '7.1',
                'VOTES': '6;8'
            }
        )

        self.testAudioFileM4A = TestAudioFile(
            filepath=mlu.common.file.JoinPaths(testAudioFileDir, 'test.m4a'),
            tagValues={
                'TITLE': 'title ddg',
                'ARTIST': 'Ambient Occlusion',
                'ALBUMARTIST': 'Ambient Occlu',
                'ALBUM': 'Youtube stuff',
                'DATE': '2017',
                'GENRE': 'Psychill',
                'TRACKNUMBER': '3',
                'TOTALTRACKS': '20',
                'DISCNUMBER': '1',
                'TOTALDISCS': '2',
                'DATE_ADDED': '2018-12-20 20:52:48',
                'BPM': '195',
                'RATING': '8.5',
                'VOTES': '8;9;10'
            }
        )   

        self.notSupportedAudioFile = "{}.ogg".format(mlutest.common.getRandomFilepath())
        self.notExistFile = mlutest.common.getRandomFilepath()

        self.jdict = mlu.common.file.getDictFromJsonFile("D:\\Temp\\mlu-test\\test-audio-filetypes\\tags.json")

class TestTagsIOModule(unittest.TestCase):
    def setUp(self):
        '''
        Sets up the test data for the tests of the tags.io module. The test audio files are copied
        from the test resource dir to the mlu cache dir, where they will be manipulated by the tests
        while preserving the original test data files.
        '''
        testResDir = mlu.common.file.getTestResourceFilesDirectory()
        testSrcAudioFilesDir = mlu.common.file.JoinPaths(testResDir, 'test-audio-filetypes')
        cacheDir = mlu.common.file.getMLUCacheDirectory()

        testSrcAudioFiles = mlu.common.file.GetAllFilesDepth1(rootPath=testSrcAudioFilesDir)
        mlu.common.file.CopyFilesToDirectory(srcFiles=testSrcAudioFiles, destDir=cacheDir)

        self.testData = TestData(testAudioFileDir=cacheDir)

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


    def testAudioFileTagIOHandlerFLAC(self):
        '''
        Tests tag reading/writing for a test FLAC file.
        '''
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileFLAC.filepath)

        # Test tag reading: defined tags
        for tagName in self.testData.testAudioFileFLAC.tagValues:
            expectedTagValue = self.testData.testAudioFileFLAC.tagValues[tagName]
            actualTagValue = handler.getAudioTagValue(tagName)

            self.assertEqual(actualTagValue, expectedTagValue)

        # Test tag reading: undefined tags
        for x in range(100):
            testUndefinedTagName = mlutest.common.getRandomString(length=30, allowSpace=True)
            actualTagValue = handler.getAudioTagValue(testUndefinedTagName)
            self.assertEqual(actualTagValue, '')

        # Test tag writing: existing tags
        for tagName in self.testData.testAudioFileFLAC.tagValues:
            testTagValue = mlutest.common.getRandomString(allowDigits=True, allowSpecial=True, allowSpace=True, allowUppercase=True)
            handler.setAudioTagValue(tagName, testTagValue)
            actualTagValue = handler.getAudioTagValue(tagName)

            self.assertEqual(actualTagValue, testTagValue)
        
        # Test tag writing: new tags
        for x in range(100):
            testUndefinedTagName = mlutest.common.getRandomString(length=30, allowSpace=True)
            testTagValue = mlutest.common.getRandomString(allowDigits=True, allowSpecial=True, allowSpace=True, allowUppercase=True)

            handler.setAudioTagValue(testUndefinedTagName, testTagValue)
            actualTagValue = handler.getAudioTagValue(testUndefinedTagName)

            self.assertEqual(actualTagValue, testTagValue)

    def testAudioFileTagIOHandlerMp3(self):
        '''
        Tests tag reading/writing for a test MP3 file.
        '''
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testData.testAudioFileMP3.filepath)

        # Test tag reading: defined tags
        for tagName in self.testData.testAudioFileMP3.tagValues:
            expectedTagValue = self.testData.testAudioFileMP3.tagValues[tagName]
            actualTagValue = handler.getAudioTagValue(tagName)

            self.assertEqual(actualTagValue, expectedTagValue)

        # Test tag reading: undefined tags
        for x in range(100):
            testUndefinedTagName = mlutest.common.getRandomString(length=30, allowSpace=True)
            actualTagValue = handler.getAudioTagValue(testUndefinedTagName)
            self.assertEqual(actualTagValue, '')

        # Test tag writing: existing tags
        for tagName in self.testData.testAudioFileMP3.tagValues:
            testTagValue = mlutest.common.getRandomString(allowDigits=True, allowSpecial=True, allowSpace=True, allowUppercase=True)
            handler.setAudioTagValue(tagName, testTagValue)
            actualTagValue = handler.getAudioTagValue(tagName)

            self.assertEqual(actualTagValue, testTagValue)
        
        # Test tag writing: new tags
        for x in range(100):
            testUndefinedTagName = mlutest.common.getRandomString(length=30, allowSpace=True)
            testTagValue = mlutest.common.getRandomString(allowDigits=True, allowSpecial=True, allowSpace=True, allowUppercase=True)

            handler.setAudioTagValue(testUndefinedTagName, testTagValue)
            actualTagValue = handler.getAudioTagValue(testUndefinedTagName)

            self.assertEqual(actualTagValue, testTagValue)

    def testAudioFileTagIOHandlerAAC(self):
        '''
        Tests tag reading/writing for a test M4A file.
        '''
        # Test tag reading: defined standard tag
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testAudioFilepathAAC)
        actualValue = handler.getAudioTagValue('title')
        expectedValue = 'Dense - Percussive Candies [ambient/chillout/psychedelic]'
        # self.assertEqual(actualValue, expectedValue)

        # Test reading: defined custom (nonstandard) tag
        actualValue = handler.getAudioTagValue('date_added')
        expectedValue = '2018-12-20 20:52:48'
        self.assertEqual(actualValue, expectedValue)

        # Test tag reading: undefined standard tag
        actualValue = handler.getAudioTagValue('copyright')
        self.assertEqual(actualValue, '')

        # Test tag reading: undefined custom tag
        actualValue = handler.getAudioTagValue('undefined_tag')
        self.assertEqual(actualValue, '')

        # Test tag writing: an existing tag
        testValue = 'title ddg'
        handler.setAudioTagValue('title', testValue)
        actualValue = handler.getAudioTagValue('title')
        self.assertEqual(actualValue, testValue)

        # Test tag writing: track/disc numbers, total tracks/discs
        testValueTrackNum = '3'
        testValueTotalTracks = '20'
        testValueDiscNum = '1'
        testValueTotalDiscs = '2'
        handler.setAudioTagValue('TRACKNUMBER', testValueTrackNum)
        handler.setAudioTagValue('TOTALTRACKS', testValueTotalTracks)
        handler.setAudioTagValue('DISCNUMBER', testValueDiscNum)
        handler.setAudioTagValue('TOTALDISCS', testValueTotalDiscs)

        actualValue = handler.getAudioTagValue('TRACKNUMBER')
        self.assertEqual(actualValue, testValueTrackNum)

        actualValue = handler.getAudioTagValue('TOTALTRACKS')
        self.assertEqual(actualValue, testValueTotalTracks)

        actualValue = handler.getAudioTagValue('DISCNUMBER')
        self.assertEqual(actualValue, testValueDiscNum)

        actualValue = handler.getAudioTagValue('TOTALDISCS')
        self.assertEqual(actualValue, testValueTotalDiscs)

        # Test tag writing: a new tag
        testValue = 'tag val asdf'
        handler.setAudioTagValue('tag_name', testValue)
        actualValue = handler.getAudioTagValue('tag_name')
        self.assertEqual(actualValue, testValue)

