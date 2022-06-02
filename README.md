# mlYou - Music Library Utilities Suite

## UNDER CONSTRUCTION
This project is still being developed: only features listed under "Current Features" are ready for use. More features are being developed and are coming soon! 

## Overview
This is a collection of scripts and modules to help you manage, maintain, and optimize your music library. 
The tools currently aim to assist with music organizing and tagging, and playlist management.

Currently supported audio filetypes: FLAC, Mp3, M4A, OGG OPUS (.opus file)

#### Cross-Platform Compatible
Works and tested under Linux (Ubuntu) and Windows.

## Installation/Setup
### Direct repo clone
- Install the latest version of Python on your system, if you don't have it already (Python 3.7 or greater is required)
- Download/clone this github project
- Change dirs to the mlYou project folder
- Windows: Run the Powershell script `Setup-Windows.ps1` by running it from the Powershell terminal:
```
cd <drive>:\path\to\mlYou
.\Setup-Windows.ps1
```
- Linux: Run the bash script `setup-linux.sh`
```
cd /path/to/mlYou
./setup-linux.sh
```

### Pip package
If you want to use the modules of this project in your own project, the best way is to install the mlu module as a Pip package.
Install with Pip:

```bash
 pip install -e git+https://github.com/nwrobel/mlYou#egg=nwrobel-mlYou
```

## Settings File
Located at `mlYou\mlu.config.json`

This file defines several setting values (user/system preferences) for use across all mlYou modules and scripts.
Before using any scripts or modules, please update the setting values as needed.

## Current Features

### The Python 'mlu' module
Contains various functions and classes. Take a look around to see what you can use.
Currently, the modules mainly help you read audio file tag data and file properties. 

### Music Player Daemon (MPD) Playback Statistics Collection and Tag Updates
- Collects and aggregates playcount information from an MPD log file and updates your audio file tags with the latest playback data.
- Preserve your playback history!
- Populates/updates the following tag values directly on your played audio files. 

-- PLAY_COUNT
-- DATE_LAST_PLAYED
-- DATE_ALL_PLAYS

These tags can then be viewed in foobar2000 (or other music player that reads custom tag values) and used to create autoplaylists.




