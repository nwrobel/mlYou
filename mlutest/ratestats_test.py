'''
Tests for mlu.ratestats

Date last passed: 12/20/20

'''
import unittest

# Do setup processing so that this script can import all the needed modules from package "mlutest"
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.settings import MLUSettings

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.logger

mypycommons.logger.initSharedLogger(logDir=MLUSettings.logDir)

import mlutest.common
import mlu.ratestats
import mlu.tags.common

class TestRatestatsModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        '''
        Sets up the test data for the tests of the tags.io module. The test audio files are copied
        from the test resource dir to the mlu cache dir, where they will be manipulated by the tests
        while preserving the original test data files.
        '''
        super(TestRatestatsModule, self).setUpClass        

        self.testDataTempDir = MLUSettings.testDataGenTempDir

        # copy the test audio files from the static test files dir to the temp cache test files dir
        # also copy the tags.json file
        testAudioFilesSrc = mypycommons.file.GetAllFilesRecursive(MLUSettings.testDataStaticAudioFilesDir)
        mypycommons.file.CopyFilesToDirectory(srcFiles=testAudioFilesSrc, destDir=MLUSettings.testDataGenAudioFilesDir)
        self.testAudioFilepaths = mypycommons.file.GetAllFilesRecursive(MLUSettings.testDataGenAudioFilesDir)
                
        # Generate new test vote playlist files in the cache test files dir 
        self.testVotePlaylistsDir = MLUSettings.testDataGenVotePlaylistsDir
        self.generateTestVotePlaylists(self)


    @classmethod
    def tearDownClass(self):
        super(TestRatestatsModule, self).tearDownClass
        mypycommons.file.DeleteDirectory(self.testDataTempDir)

    def generateTestVotePlaylists(self):
        playlistFilepaths = mlu.ratestats._getVotePlaylistFilepaths(self.testVotePlaylistsDir)

        for playlist in playlistFilepaths:
            numPlaylistEntries = mlutest.common.getRandomNumber(0, 50)
            playlistEntries = []
            for currentEntryNum in range(1, numPlaylistEntries + 1):
                playlistEntries.append(mlutest.common.getRandomItemFromList(self.testAudioFilepaths))
        
            mypycommons.file.writeToFile(playlist, playlistEntries)
        
    def getMockAudioFileVoteData(self):
        # Generate list of numbers from 0.5 to 10.0
        possibleVoteValues = mlu.ratestats._getPossibleVoteValues()

        mockFilepath = mlutest.common.getRandomItemFromList(self.testAudioFilepaths)
        mockVotesLength = mlutest.common.getRandomNumber(min=1, max=100)
        mockVotes = [mlutest.common.getRandomItemFromList(possibleVoteValues) for x in range(1, mockVotesLength + 1)]

        voteData = mlu.ratestats.AudioFileVoteData(mockFilepath, mockVotes)
        return voteData

    def appendLineToFile(self, filepath, lineText):
        with open(filepath, "a") as myfile:
            myfile.write(lineText)

    def getRandomVotePlaylistNumbers(self, count):
        randomPlaylistNums = []
        possibleNums = mlu.ratestats._getPossibleVoteValues()
        for i in range(count):
            num = mlutest.common.getRandomItemFromList(possibleNums)
            randomPlaylistNums.append(num)

        return set(randomPlaylistNums)

    def testCalculateRatingTagValue(self):
        testData = [
            {
                'testVotes': [2.5, 4.5, 9.0, 10.0, 0.5, 4.5, 5.0, 9.5, 1.0, 2.5],
                'actualRating': 4.9
            },
            {
                'testVotes': [3.5, 5.5, 0.5, 1.5, 1.5, 3.5, 6.0, 5.5, 4.0, 5.5],
                'actualRating': 3.7
            },
            {
                'testVotes': [2.0, 4.0, 9.5, 3.5, 1.5, 4.0, 9.0, 9.5, 9.0, 9.5],
                'actualRating': 6.2
            }
        ]

        for testCase in testData:
            ratingResult = mlu.ratestats._calculateRatingTagValue(testCase['testVotes'])
            self.assertEqual(ratingResult, str(testCase['actualRating']))

    def testUpdateRatestatTagsFromVoteData(self):
        '''
        Tests that a single audio file can be updated with the correct ratestat tags, using the
        'updateRatestatTagsFromVoteData' method, given a test AudioFileVoteData object to update from.
        '''
        testVoteData = self.getMockAudioFileVoteData()

        tH = mlu.tags.io.AudioFileTagIOHandler(testVoteData.filepath)
        testAudioFileInitialTags = tH.getTags()

        mlu.ratestats.updateRatestatTagsFromVoteData(testVoteData)

        # compare the values of the ratestat tags on the test file after the test operation in run
        testAudioFileNewTags = tH.getTags() 

        initialVotes = sorted(mlu.tags.common.formatAudioTagToValuesList(testAudioFileInitialTags.votes, valuesAs='float'))
        newVotes = sorted(mlu.tags.common.formatAudioTagToValuesList(testAudioFileNewTags.votes, valuesAs='float'))

        # Test new votes values
        self.assertGreater(len(newVotes), len(initialVotes))
        votesOldNewDiff = len(newVotes) - len(initialVotes)
        expectedNewVotesCount = len(initialVotes) + votesOldNewDiff
        self.assertEqual(expectedNewVotesCount, len(newVotes)) 

        newlyAddedTestVotes = sorted(testVoteData.votes)
        expectedNewVotes = sorted(newlyAddedTestVotes + initialVotes)
        self.assertEqual(expectedNewVotes, newVotes)

        # Test new rating value
        newRatingNum = float(testAudioFileNewTags.rating)
        self.assertIsNotNone(newRatingNum)
        self.assertNotEqual(newRatingNum, 0)
        self.assertGreaterEqual(newRatingNum, 0.5)
        self.assertLessEqual(newRatingNum, 10)

        actualVoteAvg = float(mlu.ratestats._calculateRatingTagValue(newVotes))
        self.assertEqual(newRatingNum, actualVoteAvg)

    def testGetAudioFileVoteDataFromRatePlaylists(self):
        '''
        Tests that the correct AudioFileVoteData list data is returned when the vote playlists are
        parsed and read by the 'getAudioFileVoteDataFromRatePlaylists' method.
        '''
        actualAudioFileVoteDataList = mlu.ratestats.getAudioFileVoteDataFromRatePlaylists(self.testVotePlaylistsDir)
        actualVotePlaylists = mlu.ratestats._getVotePlaylistFilepaths(self.testVotePlaylistsDir)

        for voteDataItem in actualAudioFileVoteDataList:
            for testPlaylist in actualVotePlaylists:
                currentPlaylistVoteValue = float(mypycommons.file.GetFileBaseName(testPlaylist))

                fileLines = mypycommons.file.readFile(testPlaylist)
                fileLines = [line.replace('\n', '') for line in fileLines]

                countOfThisAudioInPlaylist = fileLines.count(voteDataItem.filepath)
                actualCountOfThisVoteValue = voteDataItem.votes.count(currentPlaylistVoteValue)

                self.assertEqual(countOfThisAudioInPlaylist, actualCountOfThisVoteValue)

    def testArchiveVotePlaylists(self):
        mlu.ratestats.archiveVotePlaylists(playlistsDir=self.testVotePlaylistsDir, archiveDir=MLUSettings.testDataGenArchivedVotePlaylistsDir)

        archiveFiles = mypycommons.file.GetAllFilesRecursive(MLUSettings.testDataGenArchivedVotePlaylistsDir)
        self.assertEqual(len(archiveFiles), 1)

    def testResetVotePlaylists(self):
        processedFilesDir = mypycommons.file.JoinPaths(self.testDataTempDir, 'vote-playlists-that-were-processed')
        mypycommons.file.createDirectory(processedFilesDir)

        sourceVotePlaylists = mypycommons.file.GetAllFilesRecursive(self.testVotePlaylistsDir)
        mypycommons.file.CopyFilesToDirectory(sourceVotePlaylists, processedFilesDir)

        # Get the list of source playlists and randomly take one of the playlists here and update
        # it by giving it a new entry, simulating a realtime update of the source playlists
        randomVotePlaylistNums = self.getRandomVotePlaylistNumbers(count=mlutest.common.getRandomNumber(1, 15))
        randomAudioFilepath = mlutest.common.getRandomItemFromList(self.testAudioFilepaths)

        for votePlaylist in sourceVotePlaylists:
            votePlaylistNum = float(mypycommons.file.GetFileBaseName(votePlaylist))
            if (votePlaylistNum in randomVotePlaylistNums):
                self.appendLineToFile(votePlaylist, randomAudioFilepath)

        # Now that the source playlists may likely differ from the processed playlists, test this
        # to make sure the playlists get reset successfully without new data loss
        mlu.ratestats.resetVotePlaylists(votePlaylistsSourceDir=self.testVotePlaylistsDir, votePlaylistsTempDir=processedFilesDir)
        

if __name__ == '__main__':
    unittest.main()