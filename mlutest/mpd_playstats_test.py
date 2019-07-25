import unittest
import json
import os

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.cache.io import WriteMLUObjectsToJSONFile, ReadMLUObjectsFromJSONFile
from mlu.mpd.plays import SongPlaybackRecord
from mlu.tags.playstats import SongPlaystatTags
from mlu.mpd.logs import MPDLogLine
import mlu.common.file 
import mlutest.common


class TestCacheIOWriteMLUObjectsToJSONFile(unittest.TestCase):
    """
    Test case that tests the function "WriteMLUObjectsToJSONFile" of the mlu.cache.io module.
    Ensure that we can write out one or more instances of different MLU objects to JSON accurately
    and as expected. This is not a test for these object classes: just for this cache function.

    Each test function follows the following structure:
    Setup
    - Define random test data and use it to create pre-made objects 
    - Define test filepath for json file to be written to
    
    Test run
    - Write out json file from test objects
    - Use json.load to read output data from json file into dict data structures
    - check that each dict matches the properties for each test object 
    
    Teardown
    - Delete test json output file

    Do this test for the following MLU object types - for each type, one test for writing a single 
    object instance and one test for writing multiple object instances:
        SongPlaybackRecord, SongPlaystatTags, MPDLogLine    
    """
    # -----------------------------Test case helper functions --------------------------------------
    def setUp(self):
        self.testJsonFilepath = mlu.common.file.JoinPaths(mlu.common.file.GetTestResourceFilesDirectory(), "testwrite.json")

    def tearDown(self):
        os.remove(self.testJsonFilepath)

    def getTestSongPlaybackRecord(self):
        # Use  the mlutest.common functions to generate random test data to make the test instance
        filepath = mlutest.common.getRandomFilepath()
        numPlaybackTimes = mlutest.common.getRandomNumber(min=1, max=100)
        playbackTimes = [mlutest.common.getRandomTimestamp() for x in range(numPlaybackTimes)]
        return SongPlaybackRecord(songFilepath=filepath, playbackTimes=playbackTimes)

    def getTestSongPlaystatTags(self):
        filepath = mlutest.common.getRandomFilepath()
        playCount = mlutest.common.getRandomNumber(min=1, max=100)
        timeLastPlayed = mlutest.common.getRandomTimestamp()
        allTimesPlayed = [mlutest.common.getRandomTimestamp() for x in range(playCount - 1)]
        return SongPlaystatTags(songFilepath=filepath, playCount=playCount, timeLastPlayed=timeLastPlayed, allTimesPlayed=allTimesPlayed)

    def getTestMPDLogLine(self):
        text = mlutest.common.getRandomString(length=120, allowDigits=True, allowUppercase=True, allowSpecial=True, allowSpace=True)
        timestamp = mlutest.common.getRandomTimestamp()
        return MPDLogLine(text=text, timestamp=timestamp)

    def readTestJsonFile(self):
        with open(self.testJsonFilepath, 'r') as inputfile:
            results = json.load(inputfile)
        return results

    # Tests ----------------------------------------------------------------------------------------

    def testWriteSingleMLUObjectToJSONFileFile_SongPlaybackRecord(self):
        # Generate test object instance: SongPlaybackRecord
        playbackRecord = self.getTestSongPlaybackRecord()

        # Run the code: write this object to the test json filepath
        WriteMLUObjectsToJSONFile(mluObjects=playbackRecord, outputFilepath=self.testJsonFilepath)

        # Check - output file should exist
        self.assertTrue(mlu.common.file.FileExists(self.testJsonFilepath))
        # Read Results - read in the expected data from the test json output file
        jsonFileContent = self.readTestJsonFile()

        # Check - compare actual to expected data
        self.assertTrue(isinstance(jsonFileContent, dict))
        self.assertEqual(jsonFileContent['songFilepath'], playbackRecord.songFilepath)
        self.assertTrue(isinstance(jsonFileContent['playbackTimes'], list))
        self.assertEqual(jsonFileContent['playbackTimes'], playbackRecord.playbackTimes)


    def testWriteSingleMLUObjectToJSONFile_SongPlaystatTags(self):
        playstatTags = self.getTestSongPlaystatTags()
        WriteMLUObjectsToJSONFile(mluObjects=playstatTags, outputFilepath=self.testJsonFilepath)

        self.assertTrue(mlu.common.file.FileExists(self.testJsonFilepath))
        jsonFileContent = self.readTestJsonFile()

        # Check - compare actual to expected data
        self.assertTrue(isinstance(jsonFileContent, dict))
        self.assertEqual(jsonFileContent['songFilepath'], playstatTags.songFilepath)
        self.assertEqual(jsonFileContent['playCount'], playstatTags.playCount)
        self.assertEqual(jsonFileContent['timeLastPlayed'], playstatTags.timeLastPlayed)
        self.assertTrue(isinstance(jsonFileContent['allTimesPlayed'], list))
        self.assertEqual(jsonFileContent['allTimesPlayed'], playstatTags.allTimesPlayed)


    def testWriteSingleMLUObjectToJSONFile_MPDLogLine(self):
        mpdlogLine = self.getTestMPDLogLine()
        WriteMLUObjectsToJSONFile(mluObjects=mpdlogLine, outputFilepath=self.testJsonFilepath)

        self.assertTrue(mlu.common.file.FileExists(self.testJsonFilepath))
        jsonFileContent = self.readTestJsonFile()

        # Check - compare actual to expected data
        self.assertTrue(isinstance(jsonFileContent, dict))
        self.assertEqual(jsonFileContent['text'], mpdlogLine.text)
        self.assertEqual(jsonFileContent['timestamp'], mpdlogLine.timestamp)


    def testWriteMultipleMLUObjectsToJSONFile_SongPlaybackRecord(self):
        # Create a random number (at least 2, no more than 40) of test objects
        numTestObjects = mlutest.common.getRandomNumber(min=2, max=40)
        playbackRecords = [self.getTestSongPlaybackRecord() for x in range(numTestObjects)]

        # Run the test code to write out the list of objects
        WriteMLUObjectsToJSONFile(mluObjects=playbackRecords, outputFilepath=self.testJsonFilepath)

        # Check - ensure output file exists
        self.assertTrue(mlu.common.file.FileExists(self.testJsonFilepath))
        # Read in the resulting output json file
        jsonFileContent = self.readTestJsonFile()

        # Check - compare results to what is expected
        self.assertTrue(isinstance(jsonFileContent, list))

        for index, jsonDict in enumerate(jsonFileContent):
            self.assertTrue(isinstance(jsonDict, dict))
            self.assertEqual(jsonDict['songFilepath'], playbackRecords[index].songFilepath)
            self.assertTrue(isinstance(jsonDict['playbackTimes'], list))
            self.assertEqual(jsonDict['playbackTimes'], playbackRecords[index].playbackTimes)


    def testWriteMultipleMLUObjectsToJSONFile_SongPlaystatTags(self):
        # Create a random number (at least 2, no more than 40) of test objects
        numTestObjects = mlutest.common.getRandomNumber(min=2, max=40)
        songsPlaystatTags = [self.getTestSongPlaystatTags() for x in range(numTestObjects)]

        # Run the test code to write out the list of objects
        WriteMLUObjectsToJSONFile(mluObjects=songsPlaystatTags, outputFilepath=self.testJsonFilepath)

        # Check - ensure output file exists
        self.assertTrue(mlu.common.file.FileExists(self.testJsonFilepath))
        # Read in the resulting output json file
        jsonFileContent = self.readTestJsonFile()

        # Check - compare results to what is expected
        self.assertTrue(isinstance(jsonFileContent, list))

        for index, jsonDict in enumerate(jsonFileContent):
            self.assertTrue(isinstance(jsonDict, dict))
            self.assertEqual(jsonDict['songFilepath'], songsPlaystatTags[index].songFilepath)
            self.assertEqual(jsonDict['playCount'], songsPlaystatTags[index].playCount)
            self.assertEqual(jsonDict['timeLastPlayed'], songsPlaystatTags[index].timeLastPlayed)
            self.assertTrue(isinstance(jsonDict['allTimesPlayed'], list))
            self.assertEqual(jsonDict['allTimesPlayed'], songsPlaystatTags[index].allTimesPlayed)


    def testWriteMultipleMLUObjectsToJSONFile_MPDLogLine(self):
        # Create a random number (at least 2, no more than 40) of test objects
        numTestObjects = mlutest.common.getRandomNumber(min=2, max=40)
        mpdlogLines = [self.getTestMPDLogLine() for x in range(numTestObjects)]

        # Run the test code to write out the list of objects
        WriteMLUObjectsToJSONFile(mluObjects=mpdlogLines, outputFilepath=self.testJsonFilepath)

        # Check - ensure output file exists
        self.assertTrue(mlu.common.file.FileExists(self.testJsonFilepath))
        # Read in the resulting output json file
        jsonFileContent = self.readTestJsonFile()

        # Check - compare results to what is expected
        self.assertTrue(isinstance(jsonFileContent, list))

        for index, jsonDict in enumerate(jsonFileContent):
            self.assertTrue(isinstance(jsonDict, dict))
            self.assertEqual(jsonDict['text'], mpdlogLines[index].text)
            self.assertEqual(jsonDict['timestamp'], mpdlogLines[index].timestamp)


class TestCacheIOReadMLUObjectsFromJSONFile(unittest.TestCase):
    """
    Test case that tests the function "ReadMLUObjectsFromJSONFile" of the mlu.cache.io module.
    Ensure that we can read JSON files containing one or more serialized MLU object instances of 
    different types, and that the correct objects are created accurately and as expected. 
    This is not a test for these object classes: just for the cache function.

    Each test function follows the following structure:
    Setup
    - Use Random functions to create random test data needed tp populate the properties of the given
      object type
    - Save this data in key-value dictionaries, each dict represents an instance
    - use json.dump to write these dicts to the test input json file
    
    Test run
    - read in the test json file and serialize it a list of 1 or more objects
    - check that each object's attributes match each test data dict's values test data
    
    Teardown
    - Delete test json output file

    Do this test for the following MLU object types - for each type, one test for reading a Json file 
    containing a single object instance, and one test for reading a Json file containing multiple object instances:
        SongPlaybackRecord, SongPlaystatTags, MPDLogLine   
    """ 
    # ------------------------------- Test Case Helper functions -----------------------------------

    def setUp(self):
        self.testJsonFilepath = mlu.common.file.JoinPaths(mlu.common.file.GetTestResourceFilesDirectory(), "testread.json")

    def tearDown(self):
        os.remove(self.testJsonFilepath)

    def getTestJSONFormattedSongPlaybackRecord(self):
        jsonDict = {}
        jsonDict['songFilepath'] = mlutest.common.getRandomFilepath()
        numPlaybackTimes = mlutest.common.getRandomNumber(min=1, max=100)
        jsonDict['playbackTimes'] = [mlutest.common.getRandomTimestamp() for x in range(numPlaybackTimes)]
        return jsonDict

    def getTestJSONFormattedSongPlaystatTags(self):
        jsonDict = {}
        jsonDict['songFilepath'] = mlutest.common.getRandomFilepath()
        jsonDict['playCount'] = mlutest.common.getRandomNumber(min=1, max=100)
        jsonDict['timeLastPlayed'] = mlutest.common.getRandomTimestamp()
        jsonDict['allTimesPlayed'] = [mlutest.common.getRandomTimestamp() for x in range(jsonDict['playCount'] - 1)]
        return jsonDict

    def getTestJSONFormattedMPDLogLine(self):
        jsonDict = {}
        jsonDict['text'] = mlutest.common.getRandomString(length=120, allowDigits=True, allowUppercase=True, allowSpecial=True, allowSpace=True)
        jsonDict['timestamp'] = mlutest.common.getRandomTimestamp()
        return jsonDict
    
    def writeTestJsonFile(self, jsonContent):
        with open(self.testJsonFilepath, 'w+') as outputFile:
            json.dump(jsonContent, outputFile)

    # ---------------------------------- Test Functions --------------------------------------------

    def testReadSingleMLUObjectFromJsonFile_SongPlaybackRecord(self):
        # Create test data from random sources and write this data to a test json file that will 
        # be used for input to the ReadJson function
        playbackRecordJsonContent = self.getTestJSONFormattedSongPlaybackRecord()
        self.writeTestJsonFile(jsonContent=playbackRecordJsonContent)

        # Run the test code to read in the json and serialize it into a list of one or more objects of type
        playbackRecords = ReadMLUObjectsFromJSONFile(inputFilepath=self.testJsonFilepath, mluClassDefinition=SongPlaybackRecord)

        # Check results of the objects read in and compare each object's properties to those of the 
        # original test data
        self.assertTrue(isinstance(playbackRecords, list))
        self.assertEqual(len(playbackRecords), 1)
        self.assertEqual(playbackRecords[0].songFilepath, playbackRecordJsonContent['songFilepath'])
        self.assertEqual(playbackRecords[0].playbackTimes, playbackRecordJsonContent['playbackTimes'])


    def testReadSingleMLUObjectFromJsonFile_SongPlaystatTags(self):
        # Create test data from random sources and write this data to a test json file that will 
        # be used for input to the ReadJson function
        playstatTagsJsonContent = self.getTestJSONFormattedSongPlaystatTags()
        self.writeTestJsonFile(jsonContent=playstatTagsJsonContent)

        # Run the test code to read in the json and serialize it into a list of one or more objects of type
        playstatTags = ReadMLUObjectsFromJSONFile(inputFilepath=self.testJsonFilepath, mluClassDefinition=SongPlaystatTags)

        # Check results of the objects read in and compare each object's properties to those of the 
        # original test data
        self.assertTrue(isinstance(playstatTags, list))
        self.assertEqual(len(playstatTags), 1)
        self.assertEqual(playstatTags[0].songFilepath, playstatTagsJsonContent['songFilepath'])
        self.assertEqual(playstatTags[0].playCount, playstatTagsJsonContent['playCount'])
        self.assertEqual(playstatTags[0].timeLastPlayed, playstatTagsJsonContent['timeLastPlayed'])
        self.assertTrue(isinstance(playstatTags[0].allTimesPlayed, list))
        self.assertEqual(playstatTags[0].allTimesPlayed, playstatTagsJsonContent['allTimesPlayed'])


    def testReadSingleMLUObjectFromJsonFile_MPDLogLine(self):
        # Create test data from random sources and write this data to a test json file that will 
        # be used for input to the ReadJson function
        mpdlogLineJsonContent = self.getTestJSONFormattedMPDLogLine()
        self.writeTestJsonFile(jsonContent=mpdlogLineJsonContent)

        # Run the test code to read in the json and serialize it into a list of one or more objects of type
        mpdlogLine = ReadMLUObjectsFromJSONFile(inputFilepath=self.testJsonFilepath, mluClassDefinition=MPDLogLine)

        # Check results of the objects read in and compare each object's properties to those of the 
        # original test data
        self.assertTrue(isinstance(mpdlogLine, list))
        self.assertEqual(len(mpdlogLine), 1)
        self.assertEqual(mpdlogLine[0].text, mpdlogLineJsonContent['text'])
        self.assertEqual(mpdlogLine[0].timestamp, mpdlogLineJsonContent['timestamp'])


    def testReadMultipleMLUObjectsFromJsonFile_SongPlaybackRecord(self):
        # Create test data from random sources and write this data to a test json file that will 
        # be used for input to the ReadJson function
        # Get a random number for the number of MLU objects we should setup as JSON format for the test
        numTestObjects = mlutest.common.getRandomNumber(min=2, max=40)
        playbackRecordsJsonContent = [self.getTestJSONFormattedSongPlaybackRecord() for x in range(numTestObjects)]
        self.writeTestJsonFile(jsonContent=playbackRecordsJsonContent)

        # Run the test code to read in the json and serialize it into a list of one or more objects of type
        playbackRecords = ReadMLUObjectsFromJSONFile(inputFilepath=self.testJsonFilepath, mluClassDefinition=SongPlaybackRecord)

        # Check results of the objects read in and compare each object's properties to those of the 
        # original test data
        self.assertTrue(isinstance(playbackRecords, list))
        self.assertEqual(len(playbackRecords), numTestObjects)

        for index, playbackRecord in enumerate(playbackRecords):
            self.assertEqual(playbackRecord.songFilepath, playbackRecordsJsonContent[index]['songFilepath'])
            self.assertEqual(playbackRecord.playbackTimes, playbackRecordsJsonContent[index]['playbackTimes'])


    def testReadMultipleMLUObjectsFromJsonFile_SongPlaystatTags(self):
        # Create test data from random sources and write this data to a test json file that will 
        # be used for input to the ReadJson function
        # Get a random number for the number of MLU objects we should setup as JSON format for the test
        numTestObjects = mlutest.common.getRandomNumber(min=2, max=40)
        songsPlaystatTagsJsonContent = [self.getTestJSONFormattedSongPlaystatTags() for x in range(numTestObjects)]
        self.writeTestJsonFile(jsonContent=songsPlaystatTagsJsonContent)

        # Run the test code to read in the json and serialize it into a list of one or more objects of type
        songsPlaystatTags = ReadMLUObjectsFromJSONFile(inputFilepath=self.testJsonFilepath, mluClassDefinition=SongPlaystatTags)

        # Check results of the objects read in and compare each object's properties to those of the 
        # original test data
        self.assertTrue(isinstance(songsPlaystatTags, list))
        self.assertEqual(len(songsPlaystatTags), numTestObjects)

        for index, playstatTag in enumerate(songsPlaystatTags):
            self.assertEqual(playstatTag.songFilepath, songsPlaystatTagsJsonContent[index]['songFilepath'])
            self.assertEqual(playstatTag.playCount, songsPlaystatTagsJsonContent[index]['playCount'])
            self.assertEqual(playstatTag.timeLastPlayed, songsPlaystatTagsJsonContent[index]['timeLastPlayed'])
            self.assertTrue(isinstance(playstatTag.allTimesPlayed, list))
            self.assertEqual(playstatTag.allTimesPlayed, songsPlaystatTagsJsonContent[index]['allTimesPlayed']) 


    def testReadMultipleMLUObjectsFromJsonFile_MPDLogLine(self):
        # Create test data from random sources and write this data to a test json file that will 
        # be used for input to the ReadJson function
        # Get a random number for the number of MLU objects we should setup as JSON format for the test
        numTestObjects = mlutest.common.getRandomNumber(min=2, max=40)
        mpdLogLinesJsonContent = [self.getTestJSONFormattedMPDLogLine() for x in range(numTestObjects)]
        self.writeTestJsonFile(jsonContent=mpdLogLinesJsonContent)

        # Run the test code to read in the json and serialize it into a list of one or more objects of type
        mpdlogLines = ReadMLUObjectsFromJSONFile(inputFilepath=self.testJsonFilepath, mluClassDefinition=MPDLogLine)

        # Check results of the objects read in and compare each object's properties to those of the 
        # original test data
        self.assertTrue(isinstance(mpdlogLines, list))
        self.assertEqual(len(mpdlogLines), numTestObjects)

        for index, mpdlogLine in enumerate(mpdlogLines):
            self.assertEqual(mpdlogLine.text, mpdLogLinesJsonContent[index]['text'])
            self.assertEqual(mpdlogLine.timestamp, mpdLogLinesJsonContent[index]['timestamp'])                       


class TestCommonTimeFunctions(unittest.TestCase):
    """
    Test case that tests the functions defined within the mlu.common.time module.
    """
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
    # Test the common modules in MLU first, since other tests sometimes use the functions within them
    # If the tests pass for the common modules, we can assume that the tests for other modules are valid
    # If tests fail for common modules, stop the test execution b/c dependent tests will be affected
    suite = unittest.TestSuite()
    suite.addTest(TestCacheIOWriteMLUObjectsToJSONFile())
    suite.addTest(TestCacheIOReadMLUObjectsFromJSONFile())
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(GetMPDPlaystatsTestSuite())





