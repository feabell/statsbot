#calls out to the skynet fleet api

import requests
import json
import sys

def newFleet(fcname, description):
	
	payload = {'key': 'test', 'fcname': fcname, 'description': description}
	url = "http://feabell.com:5000/new/"
	r = ''

	try:	
		jsondata = json.loads(requests.post(url, data=json.dumps(payload)).text)
		r = "Fleet created! Participation URL: "+ jsondata['url']
	except:
		print "could not connect to skynet", sys.exc_info()[0]

	return r



