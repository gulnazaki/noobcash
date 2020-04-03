import requests
import json, csv
import pandas as pd
from pandas import read_json

PORT = 5000
BASE = f'http://localhost:{PORT}'

def getPort():
	global PORT
	global BASE
	try:
		keys = []
		vals = []
		with open('./bootstrapconfig.txt', 'r') as f:
			config_txt = f.read()
			for line in config_txt.splitlines():
				words = line.split()
				k, v = words[0], words[1]
				keys.append(k)
				vals.append(v)
				if k.lower() == 'PORT'.lower():
					PORT = v
					BASE = f'http://localhost:{PORT}'
					break
			# config_dict = dict( zip(keys, vals ))
	except:
		pass

getPort()

def HandleRequest(request):
	# data = json.loads(request.json() )
	# print( request.status_code )
	# print( request.json().keys() )
	code = request.status_code
	if code != 200:
		print( f'An Error Occured. Error Code {code}')
	else:
		data = request.json()
		keys = list( data.keys() )
		for key in keys:
			if key == 'msg':
				msg = data[key]
				print(msg)
			elif key == 'tx_list':
				print( pd.DataFrame(data[key]))
	# print( read_json(data[key]) )
	# print( json.loads(request.text) )

	# msg = request.msg
	# code = request.status_code
	# if code != 200:
	# 	print('ERROR! Try again later')
	# else:
	# 	response = request.json()
	# 	for key in response.keys():
	# 		val = response[keys]
	# 		if val is not None:
	# 			print(pd.read_json(val))
	return

def transaction(args):
	recip_addr = args.recip_addr
	sender_addr = args.sender_addr
	amount = args.amount
	url = f'{BASE}/transaction/create'
	data = { 'recipient':recip_addr, 'amount':amount}
	r = requests.post(url, data = data)
	HandleRequest(r)
	return 0

def view(args):
	url = f'{BASE}/view_transactions'
	r = requests.get(url)
	HandleRequest(r)
	return 0

def balance(args):
	url = f'{BASE}/wallet/balance'
	r = requests.get(url)
	HandleRequest(r)
	return 0
