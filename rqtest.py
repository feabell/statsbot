import os, threading, sys, sqlite3

import eveapi
import zkbapi
import fleetapi
# import slackapi
# import recruitment
import yaml
import os
import logging
from time import gmtime, strftime

# config = yaml.load(file('plugins/stats/statsbot.conf', 'r'))
# token = config["SLACK_TOKEN"]

# api_client = slackapi.init(token)

#logging.basicConfig(filename='/tmp/statsbot.log', level=logging.INFO)

outputs = []
crontable = []

#poll for new kills every 10minutes
#crontable.append([600, "autokill"])
#poll for new recruits every 1minutes
# crontable.append([60, "autorec"])
#poll for members approaching the end of their trial, every 24hours
# crontable.append([86400, "autotrial"])
#poll for new members in the last 24 hours
#crontable.append([86400, "autonew"])

killChannelId = "C04MCGR8Y"
testChannelId = "C04N5P17B"
recruitChannelId = "G04NGUDHF"
generalChannelId = "C04L6NKQ3"



def autokill():
	logging.info("autokill: polling for new kills")
	#grab the lastKillId from sqlite
#	dir_path = os.path.dirname(os.path.abspath(__file__))
#	con = sqlite3.connect(os.path.join(dir_path, 'statsbot.db'))

	if 1:	# Just to avoid fixing indents from here down
#	with con:
#		cur = con.cursor()
#		cur.execute('select id from lastkillid')

#		lastKillId = str(cur.fetchone()[0])
		lastKillId = 0
		kills = zkbapi.getNewKills(lastKillId)

		for kill in kills:
			if kill == "error":
				continue
#			kill = kill.encode('utf-8')
			logging.info(kill)
			logging.info('1')
#			logging.info(kill['killID'])
			logging.info(type(kill))
			logging.info('2')
			killIdInt = str(kill['killID'])
			print "Kill: ", killIdInt
			print zkbapi.parseKill(kill)
#			outputs.append([killChannelId, zkbapi.parseKill(kill)])
#			logging.info("autokill: updating latest kill to " + killIdInt)

#			cur.execute('update lastkillid set id = '+killIdInt)
#			con.commit()

print zkbapi.getLastKill()

autokill()
