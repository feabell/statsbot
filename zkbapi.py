#zkillboard api calls

from random import randint
import requests
import json
import pprint
import eveapi
import logging
import sys

toSlack = ""
killid = 0
allianceId = "99006319"
headers = {'user-agent': 'WiNGSPAN Slack webhook (all kill tracker 10min poll) feabell@gmail.com'}


def getNewKills(ignore):

# Don't need the arguement anymore, so we ignore it if it's passed


	global headers, allianceId

	kill = ""
	killmail = ""
	pkg = ""
	attkrs = ""
	alliance = ""
	allId = ""
	data = []

#	URL to use RedisQ on zkill to get killmails. 
#	- ttw param specifies the wait time - the server will return an empty result
#	  if there no new kills arrive in ttw seconds (default is 10)
#	- queueID parameter provides a string to the server to track kills sent. Default
#	  is to use the client IP address. Server will only send kills it hasn't already sent
#	  (going back 3 hours)
	url = 'https://redisq.zkillboard.com/listen.php?ttw=1&queueID=WDS9906319'

#	To prevent a runaway loop for pulling kills. Server sends just one kill per request
#	so we loop to get all available, up to this maximum
	safety = 101


	for n in range(1, safety):
		try:
			pkg =  json.loads(requests.get(url, headers=headers).text)
		except:
			logging.info("could not connect to zkb")
			break

		killmail = pkg['package']

#		RedisQ/Readme.md on github says "null" is returned if there are no
#		new kills available, but it appears that it's "None" 
		if str(killmail) == "None":
			break

		kill = killmail['killmail']

#		Select kills where Wingspan alliance is among the attackers
		attkrs = kill['attackers']
		for atkr in attkrs:
			if 'alliance' in atkr:
				alliance = atkr['alliance']

#				There are odd cases where there is no "id_str" for an alliance
				if 'id_str' in alliance:
					allId = alliance['id_str']
					if allId == allianceId:
						data.append( killmail )
						break

	return data

		

# Parse the killmail format as provided by redisq.zkillboard.com
def parseKill(killmail):
	kill = killmail['killmail']
	killIdInt = kill['killID']
	v = kill['victim']
		
	#grab the primary attacker as the pilot in the attackers array with the finalBlow attribute set
	a = filter(checkFinalBlow,kill['attackers'])[0]
		
	#grab stuff from the kill json blob
	#generic info
	system = "unknown"
	if 'solarSystem' in kill:
		if 'name' in kill['solarSystem']:
			system = kill['solarSystem']['name']
		else:
			if 'id_str' in kill['solarSystem']:
				system = eveapi.getSystem(str(kill['solarSystem']['id_str']))
	killurl = "https://zkillboard.com/kill/"+str(killIdInt)+"/"	
	shipvalue = str(round(killmail['zkb']['totalValue']/1000000, 2))
	killtime = kill['killTime']
	pilotcount = str(len(kill['attackers']) - 1)

	#victim info
	victim = "unknown"
	if 'character' in v:
		if 'name' in v['character']:
			victim = v['character']['name']
	corp = "unknown"
	if 'corporation' in v:
		if 'name' in v['corporation']:
			corp = v['corporation']['name']
#	alliance = v['allianceName']
	ship = "unknown"
	if 'shipType' in v:
		if 'name' in v['shipType']:
			ship = v['shipType']['name']
		else:
			if 'id_str' in v['shipType']:
				ship = eveapi.getShip(str(v['shipType']['id_str']))
		
	#attacker info
	pilot = "unknown"
	if 'character' in a:
		if 'name' in a['character']:
			pilot = a['character']['name']

	message = victim +"("+ corp +") lost their "+ ship +" worth "+ shipvalue +"m to "+ pilot +"(and "+ pilotcount + " others) in "+ system +" at "+ killtime +". "+ killurl 
	
	return message


# parse the kiallmail format as provided by zkillboard.com/api/kills
def parseKillZkApi(kill):
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

	rnd = str(randint(0,9)) 
	url = 'https://zkillboard.com/api/kills/alliance/' + allianceId + '/limit/'+rnd+'/no-items/'

	toSlack = ''
	
	try:
		j = json.loads(requests.get(url, headers=headers).text)

		blob = j[0]
		killidint = blob['killID']
		if (killidint > killid):
			killid = killidint
			toSlack = parseKillZkApi(blob)
	
		logging.info("lastkill: responded for killid " + str(killidint))
	except Exception as e:
		logging.info("could not connect to zkb")

	return toSlack

def checkFinalBlow(element):
	if element['finalBlow'] == 1:
		return element
	
