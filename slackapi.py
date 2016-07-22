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

def getUsername(userid):
	return  json.loads(api_client.api_call('users.info', user=userid))['user']['name']

def sendRR(input):
	api_client.api_call('chat.postMessage', channel='#rapid-response', text=input, as_user=True)

def sendPM(input, userid):
	api_client.api_call('chat.postMessage', channel="@"+getUsername(userid), text=input, as_user=True)


def sendMessage():
	api_client.api_call('chat.postMessage', channel='#Testing', text='<http://google.com|test>', as_user=True)
