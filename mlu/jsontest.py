from collections import OrderedDict
import json

import cache.io
import tags.playstats

# class MyClass:
#     def __init__(self, name, birthday, job):
#         self.name = name
#         self.birthday = birthday
#         self.job = job

#     def PrepareForJSON(self):
#         classDataDict = OrderedDict()
#         classDataDict['name'] = self.name
#         classDataDict['birthday'] = self.birthday
#         classDataDict['job'] = self.job

#         return classDataDict


# def WriteObjListToJSONFile(objList, outputFilename):
#     with open(outputFilename, 'w+') as outfile:
#         json.dump(objList, outfile, default=MyClass.PrepareForJSON)

# def LoadJsonListToObjects():
#     with open('jsontestout.json', 'r') as file:
#         jlist = json.load(file)
        
#     objList = []
#     for jobj in jlist:
#         objList.append( MyClass(**jobj) )
 
#     print(objList[0].name)


if __name__ == "__main__":
    # classList = []

    # classList.append( MyClass("bob", "27th", "programmer") )
    # classList.append( MyClass("joe", "16th", "lel") )
    # classList.append( MyClass("jon", "9th", "topper") )
    # classList.append( MyClass("fon", "7th", "kekker") )


    # LoadJsonListToObjects()

    tag1 = tags.playstats.SongPlaystatTags("C:\\sdf\\ell.mp3", 2, 234344352345, [234527352000, 234524352345])
    tag2 = tags.playstats.SongPlaystatTags("C:\\sdf\\song.mp3", 2, 234994352345, [234534352000, 234994352345])
    tag3 = tags.playstats.SongPlaystatTags("C:\\sdf\\song.mp3", 2, 234524882345, [234524382000, 234524882345])
    tagList = [tag1, tag2, tag3]

    cache.io.WriteMLUObjectsToJSONFile(tagList, "jsontest3.json")
    cache.io.WriteMLUObjectsToJSONFile(tag1, "jsontest6.json")


    print("tag list")
    tagListReadBack = cache.io.ReadMLUObjectsFromJSONFile(tagList, tags.playstats.SongPlaystatTags, "jsontest3.json")
    for tag in tagListReadBack:
        print(tag)
        print(tag.songFilepath)

    print("single tag")
    tagReadBack = cache.io.ReadMLUObjectsFromJSONFile(tag1, tags.playstats.SongPlaystatTags, "jsontest6.json")
    for tag in tagReadBack:
        print(tag)
        print(tag.songFilepath) 