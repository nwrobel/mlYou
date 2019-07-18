import unittest
import json
import os
import datetime


# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import mlutest.envsetup
mlutest.envsetup.PreparePythonProjectEnvironment()


from mlu.cache.io import WriteMLUObjectsToJSONFile, ReadMLUObjectsFromJSONFile
from mlu.mpd.plays import SongPlaybackRecord
import mlu.common.file 


class TestCacheIOWriteObjectsToJson(unittest.TestCase):
    """
    Test case that tests the functions defined within the mlu.cache.io module.
    """

    def setUp(self):
        self.testJsonOutFilepath = mlu.common.file.JoinPaths(mlu.common.file.GetTestResourceFilesDirectory(), "testwrite.json")

    def tearDown(self):
        # os.remove(self.testJsonOutFilepath)
        pass

    # Test case helper functions -------------------------------------------------------------------
    def getSingleTestSongPlaybackRecord(self):
        return SongPlaybackRecord(
            songFilepath="C:\\songs\\artist\\song1.mp3",
            playbackTimes=[2425353456, 452345972, 32920224573, 49572439587]
        )

    # TODO - refactor this into a GetRandomTestSongPlaybackRecord() function, to generate entropy in test data
    # TODO - add records with some empty values
    def getMultipleTestSongPlaybackRecords(self):
        records = [
            SongPlaybackRecord(songFilepath="C:\\songs\\artist\\song1.mp3", playbackTimes=[2425333456, 462345972, 32950224573, 49562439587]),
            SongPlaybackRecord(songFilepath="/data/music/Nine Fall/03. Nine Fall - Observer.flac", playbackTimes=[2425333456, 462345972, 32950224573, 49562439587]),
            SongPlaybackRecord(songFilepath="C:\\songs\\art\\s1.mp3", playbackTimes=[2425333456, 462345972, 32950224573, 49562439587]),
            SongPlaybackRecord(songFilepath="C:\\songs\\t\\hi.mp3", playbackTimes=[2425333456, 462345972, 32950224573, 49562439587])
        ]
        return records

    def readTestJsonFile(self):
        with open(self.testJsonOutFilepath, 'r') as inputfile:
            results = json.load(inputfile)
        return results

    # Tests ----------------------------------------------------------------------------------------
    def testWriteSingleSongPlaybackRecordToJsonFile(self):
        playbackRecord = self.getSingleTestSongPlaybackRecord()
        WriteMLUObjectsToJSONFile(mluObjects=playbackRecord, outputFilepath=self.testJsonOutFilepath)
        jsonFileContent = self.readTestJsonFile()

        self.assertTrue(isinstance(jsonFileContent, dict))
        self.assertEqual(jsonFileContent['songFilepath'], playbackRecord.songFilepath)
        self.assertTrue(isinstance(jsonFileContent['playbackTimes'], list))
        self.assertEqual(jsonFileContent['playbackTimes'], playbackRecord.playbackTimes)

    def testWriteMultipleSongPlaybackRecordsToJsonFile(self):
        playbackRecords = self.getMultipleTestSongPlaybackRecords()
        WriteMLUObjectsToJSONFile(mluObjects=playbackRecords, outputFilepath=self.testJsonOutFilepath)
        jsonFileContent = self.readTestJsonFile()

        self.assertTrue(isinstance(jsonFileContent, list))

        for index, jsonDict in enumerate(jsonFileContent):
            self.assertTrue(isinstance(jsonDict, dict))
            self.assertEqual(jsonDict['songFilepath'], playbackRecords[index].songFilepath)
            self.assertTrue(isinstance(jsonDict['playbackTimes'], list))
            self.assertEqual(jsonDict['playbackTimes'], playbackRecords[index].playbackTimes)



class TestCacheIOReadObjectsFromJson(unittest.TestCase):
    """
    """    
    def setUp(self):
        self.testJsonInSingleFilepath = mlu.common.file.JoinPaths(mlu.common.file.GetTestResourceFilesDirectory(), "testreadsingle.json")
        self.testJsonInListFilepath = mlu.common.file.JoinPaths(mlu.common.file.GetTestResourceFilesDirectory(), "testreadlist.json")

    def testReadSingleSongPlaybackRecordFromJsonFile(self):
        playbackRecords = ReadMLUObjectsFromJSONFile(inputFilepath=self.testJsonInSingleFilepath, mluClassDefinition=SongPlaybackRecord)

        self.assertTrue(isinstance(playbackRecords, list))
        self.assertEqual(len(playbackRecords), 1)
        self.assertEqual(playbackRecords[0].songFilepath, "C:\\songs\\artist\\song1.mp3")
        self.assertEqual(playbackRecords[0].playbackTimes, [2425353456, 452345972, 32920224573, 49572439587])


    def testReadMultipleSongPlaybackRecordsFromJsonFile(self):
        pass


class TestCommonTimeFunctions(unittest.TestCase):
    """
    Test case that tests the functions defined within the mlu.common.time module.
    """


    def getCurrentTimestamp(self):
        dt = datetime.datetime.now()
        return datetime.datetime.timestamp(dt)



    def testFormatTimestampForDisplay(self):
        pass


class TestCommonFileFunctions(unittest.TestCase):
    """
    Test case that tests the functions defined within the mlu.common.file module.
    """
    def testGetProjectRoot(self):
        pass

    def testJoinPaths(self):
        pass


class TestMPDLogsModule(unittest.TestCase):
    """
    Test case that tests the classes and functions defined within the mlu.mpd.logs module.
    """
    pass


class TestMPDPlaysModule(unittest.TestCase):
    """
    Test case that tests the classes and functions defined within the mlu.mpd.plays module.
    """
    pass


class TestBasicTagsModule(unittest.TestCase):
    """
    Test case that tests the classes and functions defined within the mlu.tags.basic module.
    """
    pass


class TestPlaystatsTagsModule(unittest.TestCase):
    """
    Test case that tests the classes and functions defined within the mlu.tags.playstats module.
    """
    pass


class WholeIntegrationTest(unittest.TestCase):
    """
    Test case to test the entire MPD playstats tags update script, end to end. This is an integration
    test, not a unit test, and it utilizes all the modules the script uses. The script is executed
    as it would be normally, but this test case checks the results against expected results to verify 
    accuracy after setting up input test data.
    """
    pass


def GetMPDPlaystatsTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestCacheIOWriteObjectsToJson())
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(GetMPDPlaystatsTestSuite())





