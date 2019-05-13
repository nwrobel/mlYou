# mlYou - Music Library Utilities Suite

## UNDER CONSTRUCTION
This project is still in the early stages of development and is not yet usable. 

## Overview
This is a collection of tools to help you add to, manage, and maintain your music library. 

It makes growing and maintaining a music collection of any size super easy, by automating tedious (but necessary) proccesses.

The tools assist with music downloading, tagging, and playlist management.

## Current Features and Functionality
#### Playlist root path fixing
- Allows broken playlists that have their song path entries pointing to the wrong music library root to be fixed to point to the correct root, preserving your playlist-creation work
```
convert-playlist.py OldMusicRootPath NewMusicRootPath SourcePlaylistsFolder DestinationPlaylistsFolder
```

#### Music Player Daemon (MPD) Playback Statistics Collection and Tag Updates
- Collects playcount information from MPD's logs and aggregates it to update your songs with the latest playback data as your music is played on your streaming server
- Populates/updates the following ID3 tag values directly on your played audio files:
--- Play Count
--- Date/time first played
--- Date/time last played

#### Easy-To-Setup Automation of these Scripts
- The 'automation' folder contains Powershell and Bash scripts that allow you to setup your input data for each script and have it run with that data automatically
- Once set up, you can created scheduled tasks in your OS to have work automated/done on a regular basis

#### Cross-Platform Compatible
Works and tested under Linux (Ubuntu) and Windows. Mac unteested but expected to work simular to linux.




