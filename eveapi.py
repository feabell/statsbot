#eve api calls

import requests
import json
import xml.etree.ElementTree as ET
import time
import sys
import yaml
import os
import locale
import logging

def getKey(key):

    prev_dir = os.getcwd()
    os.chdir('plugins/stats')
    config = yaml.load(file('eveapi.conf', 'r'))
    
    try:
    	apikey = config[key]
    except:
	logging.info("no key with name " +key)

    os.chdir(prev_dir)

    return apikey

def getSystem(systemID):
	url = "https://esi.tech.ccp.is/latest/universe/systems/"+systemID+"/?datasource=tranquility&language=en-us"
	
	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['name']
	except:
		logging.info("couldn't connect to ESI (system)")

	return name

def getCharacter(characterID):
	url = "https://esi.tech.ccp.is/latest/characters/names/?character_ids="+characterID+"&datasource=tranquility"
	name = ''
	try:
		blob = json.loads(requests.get(url).text)[0]
		name = blob['character_name']
	except Exception as e:
		logging.info("couldnt resolve with ESI (character name)")

	return name

def getCorporation(corporationID):
	url = "https://esi.tech.ccp.is/latest/corporations/"+corporationID+"/?datasource=tranquility"
	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['corporation_name']
	except:
		logging.info("couldnt resolve with ESI (corporation name)")

	return name

def getShip(shipID):
	url = "https://esi.tech.ccp.is/latest/universe/types/"+shipID+"/?datasource=tranquility&language=en-us"

	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['name']
	except:
		logging.info("couldn't resolve with ESI (ship)")

	return name

def getEvents():
	
	apikey = getKey("CALENDAR")	

	data = apikey.split()
	corpkey = data[0]
	corpvcode = data[1]

	url = "https://api.eveonline.com/char/UpcomingCalendarEvents.xml.aspx?keyID="+corpkey+"&vCode="+corpvcode

	response = ''	
	try:
		root = ET.fromstring(requests.get(url).content)
	
		#grab all of the events from the XML clump, throw them into a list and sort ascending by eventDate	
		sorted_events = sorted(list(root.iter('row')), key=lambda k: k.get('eventDate'))
		
		response += "Upcoming events: \r\n"

		for event in sorted_events:
			title =  event.get('eventTitle')
			text =  event.get('eventText')
			date =  time.strptime(event.get('eventDate'), '%Y-%m-%d %H:%M:%S')

			response += time.strftime('%A %b %d @%H:%M', date) + ': '  + title + " - " + text +'\r\n'

	except:
		logging.info("barfed in XML api", sys.exc_info()[0])
	
	return response

def getBookmarkCount():
	apikey = getKey("BOOKMARKS")

	data = apikey.split()
	corpkey = data[0]
	corpvcode = data[1]

	url = "https://api.eveonline.com/corp/Bookmarks.xml.aspx?keyid="+corpkey+"&vcode="+corpvcode
	#logging.info(url)

	count = 0

	try:
		root = ET.fromstring(requests.get(url).content)

		folders = list(root.find("result").findall("rowset"))		

		for folder in folders:
		        for entry in folder:
	                	bookmarks = list(entry.findall("rowset"))

	                	for bookmark in bookmarks:
        	                	count += len(list(bookmark.findall("row")))
	except:
		logging.info("barfed in XML api", sys.exc_info()[0])

	return count
			
def getBookmarkDetails():
	apikey = getKey("BOOKMARKS")

	data = apikey.split()
	corpkey = data[0]
	corpvcode = data[1]

	url = "https://api.eveonline.com/corp/Bookmarks.xml.aspx?keyid="+corpkey+"&vcode="+corpvcode
	logging.info(url)

	response = 'Bookmarks By Folder\r\n'
	response+= '-------------------------\r\n```'

	try:
		root = ET.fromstring(requests.get(url).content)

		folders = list(root.find("result").findall("rowset"))

		for folder in folders:
		        for entry in folder:
                		foldername = entry.get('folderName')
				if not foldername:
					foldername = "(top level)"

	                	bookmarks = list(entry.findall("rowset"))

	                	for bookmark in bookmarks:
        	                	count = len(list(bookmark.findall("row")))
					response+= foldername + " : " + str(count)+"\r\n"

	except:
		logging.info("barfed in XML api", sys.exc_info()[0])

	response +="```"
	return response
			
def getSRP():

	locale.setlocale(locale.LC_ALL, 'en_US.utf8')

	apikey = getKey("WALLET")	

	data = apikey.split()
	corpkey = data[0]
	corpvcode = data[1]

	url = "https://api.eveonline.com/corp/walletJournal.xml.aspx?keyid="+corpkey+"&vcode="+corpvcode+"&accountKey=1001"

	response = ''				
	starting_balance = 0.0
	start_date = ""
	donations = 0.0
	payouts = 0.0
	end_balance = 0.0
	
	try:
		root = ET.fromstring(requests.get(url).content)

		journal = sorted(list(root.iter('row')), key=lambda k: k.get('date'))

		for journal_entry in journal:

			balance = float(journal_entry.get('balance'))
			amount = float(journal_entry.get('amount'))
	
			if(starting_balance == 0):
				starting_balance = balance - amount
				start_date = journal_entry.get('date')
			
			if(amount > 0):
				donations = donations + amount
			else:
				payouts = payouts + amount
			
			end_balance = balance

	except:
		logging.info("barfed in XML api", sys.exc_info()[0])

	response += "SRP stats from " + start_date + " (last 30 days):\r\n"
	#response += "--------------------------------------------------\r\n"
	response += "```Starting balance: " + locale.format("%0.2f", starting_balance/1000000000, grouping=True) + "bn/isk\r\n"
	response += "Donations: " + locale.format("%0.2f", donations/1000000000, grouping=True) + "bn/isk\r\n"
	response += "Payouts: " + locale.format("%0.2f", payouts/1000000000, grouping=True) + "bn/isk\r\n"
	response += "Current balance: " + locale.format("%0.2f", end_balance/1000000000, grouping=True) + "bn/isk```"

	return response
