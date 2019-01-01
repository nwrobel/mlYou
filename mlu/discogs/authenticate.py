'''
Created on Dec 26, 2018

@author: nick.admin
'''

import discogs_client
from mlu import common

def GetClient():
    
    discogsClientAppName = 'mlyou/0.1'
    userTokenFilepath = common.getProjectRoot() + 'user-token.txt'
    
    with open(userTokenFilepath, 'r') as file :
        token = file.read()
        
    discogsClient = discogs_client.Client(discogsClientAppName, user_token=token)
    
    return discogsClient


client = GetClient()
r = client.search(type='master', release_title='The Fragile', artist='Nine Inch Nails')
print('hi')
print(r[0])
# r[0].data['community']