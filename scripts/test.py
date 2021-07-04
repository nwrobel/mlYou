import envsetup
envsetup.PreparePythonProjectEnvironment()

import mlu.tags.io

if __name__ == "__main__":
    audioFilepath = "Z:\\Development\\Test Data\\mlYou\\test-audio-files\\test-1.flac"
    metaHandler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
    tags = metaHandler.getTags()
    pics = metaHandler.getEmbeddedArtwork()
    print(tags)

    audioFilepath = "Z:\\Development\\Test Data\\mlYou\\test-audio-files\\test-1.mp3"
    metaHandler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
    tags = metaHandler.getTags()
    pics = metaHandler.getEmbeddedArtwork()
    print(tags)

    audioFilepath = "Z:\\Development\\Test Data\\mlYou\\test-audio-files\\test-1.m4a"
    metaHandler = mlu.tags.io.AudioFileMetadataHandler(audioFilepath)
    tags = metaHandler.getTags()
    pics = metaHandler.getEmbeddedArtwork()
    print(tags)