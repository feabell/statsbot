#slack api calls

from slackclient import SlackClient
import json

# create an instance of the api client and initialize it with a token
def init(token):
    global api_client
    api_client = SlackClient(token)
    return api_client

def getFullname(userid):
    return api_client.api_call('users.info', user=userid).get('user').get('profile').get('real_name')

def getUsername(userid):
    return  api_client.api_call('users.info', user=userid).get('user').get('name')

def sendRR(input):
    api_client.api_call('chat.postMessage', channel='#rapid-response', text=input, as_user=True)

def sendPM(input, userid):
    api_client.api_call('chat.postMessage', channel="@"+getUsername(userid), text=input, as_user=True)

def sendToChannel(input, channel):
    api_client.api_call('chat.postMessage', channel=channel, text=input, as_user=True)

def sendMessage():
    api_client.api_call('chat.postMessage', channel='#Testing', text='<http://google.com|test>', as_user=True)

def userInChannel(channel, user):
    channelInfo = api_client.api_call('groups.info', channel=channel)

    if user in channelInfo['group']['members']:
        return True

    return False
