import requests
import json, csv
import pandas as pd
from pandas import read_json
import ast

PORT = 5000
BASE_IP = f'http://localhost'
BASE = f'{BASE_IP}:{PORT}'

def getPort():
	global PORT
	global BASE_IP
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
					BASE = f'{BASE_IP}:{PORT}'
					break
			# config_dict = dict( zip(keys, vals ))
	except:
		pass

# getPort()

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
			for key in data.keys():
				print(data[key])
	#handle wrong transaction address
	if code == 404:
		data = request.json()
		if not isinstance(data, dict ):
			try:
				data = ast.literal_eval(data)
			except:
				pass
		print(data['msg'])
		print('Try locating your receiver through the following info in the ring :)\n(You can also locate the following table in the file "my_adressbook.csv")')
		ring = data['ring']
		if not isinstance(ring, dict ):
			try:
				ring =json.loads(ring)
				df = pd.DataFrame(ring).transpose()
				print(df)
				df.to_csv('my_adressbook.csv')
			except:
				ring = ast.literal_eval(ring)
				print(ring)
		# print(pd.DataFrame(data['ring']))
		# if 'ring' in keys:
			# print(data['ring'])
	return

def transaction(args):
	global PORT
	global BASE
	PORT = args.sender_port
	BASE_IP = args.sender_ip
	BASE = f'{BASE_IP}:{PORT}'
	url = f'http://{BASE}/create_transaction'
	recip_addr = args.recip_addr
	recip_id = args.recip_id[0]
	amount = args.amount[0]
	keys = ['recipient', 'id', 'amount']
	vals = [recip_addr, recip_id, amount]
	keys = [ k for k,v in zip(keys, vals) if not v is None ]
	vals = [ v for v in vals if not v is None ]
	data = dict( zip(keys, vals) )
	r = requests.post(url, data = data)
	HandleRequest(r)
	return 0

def view(args):
	global PORT
	global BASE
	getPort()
	url = f'{BASE}/view_transactions'
	r = requests.get(url)
	HandleRequest(r)
	return 0

def balance(args):
	global PORT
	global BASE
	global BASE_IP
	try:
		BASE_IP = args.my_addr
		PORT = args.my_port
		BASE = f'{BASE_IP}:{PORT}'
	except:
		getPort()
	url = f'http://{BASE}/balance'
	print(url)
	r = requests.get(url)
	HandleRequest(r)
	return 0
