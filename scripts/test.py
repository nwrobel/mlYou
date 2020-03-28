# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

import mlu.tags.io

# handler = mlu.tags.io.AudioFileTagIOHandler("D:\\Temp\mlu-test\\test-music-lib\\Content\Music\\(hed) Planet Earth\\The Best Of (Hed) Planet Earth\\1.01. (hed) Planet Earth - Suck It Up.flac")
# print(handler)

# tag = handler.getAudioTagValue('title')
# tag2 = handler.getAudioTagValue('play_count')
# print(tag)



handler = mlu.tags.io.AudioFileTagIOHandler("D:\\Temp\mlu-test\\test-music-lib\\Content\Music\\Derek Trucks And Co\\The Derek Trucks Band\\1997 - The Derek Trucks Band (320 kbps)\\01 - Sarod.mp3")
print(handler)

tag = handler.getAudioTagValue('title')
tag2 = handler.getAudioTagValue('play_count')

handler.setAudioTagValue('play_count', 10)
print(tag)