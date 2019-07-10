# Write out the 3 cache json files:
#   current playback instances found
#   current playstats tag values of the songs that will be updated
#   new tag values that will be set, based on applying the changes from 1 to the tags in 2
# use the cache module to write the json and use the tags.playstats module to read old file playstat tag values 
# and calculate new ones based on playback instances

# Use tags.playstats module to update/write the new tag values, based on the 3rd json cache file

# Use tags.playstats module to read the tags back and use the 3rd json cache file to verify integrity of each song's new values

import json




