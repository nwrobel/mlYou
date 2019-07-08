import mutagen

# Returns the following tag values for the given audio file, given its filepath:
#   durationSeconds
#   title
#   artist
#   album
#
def GetCommonTags(songFilepath):
    tags = {}
    audioFile = mutagen.File(songFilepath)

    tags['durationSeconds'] = audioFile.info.length
    tags['title'] = audioFile['title']
    tags['artist'] = audioFile['artist']
    tags['album'] = audioFile['album']

    return tags
