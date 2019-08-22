# mlYou - Music Library Utilities Suite

## UNDER CONSTRUCTION
This project is still being developed: only features listed under "Current Features" are ready for use. More features are being developed and are coming soon! 

## Overview
This is a collection of tools to help you manage, maintain, and optimize your own music library for a better experience. 

It makes growing and maintaining a music collection of any size easier by automating necessary (but tedious) proccesses.

The tools currently aim to assist with music organizing and tagging, and playlist management.

#### Cross-Platform Compatible
Works and tested under Linux (Ubuntu) and Windows. Mac untested but expected to work simular to linux.

## Installation/Setup
- Download/clone this github project, save it on your computer in any location
- In the mlYou project, open `setup` folder
- Windows: Run the Powershell script `deploy-windows.ps1` by running it from the Powershell terminal:
```
cd <drive>:\path\to\mlYou
.\setup\deploy-windows.ps1
```
- Linux: Run the bash script `deploy-linux.sh`
```
cd <drive>:\path\to\mlYou
.\setup\deploy-linux.sh
```

## Current Features
### Playlist root path fixing
- Allows broken playlists that have their song path entries pointing to the wrong music library root to be fixed to point to the correct root, preserving your playlist-creation work

#### How to use
##### (Option 1) Run using Python
- Run from the terminal:
```
python convert-playlist.py OldMusicRootPath NewMusicRootPath SourcePlaylistsFolder DestinationPlaylistsFolder
```
##### (Option 2) Run using Powershell
- Open the Powershell script `Convert-Playlist.ps1` in the `automated` folder
- Change the values of the old/new music root paths and src/dest playlists folders
- Save the script
- Run from Powershell terminal:
```
cd <drive>:\path\to\mlYou
.\automated\Convert-Playlist.ps1
```
- Note: you can use the commands above to create scheduled tasks in your OS to have work automated/done on a regular basis


## Work-in-Progress Features (Coming Soon!)
#### Music Player Daemon (MPD) Playback Statistics Collection and Tag Updates
- Collects and aggregates playcount information from MPD's logs to update your songs with the latest playback data as your music is played on your streaming server
- Populates/updates the following ID3 tag values directly on your played audio files. These tags can then be used to create autoplaylists and to preserve your playback history:
--- Play Count
--- Date/time last played
--- All date/times played

#### Tools to Maintain your own Votes & Rating System for Songs
- Music rating can be difficult at times: 
--- your opinion on a song may vary over time depending on amount played, mood, etc
--- a single like/dislike or a single static number may not best reflect your opinion of a song
--- limited granularity of rating values (only 5 possible values in a typical 1-5 system, or 2 in a like/dislike system)
- Improved rating system: Cast Votes for songs
 --- Can vote on a single song multiple times (ex: now, and then when you hear it again next month)
 --- Choose your own vote value range (1-10, 1-100, etc)
 --- Vote by adding the song to a playlist that corresponds to the desired vote value
- Rating Value for a song based on Votes
--- Rating is calculated from the average vote value
--- Much more wholistic prepresentation of your opinion of the song over time
- MLU Script will update/manage ID3 Rating tags for songs:
--- Go through all vote playlists
--- Add vote to the song's "vote" tag
--- Update each song's "rating" tag by re-calculating it




