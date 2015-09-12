#eve api calls

import requests
import json

def getSystem(systemID):
	url = "https://public-crest.eveonline.com/solarsystems/"+systemID+"/"
	
	name = ''
	with requests.get(url).text as getdata:
		name = json.loads(getdata)['name']

	return name

def getShip(shipID):
	url = "https://public-crest.eveonline.com/types/"+shipID+"/"

	name = ''
	with requests.get(url).text as getdata:
		name = json.loads(getdata)['name']

	return name
