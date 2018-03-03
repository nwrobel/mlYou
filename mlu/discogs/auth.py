import discogs_client
import sys
from discogs_client.exceptions import HTTPError

USER_AGENT = <censored>
CONSUMER_KEY = <censored>
CONSUMER_SECRET = <censored>
OAUTH_TOKEN = <censored>
OAUTH_TOKEN_SECRET = <censored>


def getDiscogsClient():
    client = discogs_client.Client(USER_AGENT, CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    return client

def printSecretsInfoForNewDiscogsClient():
    # Modified from:
    # https://github.com/jesseward/discogs-oauth-example/blob/master/discogs_client_example.py
    
    discogsclient = discogs_client.Client(USER_AGENT)
    
    discogs_client.Client(USER_AGENT)
    
    # prepare the client with our API consumer data.
    discogsclient.set_consumer_key(CONSUMER_KEY, CONSUMER_SECRET)
    token, secret, url = discogsclient.get_authorize_url()
    
    print (" == Request Token == ")
    print ("    * oauth_token        = {}".format(token))
    print ("    * oauth_token_secret = {}".format(secret))
    print ()
    
    print ("Please browse to the following URL {}".format(url))
    
    accepted = 'n'
    while accepted.lower() == 'n':
        print
        accepted = input('Have you authorized me at {} [y/n] :'.format(url))
    
    
    # Waiting for user input. Here they must enter the verifier key that was
    # provided at the unqiue URL generated above.
    oauth_verifier = input('Verification code :') #.decode('utf8')
    
    try:
        access_token, access_secret = discogsclient.get_access_token(oauth_verifier)
    except HTTPError:
        print ("Unable to authenticate.")
        sys.exit(1)
    
    # fetch the identity object for the current logged in user.
    user = discogsclient.identity()
    
    print ()
    print (' == User ==')
    print ('    * username           = {}'.format(user.username))
    print ('    * name               = {}'.format(user.name))
    print ('    * user_agent           {}').format(USER_AGENT)
    print (' == Consumer Secrets ==')
    print ('    * consumer_key       = {}').format(CONSUMER_KEY)
    print ('    * consumer_secret    = {}').format(CONSUMER_SECRET)
    print (' == Access Token ==')
    print ('    * oauth_token        = {}'.format(access_token))
    print ('    * oauth_token_secret = {}'.format(access_secret))
    print ()
    print ('Now, to make a client, input the following info printed above into the constructor:')
    print ('    discogs_client.Client(user_agent, consumer_key, consumer_secret, oauth_token, oauth_token_secret)')
        


