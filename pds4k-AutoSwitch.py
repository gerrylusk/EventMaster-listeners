#! /usr/bin/python

import time
import socket
import urllib.request # to get json
import json           

debug = 0

EMhost = '192.168.0.195'	# the address of the EM processor
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

def sendEMallTrans():
  #response = EMrpc(EMhost, 'allTrans', '{"transTime":' + str(time) + '}')
  response = EMrpc(EMhost, 'allTrans', '{}')
  return()

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

def getPDSpreviewLayer(dest):
  response = EMrpc(EMhost, 'listContent', '{"id":' + str(dest) + '}')
  items = response['Layers']
  if debug: print("Getting ", len(items), " layers from PDS.")
  for layer in range(len(items)):
    if debug: print(layer, items[layer]['id'], items[layer]['PvwMode'], items[layer]['LastSrcIdx'])
    if items[layer]['PvwMode'] == 1:
      previewLayer = items[layer]['id']
  return(previewLayer)

def switchPDSlayer(dest, layer, src):
  response = EMrpc(EMhost, 'changeContent', '{"id":' + str(dest) + ', "Layers":[ {"id":' + str(layer) + ', "LastSrcIdx":' + str(src) + '} ] }')
  if debug: print("switching: ", dest, layer, src, response)
  return()


def geEMactiveSources():
  response = EMrpc(EMhost, 'listSources', '{}')
  activeSources=[]
  if debug: print("Getting ", len(response), " sources from EM.")
  for item in range(len(response)):
    if 'InputCfgVideoStatus' in response[item]:
      if debug: print(item, response[item]['id'], response[item]['Name'], response[item]['InputCfgVideoStatus'])
      if response[item]['InputCfgVideoStatus']==1:
        activeSources.append(response[item]['id'])
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
	switchTo=''
	switchToOld = ''
	try:
		while True:	
			activeSources = geEMactiveSources()
			if activeSources != []: switchTo = activeSources[0]
			if debug: print(switchTo, "\n")
			
			# switch to the first active source
			previewLayer = getPDSpreviewLayer(0)
			if switchTo != switchToOld and switchTo != '':
				print("switch to", switchTo)
				switchPDSlayer(0, previewLayer, switchTo)
				sendEMallTrans()

			switchToOld = switchTo
				
			time.sleep(2)
	except KeyboardInterrupt :
		## tidy up
		print("\nDone.\n")
## end

	

