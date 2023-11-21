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

Each python script accepts an optional param `--config-file`, which can be used to load a different config other than from "mlu.config.json"

## Current Stable Features
### Change root directory paths of playlist items in mass 
Replace one root directory string with another, in mass (useful if managing music on two different systems)

- set config file values: 
  - `convertPlaylists.inputDir`: where to process all playlists from
  - `convertPlaylists.outputDir`: where new playlists are written
- cd into mlu dir and activate virtual environment (py-venv-<your_os>)
```
python3 scripts/change-playlist-items-root-path.py "Z:\\" "/datastore/nick/" --extension "m3u"
```

### Update 'RATING' tag based on vote playlists
Use 'vote' playlists to assign values to 'RATING' tag. This updates the tag values based on the configured
vote playlists. 
Useful if you want to rate your music and persist it in tags. 
I listen to my music via MPD server, but this strategy can be used with any playback program that does not allow you to set rating (but does allow you to save playlists).
I like to rate my songs while listening to them, and this is not possible in many playback programs. 

- set config file values: 
  - `rating.votePlaylistInputDir`: dir where the configured vote playlist files are stored
  - `rating.votePlaylistArchiveDir`: dir where processed vote playlists will be saved for archival before being reset
  - `rating.votePlaylistFiles`: set items in the array according to how you want to set up your rating system
    - `filename`: name of vote playlist file
    - `value`: value to assign to the rating tag for tracks in this playlist
- cd into mlu dir and activate virtual environment (py-venv-<your_os>)
```
python3 scripts/update-ratestat-tags-from-vote-playlists.py
```

### Music Player Daemon (MPD) Playback Statistics Collection and Tag Updates
- Collects and aggregates playcount information from an MPD log file and updates your audio file tags with the collected playback data
- Populates/updates the following tag values 
  - PLAY_COUNT
  - DATE_LAST_PLAYED
  - DATE_ALL_PLAYS

#### Usage
- Configure mpd to log to syslog
```
log_file     "syslog"
```

- Install and configure `rsyslog`
```
sudo apt install rsyslog
```
  - Configure /etc/rsyslog.conf (see config-examples)
  - Configure /etc/rsyslog.d/mpd.conf (see config-examples)
  - touch the log file at the path you used in previous config
```
sudo chown syslog:adm /var/log/mpd-master.log
sudo chmod 640 /var/log/mpd-master.log
sudo service rsyslog restart
sudo service mpd restart
```

- set config file values: 
  - `mpd.logFilepath`: filepath of your mpd log file
  - `mpd.logArchiveDir`: dir where processed mpd log file will be saved for archival before being reset
  - `mpd.outputDir`: dir where playback data collected from the mpd log file will be written for review

- Listen to your music on MPD. When ready to collect and review playstats tags, run the loader script:
```
python3 scripts/update-playstat-tags-from-mpd-log.py -l
``` 

This will create a data dir inside your `mpd.outputDir` timestamped. Inside are two data files and two summary files:
  - `playbacks.data.json`: raw playback data of included playback instances for audio files
  - `playbacks-excluded.data.json`: raw playback data of excluded playback instances for audio files
  - `summary-playback-history.txt`: table of tracks listing playback date and duration (for logging purposes only)
  - `summary-playback-totals.txt`: table of tracks listing play count totals (for logging purposes only) 

Script is configured currently to exclude any playbacks where <20% of the file is played.

- Review and edit `playbacks.data.json` (remove any false playbacks you don't recall, or copy some from excluded file to this file)

- Run the save script, passing it the name of the data dir (name only, it should be in your `mpd.outputDir`)
```
python3 scripts/update-playstat-tags-from-mpd-log.py -s "[2023-11-21 12.44.37] playback-data-output"
```

This will update the playback tags from the data in `playbacks.data.json` you reviewed earlier

### mlu.tags.io module can be used for your own purposes
Useful if you want to read from / write to to your own custom tag names (uses `mutagen`)


 



