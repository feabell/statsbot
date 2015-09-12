#eve api calls

import requests
import json

def getSystem(systemID):
	url = "https://public-crest.eveonline.com/solarsystems/"+systemID+"/"
	
	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['name']
	except:
		print "couldn't connect to crest"

	return name

def getShip(shipID):
	url = "https://public-crest.eveonline.com/types/"+shipID+"/"

	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['name']
	except:
		print "couldn't connect to crest"

	return name
