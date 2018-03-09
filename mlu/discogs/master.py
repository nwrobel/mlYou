import argparse
import mutagen
from bs4 import BeautifulSoup
from urllib.request import urlopen
from mlu.discogs import auth
from mlu import common
import time

def printScriptIntro():
    print("############ Welcome to the Discogs Master Tag Writer ##############")
    print()
    print("----------------------------BACKGROUND------------------------------")
    print("Using the Discogs plugin to add tags to songs through foobar2000")
    print("(by clicking 'Tagging' > 'Discogs' > 'Write Tags') does not get all")
    print("of the correct tags. For example, you could have picked an album") 
    print("release that fits your album's tracklist, but that release may differ")
    print("from the master in the tags Date, Genre, and Discogs user statistics.")
    print()
    print("This script corrects this by finding the Discogs master release page")
    print("for all albums in the music directory and writing the following tags,")
    print("taken directly from the master release page, to each album's songs:")
    print("- Date")
    print("- Genre (including 'Style')")
    print("- DISCOGS_RATING")
    print("- DISCOGS_VOTES")
    print("- DISCOGS_USERS_HAVE")
    print("- DISCOGS_USERS_WANT")
    print()
    input("Press ENTER to begin the process...")
    print()

def printReleaseIdNotFoundForSong(songPath):
    print("Error parsing the tag 'DISCOGS_RELEASE_ID' for file ", songPath)
    print("In foobar2000, write the following tags using Discogs by")
    print("selecting the song(s) on an album, then clicking 'Tagging'") 
    print("> 'Discogs' > 'Write Tags':")
    print("- Artist Name")
    print("- Track Title")
    print("- Album Title (normal, do not write the words 'delux' or 'xxx version' in the album title...check the tag in the Discogs window before it is written)")
    print("- Composer")
    print("- Album Artist")
    print("- Track Number")
    print("- Total Tracks")
    print("- Disc Number")
    print("- Total Discs")
    print("- ALBUM_NOTES")
    print("- ARTIST_NOTES")
    print("- ARTIST_WEBSITES")
    print("- DISCOGS_RELEASE_ID")
    print()
    print("Skipping this album and its songs becuase no release ID was found...")
    print()

def getDeepestObjectInPath(path):
    pathParts = path.split("/")
    deepestObjectInPath = pathParts[-1]
    return deepestObjectInPath

def getAllArtistsAlbumsSongs(musicDir):
    
    allArtistsAlbumSongs = []
    
    allArtistDirs = common.getAllDirsDepth1(musicDir)
    
    for artistDir in allArtistDirs:
        albumDirs = common.getAllDirsDepth1(artistDir)
        
        for albumDir in albumDirs:
            albumSongs = common.getAllFilesRecursive(albumDir)
            newAlbum = {"artist": getDeepestObjectInPath(artistDir), "album": getDeepestObjectInPath(albumDir), "albumSongPaths": albumSongs}
            allArtistsAlbumSongs.append(newAlbum)
            
    return allArtistsAlbumSongs

def countSongs(allArtistAlbumSongs):
    count = 0
    for artistAlbumSongs in allArtistAlbumSongs:
        countForAlbum = len(artistAlbumSongs['albumSongPaths'])
        count += countForAlbum
        
    return count
    

def getReleaseIdForAlbum(artistAlbumSongs):
    
    songPaths = artistAlbumSongs['albumSongPaths']
    
    # Get the releaseId for the album based on the first song in the album.
    # We assume all the songs in the album already have a releaseId
    # because we run this script AFTER getting tags through foobar
    selectedSongPath = songPaths[0]
    audioFile = mutagen.File(selectedSongPath)
     
    try:
        albumReleaseID = audioFile['DISCOGS_RELEASE_ID'][0]
        return albumReleaseID
        
    except KeyError:
        printReleaseIdNotFoundForSong(selectedSongPath)
        return 0
        

def getMasterReleaseUserStats(masterUri):
    try:
        page = urlopen(masterUri)
    except:
        print("Too many requests...server returned a 429. Waiting 60 seconds before sending more requests.")
        time.sleep(60)
        page = urlopen(masterUri)

        
    soup = BeautifulSoup(page, "html.parser")
    
    statsOuterDiv = soup.find("div", {"id": "statistics"})
    
    userStatsTags = {}
    
    have = statsOuterDiv.find("a", { "class": "coll_num" })
    userStatsTags["DISCOGS_USERS_HAVE"] = have.text
    
    want = statsOuterDiv.find("a", { "class": "want_num" })
    userStatsTags["DISCOGS_USERS_WANT"] = want.text
    
    rating = statsOuterDiv.find("span", { "class": "rating_value" })
    userStatsTags["DISCOGS_RATING"] = rating.text
    
    votes = statsOuterDiv.find("span", { "class": "rating_count" })
    userStatsTags["DISCOGS_VOTES"] = votes.text
    
    return userStatsTags
    

def getMasterReleaseTagsFromNonMasterReleaseId(client, releaseId):
    
    tags = {}
    release = client.release(releaseId)
    masterRelease = release.master
    
    if (not masterRelease):
        print("Failed to get the master release object from the release Id ", releaseId)
        print("Skipping this album and its songs...")
        return 0
        
    
    print("Found master release for album successfully:", masterRelease)

    try:
        styles = masterRelease.data['styles']
    except KeyError:
        print("'Styles' property not found on the master album object:", masterRelease.title)
        styles = ''
        
    tags['genres'] = masterRelease.data['genres'] + styles
    tags['date'] = masterRelease.data['year']
    
    masterUserStats = getMasterReleaseUserStats(masterRelease.data['uri'])
    tags["DISCOGS_RATING"] = masterUserStats["DISCOGS_RATING"]
    tags["DISCOGS_VOTES"] = masterUserStats["DISCOGS_VOTES"]
    tags["DISCOGS_USERS_HAVE"] = masterUserStats["DISCOGS_USERS_HAVE"]
    tags["DISCOGS_USERS_WANT"] = masterUserStats["DISCOGS_USERS_WANT"]
    
    return tags


    
def writeTagsToSongs(songPaths, masterReleaseTags):
    
    try:
        for songPath in songPaths:
            audioFile = mutagen.File(songPath)
            audioFile['genre'] = masterReleaseTags['genres']
            audioFile['date'] = str(masterReleaseTags['date'])
            audioFile["DISCOGS_RATING"] = masterReleaseTags["DISCOGS_RATING"]
            audioFile["DISCOGS_VOTES"] = masterReleaseTags["DISCOGS_VOTES"]
            audioFile["DISCOGS_USERS_HAVE"] = masterReleaseTags["DISCOGS_USERS_HAVE"]
            audioFile["DISCOGS_USERS_WANT"] = masterReleaseTags["DISCOGS_USERS_WANT"]
            
            audioFile.save()
            print("Master release tags set successfully for song: ", songPath)
            
    except Exception as e:
        print("Failed to write master release tags to the song: ", songPath)
        print("Aborting writing tags for the rest of the songs on this album")
        print("Error was ", str(e))
    

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("musicDir", help="The root directory of the music library")
    args = parser.parse_args()    
    musicDir = args.musicDir
    
    erroredArtistAlbumSongs = []
    
    printScriptIntro()
    
    print("Loading and grouping all artists, albums, and songs...")
    allArtistsAlbumSongs = getAllArtistsAlbumsSongs(musicDir)
    print()
    
    songsCount = countSongs(allArtistsAlbumSongs)
    albumsCount = len(allArtistsAlbumSongs)
    print("All songs loaded and grouped successfully")
    print(songsCount, " songs found in ", albumsCount, " albums")
    print()
    
    print("Initializing the Discogs client...")
    client = auth.getDiscogsClient()
    
    print("BEGIN PROCESSING: Finding and setting the master release tags for all songs in all albums...")
    print()
    for artistAlbumSongs in allArtistsAlbumSongs:
        albumReleaseId = getReleaseIdForAlbum(artistAlbumSongs)
        
        if (not albumReleaseId):
            erroredArtistAlbumSongs.append(artistAlbumSongs)
            continue
        
        masterReleaseTags = getMasterReleaseTagsFromNonMasterReleaseId(client, albumReleaseId)
        
        if (not masterReleaseTags):
            erroredArtistAlbumSongs.append(artistAlbumSongs)
            continue
            
        print(masterReleaseTags)
        albumSongPaths = artistAlbumSongs['albumSongPaths']
        
        writeTagsToSongs(albumSongPaths, masterReleaseTags)
        print("Master release tags set successfully for all songs in album: ", artistAlbumSongs['album'])
        print("------------------------------------------------------------------------------------------------------------------- Sleeping for 6 seconds")
        time.sleep(6)
    
    print('########################################################################################################################')
    print()
    print("All songs in the music library processed")
    print(len(erroredArtistAlbumSongs), " albums had an error in finding the master tags. See errored albums below:")
    print()
    
    for errorAlbum in erroredArtistAlbumSongs:
        print("Artist: ", errorAlbum['artist'], "Album: ", errorAlbum['album'], "Songs: ")
        
        for song in errorAlbum['albumSongPaths']:
            print(getDeepestObjectInPath(song))
        
        print("----------------------------------------------------------------------------------------")
    
    print()    
    print("ALL FINISHED, now leaving this script....")
    print("Bye.")

            
run()


    
