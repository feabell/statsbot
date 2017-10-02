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


def getNewKills():

	global headers, allianceId

	logging.getLogger("requests").setLevel(logging.WARNING)	

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

#		new kills available, but it appears that it's "None" 
		if str(killmail) == "None":
			break

		kill = killmail['killmail']

#		Select kills where Wingspan alliance is among the attackers
		attkrs = kill['attackers']
		for atkr in attkrs:
			if 'alliance_id' in atkr:
 				if str(atkr['alliance_id']) == allianceId:
					data.append(killmail)
					break

		#	if 'alliance' in atkr:
		#		alliance = atkr['alliance']

#				There are odd cases where there is no "id_str" for an alliance
		#		if 'id_str' in alliance:
	#				allId = alliance['id_str']
	#				if allId == allianceId:
	#					data.append( killmail )
	#					break

	return data

		

# Parse the killmail format as provided by redisq.zkillboard.com
def parseKill(killmail):
        if 'killmail' in killmail:
		kill = killmail['killmail']
	else:
		kill = killmail

	killIdInt = kill['killmail_id']
	v = kill['victim']
		
	#grab the primary attacker as the pilot in the attackers array with the finalBlow attribute set
	a = filter(checkFinalBlow,kill['attackers'])[0]
		
	#grab stuff from the kill json blob
	#generic info
	system = "unknown"
	if 'solar_system_id' in kill:
		system = eveapi.getSystem(str(kill['solar_system_id']))
	killurl = "https://zkillboard.com/kill/"+str(killIdInt)+"/"	
	shipvalue = str(round(killmail['zkb']['totalValue']/1000000, 2))
	killtime = kill['killmail_time']
	pilotcount = str(len(kill['attackers']) - 1)

	#victim info
	victim = "unknown"
	if 'character_id' in v:
		victim = eveapi.getCharacter(str(v['character_id']))
	corp = "unknown"
	if 'corporation_id' in v:
		corp = eveapi.getCorporation(str(v['corporation_id']))
	ship = "unknown"
	if 'ship_type_id' in v:
		ship = eveapi.getShip(str(v['ship_type_id']))
		
	#attacker info
	pilot = "unknown"
	if 'character_id' in a:
		pilot = eveapi.getCharacter(str(a['character_id']))

	message = victim +"("+ corp +") lost their "+ ship +" worth "+ shipvalue +"m to "+ pilot +"(and "+ pilotcount + " others) in "+ system +" at "+ killtime +". "+ killurl 
	
	logging.info("Kill logged for " + killurl)
	
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
		killidint = blob['killmail_id']
		if (killidint > killid):
			killid = killidint
		
		toSlack = parseKill(blob)
	
		logging.info("lastkill: responded for killid " + str(killidint))
	except Exception as e:
		logging.info("could not connect to zkb")

	return toSlack

def checkFinalBlow(element):
	if element['final_blow'] == True:
		return element
	
