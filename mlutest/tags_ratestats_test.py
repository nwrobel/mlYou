import unittest
import numpy as np

# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from mlu.settings import MLUSettings

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.logger

mypycommons.logger.initSharedLogger(MLUSettings.logDir)
logger = mypycommons.logger.getSharedLogger()

import mlutest.common
import mlu.ratestats


class TestRatestatsModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        '''
        Sets up the test data for the tests of the tags.io module. The test audio files are copied
        from the test resource dir to the mlu cache dir, where they will be manipulated by the tests
        while preserving the original test data files.
        '''
        super(TestRatestatsModule, self).setUpClass        

        self.testDataDir = MLUSettings.testDataGenTempDir

        # copy the test audio files from the static test files dir to the temp cache test files dir
        testStaticAudioFilepaths = mypycommons.file.GetAllFilesRecursive(MLUSettings.testDataStaticAudioFilesDir)
        mypycommons.file.CopyFilesToDirectory(srcFiles=testStaticAudioFilepaths, destDir=MLUSettings.testDataGenAudioFilesDir)
        self.testAudioFilepaths = mypycommons.file.GetAllFilesRecursive(MLUSettings.testDataGenAudioFilesDir)
        
        # Generate new test vote playlist files in the cache test files dir 
        self.testVotePlaylistsDir = MLUSettings.testDataGenVotePlaylistsDir
        self.generateTestVotePlaylists(self)


    @classmethod
    def tearDownClass(self):
        super(TestRatestatsModule, self).tearDownClass
        
        mypycommons.file.DeleteDirectory(self.testDataDir)

    def generateTestVotePlaylists(self):
        playlistFilepaths = mlu.ratestats._getVotePlaylistFilepaths(self.testVotePlaylistsDir)

        for playlist in playlistFilepaths:
            numPlaylistEntries = mlutest.common.getRandomNumber(0, 20)
            playlistEntries = []
            for currentEntryNum in range(1, numPlaylistEntries + 1):
                playlistEntries.append(mlutest.common.getRandomItemFromList(self.testAudioFilepaths))
        
            mypycommons.file.writeToFile(playlist, playlistEntries)
        
    def getMockAudioFileVoteData(self):
        possibleVoteValues = np.linspace(0.5,10,20)

        mockFilepath = mlutest.common.getRandomItemFromList(self.testAudioFilepaths)
        mockVotesLength = mlutest.common.getRandomNumber(min=1, max=100)
        mockVotes = [mlutest.common.getRandomItemFromList(possibleVoteValues) for x in range(1, mockVotesLength + 1)]

        voteData = mlu.ratestats.AudioFileVoteData(mockFilepath, mockVotes)
        return voteData

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

        # Test new rating value
        newRatingNum = float(testAudioFileNewTags.rating)
        self.assertIsNotNone(newRatingNum)
        self.assertNotEqual(newRatingNum, 0)
        self.assertGreaterEqual(newRatingNum, 0.5)
        self.assertLessEqual(newRatingNum, 10)

        # Test new votes values
        self.assertGreater(len(testAudioFileNewTags.votes), len(testAudioFileInitialTags.votes))
        votesOldNewDiff = len(testAudioFileNewTags.votes) - len(testAudioFileInitialTags.votes)
        expectedNewVotesCount = len(testAudioFileInitialTags.votes) + votesOldNewDiff
        self.assertEqual(expectedNewVotesCount, len(testAudioFileNewTags.votes))   
    
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
        mlu.ratestats.archiveVotePlaylists(playlistsDir=MLUSettings.votePlaylistsTempDir, archiveDir=MLUSettings.votePlaylistsArchiveDir)

    def testResetVotePlaylists(self):
        mlu.ratestats.resetVotePlaylists(votePlaylistsSourceDir=MLUSettings.votePlaylistsDir, votePlaylistsTempDir=MLUSettings.votePlaylistsTempDir)
        

if __name__ == '__main__':
    unittest.main()