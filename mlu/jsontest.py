from collections import OrderedDict
import json

class MyClass:
    def __init__(self, name, birthday, job):
        self.name = name
        self.birthday = birthday
        self.job = job

    def PrepareForJSON(self):
        classDataDict = OrderedDict()
        classDataDict['name'] = self.name
        classDataDict['birthday'] = self.birthday
        classDataDict['job'] = self.job

        return classDataDict


def WriteObjListToJSONFile(objList, outputFilename):
    with open(outputFilename, 'w+') as outfile:
        json.dump(objList, outfile, default=MyClass.PrepareForJSON)

def LoadJsonListToObjects():
    with open('jsontestout.json', 'r') as file:
        jlist = json.load(file)
        
    objList = []
    for jobj in jlist:
        objList.append( MyClass(**jobj) )
 
    print(objList[0].name)




if __name__ == "__main__":
    classList = []

    classList.append( MyClass("bob", "27th", "programmer") )
    classList.append( MyClass("joe", "16th", "lel") )
    classList.append( MyClass("jon", "9th", "topper") )
    classList.append( MyClass("fon", "7th", "kekker") )


    LoadJsonListToObjects()



