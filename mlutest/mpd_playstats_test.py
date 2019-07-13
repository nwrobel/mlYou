import unittest
import json
import os

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import mlutest.envsetup
mlutest.envsetup.PreparePythonProjectEnvironment()

from mlu.cache.io import WriteMLUObjectsToJSONFile, ReadMLUObjectsFromJSONFile
from mlu.mpd.plays import SongPlaybackRecord

class TestCacheFunctions(unittest.TestCase):

    def setUp(self):
        self.testJsonFilepath = 'D:\\Temp\\mlu-test\\test.json'

    def tearDown(self):
        os.remove(self.testJsonFilepath)

    # Test case helper functions -------------------------------------------------------------------
    def getSingleTestSongPlaybackRecord(self):
        return SongPlaybackRecord(
            songFilepath="C:\\songs\\artist\\song1.mp3",
            playbackTimes=[2425353456, 452345972, 32920224573, 49572439587]
        )

    def getMultipleTestSongPlaybackRecords(self):
        records = [
            SongPlaybackRecord(songFilepath="C:\\songs\\artist\\song1.mp3", playbackTimes=[2425333456, 462345972, 32950224573, 49562439587]),
            SongPlaybackRecord(songFilepath="C:\\songs\\artist\\song2.mp3", playbackTimes=[2425333456, 462345972, 32950224573, 49562439587]),
            SongPlaybackRecord(songFilepath="C:\\songs\\art\\s1.mp3", playbackTimes=[2425333456, 462345972, 32950224573, 49562439587]),
            SongPlaybackRecord(songFilepath="C:\\songs\\t\\hi.mp3", playbackTimes=[2425333456, 462345972, 32950224573, 49562439587])
        ]
        return records

    def readTestJsonFile(self):
        with open(self.testJsonFilepath, 'r') as inputfile:
            results = json.load(inputfile)
        return results

    # Tests ----------------------------------------------------------------------------------------
    def testWriteSingleSongPlaybackRecordToJsonFile(self):
        playbackRecord = self.getSingleTestSongPlaybackRecord()
        WriteMLUObjectsToJSONFile(mluObjects=playbackRecord, outputFilepath=self.testJsonFilepath)
        jsonFileContent = self.readTestJsonFile()

        self.assertTrue(isinstance(jsonFileContent, dict))
        self.assertEqual(jsonFileContent['songFilepath'], playbackRecord.songFilepath)
        self.assertTrue(isinstance(jsonFileContent['playbackTimes'], list))
        self.assertEqual(jsonFileContent['playbackTimes'], playbackRecord.playbackTimes)

    def testWriteMultipleSongPlaybackRecordsToJsonFile(self):
        playbackRecords = self.getMultipleTestSongPlaybackRecords()
        WriteMLUObjectsToJSONFile(mluObjects=playbackRecords, outputFilepath=self.testJsonFilepath)
        jsonFileContent = self.readTestJsonFile()

        self.assertTrue(isinstance(jsonFileContent, list))

        for index, jsonDict in enumerate(jsonFileContent):
            self.assertEqual(jsonDict['songFilepath'], playbackRecords[index].songFilepath)
            self.assertTrue(isinstance(jsonDict['playbackTimes'], list))
            self.assertEqual(jsonDict['playbackTimes'], playbackRecords[index].playbackTimes)



def MPDPlaystatsTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestCacheFunctions())
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(MPDPlaystatsTestSuite())





