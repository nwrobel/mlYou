import unittest

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import mlu.tags.io
import mlutest.common

class TestAudioFile:
    def __init__(self, filepath, tagValues):
        self.filepath = filepath
        self.tagValues = tagValues

class TestData:
    def __init__(self, testAudioFileDir):
        

    class FLAC:
        filepath = 'test.flac'
        tagValue = {}
    class MP3:
        filepath = 'test.mp3'
        tagValue = {}
    class M4A:
        filepath = 'test.m4a'
        tagValue = {}    

class TestTagsIOModule(unittest.TestCase):
    def setUp(self):
        self.testAudioFilepathFLAC = "D:\\Temp\mlu-test\\"
        self.testAudioFilepathMp3 = "D:\\Temp\mlu-test\\test-music-lib\\Content\\Music\\Derek Trucks And Co\\The Derek Trucks Band\\1997 - The Derek Trucks Band (320 kbps)\\01 - Sarod.mp3"
        self.testAudioFilepathAAC = "D:\\Temp\\mlu-test\\test-music-lib\\Content\\Music\\Ambient Occlusion\\Dense - Percussive Candies [ambient_chillout_psychedelic].m4a"
        self.testAudioFileALAC = "D:\\Temp\\mlu-test\\test-music-lib\\Content\\Music\\Buckethead [ALAC]\\Studio albums\\[1992]Bucketheadland\\CD1\\01. Buckethead - Intro- Park Theme.m4a"
        self.notExistFile = 'D:\\hello.mp3'
        
        testResDir = mlu.common.file.getTestResourceFilesDirectory()
        testSrcAudioFilesDir = mlu.common.file.JoinPaths(testResDir, 'test-audio-filetypes')
        cacheDir = mlu.common.file.getMLUCacheDirectory()

        testSrcAudioFiles = [, , ]
        testSrcAudioFilepaths = [mlu.common.file.JoinPaths(testSrcAudioFilesDir, audioFile) for audioFile in testSrcAudioFiles]

        mlu.common.file.CopyFilesToDirectory(srcFiles=testSrcAudioFilepaths, destDir=cacheDir)

        self.testData = TestData

    def testAudioFileTagIOHandlerConstructor(self):
        # Test nonexisting file given
        self.assertRaises(ValueError, mlu.tags.io.AudioFileTagIOHandler, self.notExistFile)

        # Test FLAC file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testAudioFilepathFLAC)
        self.assertEqual(handler.audioFileType, 'flac')

        # Test MP3 file given
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testAudioFilepathMp3)
        self.assertEqual(handler.audioFileType, 'mp3')

        # Test non-supported filetype given
        self.assertRaises(ValueError, mlu.tags.io.AudioFileTagIOHandler, self.testAudioFileALAC)


    def testAudioFileTagIOHandlerFLAC(self):
        # Test tag reading: defined tag
        handler = mlu.tags.io.AudioFileTagIOHandler(self.testAudioFilepathFLAC)
        actualValue = handler.getAudioTagValue('title')
        expectedValue = 'Intro- Park Theme'
        self.assertEqual(actualValue, expectedValue)

        # Test tag reading: undefined tag
        actualValue = handler.getAudioTagValue('undefined_tag')
        self.assertEqual(actualValue, '')

        # Test tag writing
        testValue = 'asdf'
        handler.setAudioTagValue('tag_name', testValue)
        
        actualValue = handler.getAudioTagValue('tag_name')
        self.assertEqual(actualValue, testValue)

    def testAudioFileTagIOHandlerMp3(self):
        tag1Start = handler.getAudioTagValue('title')
        tag2Start = handler.getAudioTagValue('copyright')
        tag3Start = handler.getAudioTagValue('play_count')
        tag4Start = handler.getAudioTagValue('undefined_tag')

    def testAudioFileTagIOHandlerAAC(self):
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

