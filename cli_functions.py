import requests
import json, csv
import pandas as pd
from pandas import read_json
import ast

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

	code = request.status_code
	if code != 200:
		print( f'An Error Occured. Error Code {code}')
	else:
		data = request.json()
		if not isinstance(data, dict ):
			try:
				data = ast.literal_eval(data)
			except:
				pass

		keys = list( data.keys() )
		if 'tx_list' in keys:
			showlist = ['sender_address', 'receiver_address', 'amount', 'transaction_id' ]
			df = pd.DataFrame(data['tx_list'])
			f = lambda x : x[-12:]
			for elem in showlist:
				if elem != 'amount':
					df[elem] = df[elem].apply(f)
			with pd.option_context('display.max_rows',None, 'display.max_columns', None):
				print(df [ showlist ] )
		elif 'balance' in keys:
			key = 'balance'
			print(f'My balance is: {data[key]}')
		else:
			print(data)
	return

def transaction(args):
	recip_addr = args.recip_addr
	sender_addr = args.sender_addr
	amount = args.amount
	url = f'{BASE}/create_transaction'
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
	url = f'{BASE}/balance'
	r = requests.get(url)
	HandleRequest(r)
	return 0
