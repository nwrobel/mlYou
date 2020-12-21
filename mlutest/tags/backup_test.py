import unittest
import os
import sys
import envsetup
envsetup.PreparePythonProjectEnvironment()

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mlu.cache.io
from mlu.settings import MLUSettings

class TestTagsBackupModule(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        '''
        Sets up the test data for the tests of the tags.io module. The test audio files are copied
        from the test resource dir to the mlu cache dir, where they will be manipulated by the tests
        while preserving the original test data files.
        '''
        super(TestTagsBackupModule, self).setUpClass        
        x = '2'
        print(x)
        # self.testDataDir = MLUSettings.testDataStaticDir

        # # copy the test audio files from the static test files dir to the temp cache test files dir
        # testStaticAudioFilepaths = mypycommons.file.GetAllFilesRecursive(MLUSettings.testDataStaticAudioFilesDir)
        # mypycommons.file.CopyFilesToDirectory(srcFiles=testStaticAudioFilepaths, destDir=MLUSettings.testDataGenAudioFilesDir)
        # self.testAudioFilepaths = mypycommons.file.GetAllFilesRecursive(MLUSettings.testDataGenAudioFilesDir)
        
        # # Generate new test vote playlist files in the cache test files dir 
        # self.testVotePlaylistsDir = MLUSettings.testDataGenVotePlaylistsDir
        # self.generateTestVotePlaylists(self)


    @classmethod
    def tearDownClass(self):
        super(TestTagsBackupModule, self).tearDownClass
        
        print('dying')

    def testGetNewAudioFileTagsBackupFilepath(self):
        x = 2
        self.assertEqual(x, 2)
        print(MLUSettings.musicLibraryRootDir)


if __name__ == '__main__':
    unittest.main()