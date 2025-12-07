#! /usr/bin/python

import time
import socket
import urllib.request # to get json
import json           

debug = 0

EMhost = '192.168.11.190'	# the address of the EM processor
myHost = '0.0.0.0'			# my own address to use for EM subscribe notifications

def EMrpc(host, method, params):
  EMurl = "http://" + host + ":9999"
  EMdata = '{"params":' + params + ', "method":"' + method + '", "id":"1234", "jsonrpc":"2.0"}'
  EMrequest = urllib.request.Request(EMurl, EMdata.encode(), {'Content-Type': 'application/json'})
  EMresponse = urllib.request.urlopen(EMrequest).read()
  try:
    return(json.loads(EMresponse)['result']['response'])
  except:
    return(json.loads(EMresponse))

def getEMauxes(): # Populate the routing table with the auxes found in EM
  response = EMrpc(EMhost, 'listDestinations', '{"type":2}')
  EMdests = response['AuxDestination']
  if debug: print("Getting ", len(EMdests), " auxes from EM.")
  for aux in range(len(EMdests)):
    response = EMrpc(EMhost, 'listAuxContent', '{"id":' + str(aux) + '}')
    EMauxName = response['Name']
    EMauxPGM  = response['PgmLastSrcIndex']
    if debug: print(aux, EMauxName, EMauxPGM)
    #if EMauxPGM != -1: vRouting[aux] = int(EMauxPGM)
  return()

def geEMactiveSources():
  response = EMrpc(EMhost, 'listSources', '{}')
  activeSources=[]
  if debug: print("Getting ", len(response), " sources from EM.")
  for item in range(len(response)):
    if 'InputCfgVideoStatus' in response[item] and response[item]['InputCfgVideoStatus']==1:
        activeSources.append(response[item]['id'])
        if debug: print(item, response[item]['Name'], response[item]['InputCfgVideoStatus'])
  return(activeSources)
  
def sendEMaux(auxID, source): # send the route change to the EM aux
  print("Changing AUX ", auxID, "to ", source)
  response = EMrpc(EMhost, 'changeAuxContent', '{"id":' + str(auxID) + ', "PgmLastSrcIndex":' + str(source) + '}')
  print(response)
  return()

def EMsubscribe(): # subscribe to changes so we know when something else changes an aux
  if myHost != "0.0.0.0":
    print("Subscribing to aux change notices.\n")
    response = EMrpc(EMhost, 'subscribe', '{"hostname":"' + myHost + '", "port":"9990", "notification":["AUXDestChanged"]}')
    print(response)
  else:
    print("Can't subscribe to EM changes if my address is ", myHost)
  return()

def EMunsubscribe(): # unsubscribe from the EM notice
  if myHost != "0.0.0.0":
    print("Unubscribing to aux change notices.\n")
    response = EMrpc(EMhost, 'unsubscribe', '{"hostname":"' + myHost + '", "port":"9990", "notification":["AUXDestChanged"]}')
    print(response)
  else:
    print("Can't unsubscribe to EM changes if my address is ", myHost)
  return()

if __name__ == "__main__":
	switchToOld = []
	try:
		while True:
	
			getEMauxes()
			switchTo = geEMactiveSources()
			if debug: print(switchTo, "\n\n\n")
			
			# switch to the first active source or 7 if none
			## note that this needs to change to EMScreen or something for PDS
			if switchTo != switchToOld and switchTo != []:
				sendEMaux(0, switchTo[0])
			elif switchTo != switchToOld:
				sendEMaux(0, 7)
			switchToOld = switchTo
				
			time.sleep(2)
	except KeyboardInterrupt :
		## tidy up
		print("\nDone.\n")
## end

	

