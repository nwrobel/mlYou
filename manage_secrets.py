import argparse
from mlu import common

DISCOGS_AUTH_FILEPATH =  common.getProjectRoot() + 'mlu/discogs/auth.py'

def removeSecrets():
    
    print("Removing secrets from", DISCOGS_AUTH_FILEPATH)
    with open(DISCOGS_AUTH_FILEPATH, 'r') as file :
        filedata = file.readlines()
    
    for index, line in enumerate(filedata):
        if ("USER_AGENT =" in line):
            filedata[index] = "USER_AGENT = <censored>\n"
        
        elif ("CONSUMER_KEY =" in line):
            filedata[index] = "CONSUMER_KEY = <censored>\n"
            
        elif ("CONSUMER_SECRET =" in line):
            filedata[index] = "CONSUMER_SECRET = <censored>\n"
        
        elif ("OAUTH_TOKEN =" in line):
            filedata[index] = "OAUTH_TOKEN = <censored>\n"
            
        elif ("OAUTH_TOKEN_SECRET =" in line):
            filedata[index] = "OAUTH_TOKEN_SECRET = <censored>\n"
           
    # Write the file out again
    with open(DISCOGS_AUTH_FILEPATH, 'w') as file:
        file.writelines(filedata)
    
    print("Secrets removed successfully")
        
def restoreSecrets(secrets): 

    print("Restoring secrets to", DISCOGS_AUTH_FILEPATH)
    
    with open(DISCOGS_AUTH_FILEPATH, 'r') as file :
        filedata = file.readlines()
    
    for index, line in enumerate(filedata):
        if ("USER_AGENT =" in line):
            filedata[index] = "USER_AGENT = '" + secrets[0] + "'\n"
        
        elif ("CONSUMER_KEY =" in line):
            filedata[index] = "CONSUMER_KEY = '" + secrets[1] + "'\n"
            
        elif ("CONSUMER_SECRET =" in line):
            filedata[index] = "CONSUMER_SECRET = '" + secrets[2] + "'\n"
        
        elif ("OAUTH_TOKEN =" in line):
            filedata[index] = "OAUTH_TOKEN = '" + secrets[3] + "'\n"
            
        elif ("OAUTH_TOKEN_SECRET =" in line):
            filedata[index] = "OAUTH_TOKEN_SECRET = '" + secrets[4] + "'\n"
     
    # Write the file out again
    with open(DISCOGS_AUTH_FILEPATH, 'w') as file:
        file.writelines(filedata)
        
    print("Secrets restored successfully")

def run():
   
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=['remove','restore'], help="What to do with the code's secrets ('Remove' or 'Restore')")
    parser.add_argument('--secrets', nargs='+', dest='secrets', help='List of secrets values to be restored, seperated by a space, in the order: USER_AGENT, CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET')
    args = parser.parse_args()

    action = args.action 
    secrets = args.secrets 
    
    if (action == 'remove'):
        removeSecrets()
    else:
        if (secrets):
            restoreSecrets(secrets)
        else:
            print("Error: must pass in --secrets if we are going to restore them")
    


run()