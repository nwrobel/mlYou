'''
Created on Mar 17, 2019

@author: nick.admin
'''

def PrepareScriptsForExecution():
    import sys, os
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    projectRoot = os.path.abspath(os.path.join(scriptPath ,".."))
    sys.path.append(projectRoot)
    