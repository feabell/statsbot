import os, threading, sys, sqlite3

import eveapi
import zkbapi
#import slackapi

outputs = []
crontable = []

#poll for new kills every 10minutes
crontable.append([600, "autokill"])

killChannelId = "C04MCGR8Y"

def process_message(data):
	#stop the bot from barfing out for events without a text chunk (event_ts chunks happen with unfurled links)
	if not 'text' in data:
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
			outputs.append([channel, "help messages goes here"])
		elif command.startswith("lastkill"):
			outputs.append([channel, zkbapi.getLastKill()])	
		elif command.startswith("events"):
			outputs.append([channel, eveapi.getEvents()])	
		elif command.startswith("xxxxbbbb"):
			outputs.append([channel, zkbapi.getLastKill()])	
		elif command.startswith("xxxxvvvv"):
			outputs.append([channel, zkbapi.getLastKill()])	
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



