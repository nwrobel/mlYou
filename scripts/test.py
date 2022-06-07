# Do setup processing so that this script can import all the needed modules from the "mlu" package.
# This is necessary because these scripts are not located in the root directory of the project, but
# instead in the 'scripts' folder.
import envsetup
envsetup.PreparePythonProjectEnvironment()

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.archive

from mlu.settings import MLUSettings
import mlu.mpd.log
import mlu.mpd.plays
import mlu.tags.playstats
from mlu.tags.io import AudioFileFormatNotSupportedError, AudioFileNonExistentError
import mlu.utilities

mlu.utilities.testAudioFilesForErrors(
    ["Z:\\Music Library\\Content\\Web-DL\\Remix\\remix.nin.com\\Reaps08 - Vessel - Reaps Remix.mp3", 
    "Z:\\Music Library\\Content\\Web-DL\\Remix\\remix.nin.com\\Reaps08 - Last - Reaps Remix V2.mp3  ",
    "Z:\\Music Library\\Content\\Web-DL\\Remix\\remix.nin.com\\TweakerRay - The good soldier (believes in peace RMX).mp3"])