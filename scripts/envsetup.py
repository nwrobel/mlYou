'''
Created on Mar 17, 2019

@author: nick.admin

This file contains initialization code, which is used by scripts in the folder to setup project
variables and paths so that this project's modules can be used.
'''


def PreparePythonProjectEnvironment():
    import sys, os
    
    # Add project root to PYTHONPATH so MLU modules can be imported
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    projectRoot = os.path.abspath(os.path.join(scriptPath ,".."))
    sys.path.append(projectRoot)
    
    # Activate the virtual environment, so you can import libraries in the virtualenv
    activateThisFilepath = os.path.join(projectRoot, "py-venv/Scripts/activate_this.py")
    exec(open(activateThisFilepath).read(), {'__file__': activateThisFilepath})