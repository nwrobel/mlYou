'''
Created on Dec 26, 2018

@author: nick.admin
'''

import discogs_client
from mlu import common

class DiscogsAPIConnection(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        self.client = self.createClient()
        
    
    def CreateClient(self):
        discogsClientAppName = 'mlyou/0.1'
        userTokenFilepath = common.getProjectRoot() + 'user-token.txt'
    
        with open(userTokenFilepath, 'r') as file :
            token = file.read()
            
        discogsClient = discogs_client.Client(discogsClientAppName, user_token=token)
        
        return discogsClient
        