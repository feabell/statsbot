import os, threading, sys, sqlite3

import eveapi
import zkbapi
import fleetapi
import slackapi
import yaml
import os

config = yaml.load(file('plugins/stats/statsbot.conf', 'r'))
token = config["SLACK_TOKEN"]

api_client = slackapi.init(token)

outputs = []
crontable = []

#poll for new kills every 10minutes
crontable.append([600, "autokill"])

killChannelId = "C04MCGR8Y"

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
    	text = data["text"]
	print data

	#if channel.startswith("D"): # or channel.startswith("C"):
	if text.startswith("!sb") or text.startswith("!statsbot"):
		blob = text.split()

		if len(blob) < 2:
			outputs.append([channel, "Not enough arguments supplied, type !sb help to see a list of commands."])		
			return

		command = blob[1]
		
		if command.startswith("help"):
			outputs.append([channel, "!sb lastkill || shows the lastkill reported in #kills\r\n"+
						 "!sb events || list events on the WDS in-game calendar\r\n"+
						 "!sb srp || view the current status of the WDS SRP wallet"])
		elif command.startswith("lastkill"):
			outputs.append([channel, zkbapi.getLastKill()])	
		elif command.startswith("events"):
			outputs.append([channel, eveapi.getEvents()])	
		elif command.startswith("srp"):
			outputs.append([channel, eveapi.getSRP()])	
		elif command.startswith("fleet"):
			if not channel.startswith("D"):
				outputs.append([channel, "This command cannot be ran in this channel"])
				return

			subcomm = blob[2]
			if subcomm.startswith("new"):
				#grab the description by compounding together all entries after 2
				description = ' '.join(blob[3:])
				outputs.append([channel, fleetapi.newFleet(slackapi.getFullname(user), description)])	
		elif command.startswith("testme"):
			slackapi.sendMessage()
		elif command.startswith("xxxxzzzz"):
			outputs.append([channel, zkbapi.getLastKill()])	
		elif command.startswith("xxxxdddd"):
			outputs.append([channel, zkbapi.getLastKill()])	
		elif command.startswith("xxxxeeee"):
			outputs.append([channel, zkbapi.getLastKill()])	


def autokill():
	print "autokill: polling for new kills"
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
			print "autokill: updating latest kill to " + killIdInt

			cur.execute('update lastkillid set id = '+killIdInt)
			con.commit()



