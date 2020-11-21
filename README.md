# mlYou - Music Library Utilities Suite

## UNDER CONSTRUCTION
This project is still being developed: only features listed under "Current Features" are ready for use. More features are being developed and are coming soon! 

## Overview
This is a collection of tools to help you manage, maintain, and optimize your own music library for a better experience. 

It makes growing and maintaining a music collection of any size easier by automating necessary (but tedious) processes.

The tools currently aim to assist with music organizing and tagging, and playlist management.

#### Cross-Platform Compatible
Works and tested under Linux (Ubuntu) and Windows.

## Installation/Setup
- Install the latest version of Python on your system, if you don't have it already (Python 3.7 or greater is required)
- Download/clone this github project, save it on your computer in any location
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

## Settings File
Located in `mlYou\mlu\settings.py`

This file defines several setting values (user/system preferences) for use across all mlYou scripts.
Before using any scripts, please update the setting values as needed.

## Current Features
### Playlist root path fixing
- Allows broken playlists that have their song path entries pointing to the wrong music library root to be fixed to point to the correct root, preserving your playlist-creation work

#### Usage
- cd to the `scripts` dir of the mlYou project folder
- Run from the terminal:
```
python .\convert-playlist.py <OldMusicRootPath> <NewMusicRootPath> <SourcePlaylistsFolder> <DestinationPlaylistsFolder>
```

### Maintaining a Votes & Rating System for Songs
#### Music rating can be difficult at times: 
- your opinion on a song may vary over time depending on amount played, mood, etc
- a single like/dislike or a single static number may not best reflect your opinion of a song
- limited granularity of rating values (only 5 possible values in a typical 1-5 system, or 2 in a like/dislike system)
#### Improved rating system: Cast Votes for songs
 - Can vote on a single song multiple times (ex: now, and then when you hear it again next month)
 - Choose your own vote value range (1-10, 1-100, etc)
 - Vote by adding the song to a playlist that corresponds to the desired vote value
#### Rating Value for a song based on Votes
- Rating is calculated from the average vote value
- Much more wholistic prepresentation of your opinion of the song over time
#### MLU Scripts will update/manage ID3 Rating tags for songs:
- Go through all vote playlists
- Add vote to the song's `VOTES` tag
- Update each song's `RATING` tag by re-calculating it or adding it for first time

#### Usage: Updating song rating tags from current vote playlists
- cd to the `scripts` dir of the mlYou project folder
- Run from the terminal:
```
python .\update-ratestat-tags-from-vote-playlists.py
```

Based on your settings defined in the mlYou settings file, the script will find your vote playlists
and music directory to work. For each time a song is part of a vote playlist, that corresponding vote value
will be added to the song's `VOTES` array tag. When done processing votes, all the song's saved and new 
votes will be averaged to update the song's `RATING` tag value. 

Once this finishes for all songs, the vote playlists will be archived and then cleared/reset so that
this vote data won't be counted again.

## Note: Windows Automation For mlYou Scripts
On Windows, the mlYou python scripts can be made to run using Powershell scripts for automation purposes.
Each Powershell script can run a specific script using predefined parameters. 

This way, arguments to mlYou scripts that you want to preserve can be saved within these files.
Also, you can use this to create scheduled tasks in your OS to have work automated/done on a regular basis.

See the .ps1 script files in the `automated` dir of the mlYou project folder for examples of how to do this.

- Run from automated scripts from Powershell terminal:
```
cd \path\to\mlYou\automated
.\<script-name>.ps1
```


## Work-in-Progress Features (Coming Soon!)
### Music Player Daemon (MPD) Playback Statistics Collection and Tag Updates
- Collects and aggregates playcount information from MPD's logs to update your songs with the latest playback data as your music is played on your streaming server
- Populates/updates the following ID3 tag values directly on your played audio files. These tags can then be used to create autoplaylists and to preserve your playback history:
--- Play Count
--- Date/time last played
--- All date/times played



### Auto-Tagging of Music using Discogs Tag Data




