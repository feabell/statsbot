#eve api calls

import requests
import json
import xml.etree.ElementTree as ET
import time
import sys


def getSystem(systemID):
	url = "https://public-crest.eveonline.com/solarsystems/"+systemID+"/"
	
	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['name']
	except:
		print "couldn't connect to crest"

	return name

def getShip(shipID):
	url = "https://public-crest.eveonline.com/types/"+shipID+"/"

	name = ''
	try:
		blob = json.loads(requests.get(url).text)
		name = blob['name']
	except:
		print "couldn't connect to crest"

	return name

def getEvents():
	url = "https://api.eveonline.com/char/UpcomingCalendarEvents.xml.aspx?keyID=4718636&vCode=9sYvXlgR3hoUI5vdcFbSeYQEXbq7H9NK7mpYCf4GVQHKe7MAmQvAGc5OltUgw399"


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
	
	print response
	return response
			
				
