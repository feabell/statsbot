#slack api calls

from slackclient import SlackClient
import json

# create an instance of the api client and initialize it with a token
def init(token):
    global api_client
    api_client = SlackClient(token)
    return api_client

def getFullname(userid):
	return  json.loads(api_client.api_call('users.info', user=userid))['user']['profile']['real_name']

