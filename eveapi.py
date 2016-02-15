#eve api calls

import requests
import json
import xml.etree.ElementTree as ET
import time
import sys
import yaml
import os
import locale

def getKey(key):

    prev_dir = os.getcwd()
    os.chdir('plugins/stats')
    config = yaml.load(file('eveapi.conf', 'r'))
    
    try:
    	apikey = config[key]
    except:
	print "no key with name " +key

    os.chdir(prev_dir)

    return apikey

def getSystem(systemID):
	url = "https://public-crest.eveonline.com/solarsystems/"+systemID+"/"
	
	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['name']
	except:
		print "couldn't connect to crest (system)"

	return name

def getShip(shipID):
	url = "https://public-crest.eveonline.com/types/"+shipID+"/"

	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['name']
	except:
		print "couldn't connect to crest (ship)"

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
		print "barfed in XML api", sys.exc_info()[0]
	
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
				print start_date
			
			if(amount > 0):
				donations = donations + amount
			else:
				payouts = payouts + amount
			
			end_balance = balance

	except:
		print "barfed in XML api", sys.exc_info()[0]

	response += "SRP stats from " + start_date + " (last 30 days):\r\n"
	response += "--------------------------------------------------\r\n"
	response += "Starting balance: " + locale.format("%d", starting_balance/1000, grouping=True) + "mn/isk\r\n"
	response += "Donations: " + locale.format("%d", donations/1000, grouping=True) + "mn/isk\r\n"
	response += "Payouts: " + locale.format("%d", payouts/1000, grouping=True) + "mn/isk\r\n"
	response += "Current balance: " + locale.format("%d", end_balance/1000, grouping=True) + "mn/isk\r\n"

	print response
	return response
