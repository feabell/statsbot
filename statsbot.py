import os, threading, sys, sqlite3

import eveapi
import zkbapi
import fleetapi
import slackapi
import recruitment
import yaml
import os
import logging
from time import gmtime, strftime

config = yaml.load(file('plugins/stats/statsbot.conf', 'r'))
token = config["SLACK_TOKEN"]

api_client = slackapi.init(token)

#logging.basicConfig(filename='/tmp/statsbot.log', level=logging.INFO)

outputs = []
crontable = []

#poll for new kills every 10minutes
crontable.append([600, "autokill"])
#poll for new recruits every 1minutes
crontable.append([60, "autorec"])
#poll for members approaching the end of their trial, every 24hours
crontable.append([86400, "autotrial"])
#poll for new members in the last 24 hours
crontable.append([86400, "autonew"])

killChannelId = "C04MCGR8Y"
testChannelId = "C04N5P17B"
recruitChannelId = "G04NGUDHF"
generalChannelId = "C04L6NKQ3"

logging.info('Statsbot started')

def process_message(data):
	#stop the bot from barfing out for events without a text, channel  or user chunk (event_ts chunks happen with unfurled links)
	if not 'text' in data:
		return
	if not 'user' in data:
		return
	if not 'channel' in data:
		return

	channel = data["channel"]
	user = data["user"]
	username = slackapi.getFullname(user)
    	text = data["text"].lower()
	#print data

	#if channel.startswith("D"): # or channel.startswith("C"):
	if text.startswith("!sb") or text.startswith("!statsbot"):
		blob = text.split()

		if len(blob) < 2:
			outputs.append([channel, "Not enough arguments supplied, type !sb help to see a list of commands."])		
			return

		command = blob[1]
		
		if command.startswith("help"):
			logging.info('help command received from ' + username)
			outputs.append([channel, "!sb lastkill || shows the lastkill reported in #kills\r\n"+
						 "!sb events || list events on the WDS in-game calendar\r\n"+
						 "!sb srp || view the current status of the WDS SRP wallet\r\n"+
						 "!sb rr <your message here> || post a request for a fleet or forump message to #rapid-response"])
		elif command.startswith("lastkill"):
			logging.info('lastkill command received from ' + username)
			outputs.append([channel, zkbapi.getLastKill()])	
		elif command.startswith("events"):
			logging.info('events command received from ' + username)
			outputs.append([channel, eveapi.getEvents()])	
		elif command.startswith("srp"):
			logging.info('srp command received from ' + username)
			outputs.append([channel, eveapi.getSRP()])	
		elif command.startswith("fleet"):
			logging.info('fleet command received from ' + username)
			if not channel.startswith("D"):
				outputs.append([channel, "This command cannot be ran in this channel"])
				return

			subcomm = blob[2]
			if subcomm.startswith("new"):
				#grab the description by compounding together all entries after 2
				description = ' '.join(blob[3:])
				outputs.append([channel, fleetapi.newFleet(username, description)])	
		elif command.startswith("testme"):
			logging.info('testme v2 command received from ' + username)
			#slackapi.sendMessage()
			#slackapi.sendPM("did this work?", user)
		elif command.startswith("recruit"):
			logging.info('recruit command received from ' + username)
			if not (channel.startswith(recruitChannelId) or slackapi.userInChannel(recruitChannelId, user)):
				outputs.append([channel, "This command cannot be ran in this channel"])
				return

			subcomm = blob[2]

			if subcomm == "help":
				helptext = "!sb recruit list\r\n"
				helptext+= "!sb recruit list <recruits|invited|inducted|rejected|trial> <full>\r\n" 
				helptext+= "!sb recruit list <id> <full>\r\n"
				helptext+= "!sb recruit <invite|induct|reject> <id>\r\n"
				outputs.append([channel, helptext])
				return

			if subcomm == "list":
				if len(blob) == 3:
					targetcomm = "recruits"
				else:
					targetcomm = blob[3]

				showFull=False

				if len(blob) >= 5: 
				  if blob[4] == "full":
					showFull=True
				if targetcomm.isdigit():
					#list a specific recruit
					slackapi.sendToChannel(recruitment.list(recid=targetcomm, showfull=showFull), channel)
				elif targetcomm == "recruits":
					#list all waiting recruits
					slackapi.sendToChannel(recruitment.list(recruits=True, showfull=showFull), channel)
				elif targetcomm == "invited":
					#list invited
					slackapi.sendToChannel(recruitment.list(invited=True, showfull=showFull), channel)
				elif targetcomm == "inducted":
					#list invited
					slackapi.sendToChannel(recruitment.list(inducted=True,  showfull=showFull), channel)
				elif targetcomm == "rejected":
					#list invited
					slackapi.sendToChannel(recruitment.list(rejected=True, showfull=showFull), channel)
				elif targetcomm == "trial":
					#list trial users 
					slackapi.sendToChannel(recruitment.list(trial=True), channel)
				elif targetcomm == "endtrial":
					#list trial users 
					slackapi.sendToChannel(recruitment.list(endOfTrial=True), channel)
			elif subcomm.startswith("induct"):
				#mark selected recruits as inducted and needing an invite
				recruitment.update(1, blob[3:], username)
				slackapi.sendToChannel('Recruit(s) '+ ''.join(blob[3:]) +' marked as inducted by ' + username, recruitChannelId)
			elif subcomm.startswith("invite"):
				#mark selected recruits as invited
				recruitment.update(2, blob[3:], username)
				slackapi.sendToChannel('Recruit(s) '+ ''.join(blob[3:]) +' marked as invited by ' + username, recruitChannelId)
			elif subcomm.startswith("reject"):
				#mark selected recruits as rejected
				recruitment.update(3, blob[3:], username)
				slackapi.sendToChannel('Recruit(s) '+ ''.join(blob[3:]) +' marked as rejected by ' + username, recruitChannelId)
			else:
				outputs.append([channel, "Unknown command"])


		elif command.startswith("rr"):
			logging.info('rr command received from ' + username)
			if not channel.startswith("D"):
				slackapi.sendPM("You can't send rapid reponses from channels, try copying and pasting the message (starting '!sb rr...')  in here instead!",
						user)
				return

			currtime = strftime('%H:%M %d-%m', gmtime())
			rr = ' '.join(blob[2:])
			message = 'Rapid Response by '+username+' at '+currtime+' (eve time):\r\n'+rr
			slackapi.sendRR(message)

def autokill():
	logging.info("autokill: polling for new kills")
	#grab the lastKillId from sqlite
	dir_path = os.path.dirname(os.path.abspath(__file__))
	con = sqlite3.connect(os.path.join(dir_path, 'statsbot.db'))

	with con:
		cur = con.cursor()
		cur.execute('select id from lastkillid')

		lastKillId = str(cur.fetchone()[0])
		kills = zkbapi.getNewKills(lastKillId)

		for kill in kills:
			killIdInt = str(kill['killID'])
			outputs.append([killChannelId, zkbapi.parseKill(kill)])
			logging.info("autokill: updating latest kill to " + killIdInt)

			cur.execute('update lastkillid set id = '+killIdInt)
			con.commit()


def autorec():
	logging.info("autorec: polling for new recruits")
	
	dir_path = os.path.dirname(os.path.abspath(__file__))
	con = sqlite3.connect(os.path.join(dir_path, 'statsbot.db'))

	with con:
		cur = con.cursor()
		cur.execute('select id from lastrecruitid')

		lastRecId = str(cur.fetchone()[0])
		recruits = recruitment.getNew(lastRecId)

		if len(recruits) >=1:
  		  slackapi.sendToChannel("New recruits!", recruitChannelId)

		  for recruit in recruits:
			recIdInt = str(recruit['id'])
			slackapi.sendToChannel(recruitment.list(recid=recIdInt), recruitChannelId)
			logging.info("autorec: updating latest recruit to " + recIdInt)

			cur.execute('update lastrecruitid set id = '+recIdInt)
			con.commit()


def autotrial():
	logging.info("autotrial: polling for members nearing the end of their trial period")

	slackapi.sendToChannel(recruitment.list(endOfTrial=True), recruitChannelId)
	
def autonew():
	logging.info("autonew: polling for new members in the last 24hours")

	slackapi.sendToChannel(recruitment.newMembers(), generalChannelId)


