#zkillboard api calls

from random import randint
import requests
import json
import pprint
import eveapi

toSlack = ""
killid = 0


def getLastKill():
	global toSlack
	global killid

	rnd = str(randint(0,9)) 
	url = 'https://zkillboard.com/api/kills/corporationID/98330748/limit/'+rnd+'/no-items/'

	j = json.loads(requests.get(url).text)
	
	#pp = pprint.PrettyPrinter(indent=4)
	#pp.pprint(j[0])

	blob = j[0]

	#grab stuff from the blob
	#generic info
	
	killidint = blob['killID']
	if (killidint > killid):
		killid = killidint

		v = blob['victim']
		a = blob['attackers'][0]
		system = eveapi.getSystem(str(blob['solarSystemID']))
		killurl = "https://zkillboard.com/kill/"+str(killidint)+"/"	
		shipvalue = str(round(blob['zkb']['totalValue']/1000000, 2))
		killtime = blob['killTime']
		pilotcount = str(len(blob['attackers']) - 1)
	
		#victim info
		victim = v['characterName']
		corp = v['corporationName']
		alliance = v['allianceName']
		ship = eveapi.getShip(str(v['shipTypeID']))
		
		#attacker info
		pilot = a['characterName']

		toSlack = victim +"("+ corp +") lost their "+ ship +" worth "+ shipvalue +"m to "+ pilot +"(and "+ pilotcount + " others) in "+ system +" at "+ killtime +". "+ killurl 

	print toSlack

	return toSlack
	
