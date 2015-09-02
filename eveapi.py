#eve api calls

import requests
import json

def getSystem(systemID):
	url = "https://public-crest.eveonline.com/solarsystems/"+systemID+"/"

	j = json.loads(requests.get(url).text)

	return j['name']

def getShip(shipID):
	url = "https://public-crest.eveonline.com/types/"+shipID+"/"

	j = json.loads(requests.get(url).text)
	
	return j['name']
