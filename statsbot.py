import os, threading, sys

import eveapi
import zkbapi
#import slackapi

outputs = []

def process_message(data):
	#stop the bot from barfing out for events without a text chunk (event_ts chunks happen with unfurled links)
	if not 'text' in data:
		return

	channel = data["channel"]
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
		elif command.startswith("xxxxaaaa"):
			outputs.append([channel, zkbapi.getLastKill()])	
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
		


