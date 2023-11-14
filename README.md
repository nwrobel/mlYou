# mlu - My Music Library Utilities Suite

## Overview
This is a collection of scripts and modules that I use to manage and maintain my music library. 

I use the following software primarily:
- foobar2000: local tag editing, viewing, queries, autoplaylists, file utilities
- Musicbrainz Picard: mass tagging
- MPD: music player daemon server for listening to music

Supported audio filetypes: FLAC, Mp3, M4A, OGG OPUS (.opus file)

#### Cross-Platform Compatible
Works and tested under Linux (Ubuntu) and Windows.

## Installation/Setup
### Direct repo clone
- Install the latest version of Python on your system, if you don't have it already (Python 3.7 or greater is required)
- Download/clone this github project
- Change dirs to the mlu project folder
- Windows: Run the Powershell script `Setup-Windows.ps1` by running it from the Powershell terminal:
- Linux: Run the bash script `setup-linux.sh`

## Settings File
Located at `mlu/config/mlu.config.json`

This file defines several setting values (user/system preferences) for use across all mlu modules and scripts.
Before using any scripts or modules, please update the setting values as needed.

## Current Stable Features
- Change root directory paths of playlist items in mass (useful if managing music on two different systems)
- Update 'RATING' tag based on vote playlists. Useful if you listen to music via MPD server and you want to rate your music and persist it in tags.
- mlu.tags.io module can be used for your own purposes (can extend to write to your own custom tag names) 

## WIP Features
### Music Player Daemon (MPD) Playback Statistics Collection and Tag Updates
- Collects and aggregates playcount information from an MPD log file and updates your audio file tags with the latest playback data.
- Preserve your playback history!
- Populates/updates the following tag values directly on your played audio files. 
    - PLAY_COUNT
    - DATE_LAST_PLAYED
    - DATE_ALL_PLAYS
 



