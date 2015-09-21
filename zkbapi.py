#zkillboard api calls

from random import randint
import requests
import json
import pprint
import eveapi

toSlack = ""
killid = 0
headers = {'user-agent': 'WiNGSPAN Slack webhook (all kill tracker 10min poll) feabell@gmail.com'}

def getNewKills(lastKillId):
	global headers
	data = ""
	url = 'https://zkillboard.com/api/kills/corporationID/98330748/no-items/afterKillID/' + lastKillId + '/orderDirection/asc/';

	try:
		data = json.loads(requests.get(url, headers=headers).text)
	except:
		print "could not connect to zkb"

	return data
		

def parseKill(kill):
	killIdInt = kill['killID']
	v = kill['victim']
		
	#grab the primary attacker as the pilot in the attackers array with the finalBlow attribute set
	a = filter(checkFinalBlow,kill['attackers'])[0]
		
	#grab stuff from the kill json blob
	#generic info
	system = eveapi.getSystem(str(kill['solarSystemID']))
	killurl = "https://zkillboard.com/kill/"+str(killIdInt)+"/"	
	shipvalue = str(round(kill['zkb']['totalValue']/1000000, 2))
	killtime = kill['killTime']
	pilotcount = str(len(kill['attackers']) - 1)

	#victim info
	victim = v['characterName']
	corp = v['corporationName']
	alliance = v['allianceName']
	ship = eveapi.getShip(str(v['shipTypeID']))
		
	#attacker info
	pilot = a['characterName']

	message = victim +"("+ corp +") lost their "+ ship +" worth "+ shipvalue +"m to "+ pilot +"(and "+ pilotcount + " others) in "+ system +" at "+ killtime +". "+ killurl 
	
	return message


def getLastKill():
	global toSlack
	global killid
	global headers

	print "lastkill: request received"

	rnd = str(randint(0,9)) 
	url = 'https://zkillboard.com/api/kills/corporationID/98330748/limit/'+rnd+'/no-items/'

	toSlack = ''
	
	try:
		j = json.loads(requests.get(url, headers=headers).text)

		blob = j[0]
		killidint = blob['killID']
		if (killidint > killid):
			killid = killidint
			toSlack = parseKill(blob)
	
		print "lastkill: responded for killid " + killidint
	except:
		print "could not connect to zkb"

	return toSlack

def checkFinalBlow(element):
	if element['finalBlow'] == 1:
		return element
	
