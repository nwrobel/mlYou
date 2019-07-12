import mutagen

# Returns the following tag values for the given audio file, given its filepath:
#   durationSeconds
#   title
#   artist
#   album
#
def GetBasicTags(songFilepath):
    tags = {}
    audioFile = mutagen.File(songFilepath)

    tags['durationSeconds'] = audioFile.info.length
    tags['title'] = audioFile['TITLE']
    tags['artist'] = audioFile['ARTIST']
    tags['album'] = audioFile['ALBUM']

    return tags
