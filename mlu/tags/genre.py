import os
import argparse
import mutagen


def getAllFilesRecursive(rootPath):
    
    allFiles = []
    
    for path, subdirs, files in os.walk(rootPath):
        for name in files:
            theFile = os.path.join(path, name)
            print (theFile)
            allFiles.append(theFile)
            
    return allFiles
            

def run():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("musicDir", help="The root directory of the music library")
    args = parser.parse_args()
    
    musicDir = args.musicDir
    
    allMusicFilePaths = getAllFilesRecursive(musicDir)
    
    for musicFilePath in allMusicFilePaths:
        audioFile = mutagen.File(musicFilePath)
        
        try:
            songGenre = audioFile['genre']
        
        except KeyError:
            print("Error parsing the tag 'genre' for file ", musicFilePath, ".....Does it exist?")
            continue
        
        try:
            songStyle = audioFile['style']
            
        except KeyError:
            print("Error parsing the tag 'style' for file ", musicFilePath, ".....Does it exist?")
            continue
        
        try:
            newSongGenre = songGenre + songStyle
            
            audioFile['genre'] = newSongGenre
            audioFile.save()
            
            print("New genre written successfully for file: ", musicFilePath)
            
        except:
            print("Error writing the new 'genre' tag for file ", musicFilePath)
    
run()
