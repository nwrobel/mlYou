'''
mlu.playbacks

First Created: 01/16/20
Last Modified: 01/16/20

Module that deals with handling song playback instances and determining the playback tag values
(playstat tags) that should be written to the played songs accordingly. 

This includes logic for: 
- determining if a play should be counted based on playback duration 
- calculations for time last played, first played, all times played, and play count tag values
- defining playback instance and playback records classes
- merging playback instances containing multiple play instances of the same song into playback 
list records containing multiple records of plays for a single song

'''

# TODO: move functionality from mpd.plays module into this module - any functionality that can
# apply to playback tracking for any player (not just MPD)