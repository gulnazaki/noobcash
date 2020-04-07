import requests as r
from collections import OrderedDict
from multiprocessing.pool import ThreadPool as Pool
from threading import Thread, Lock
import json
from time import sleep, time
import os
from pathlib import Path
from copy import deepcopy

from wallet import Wallet
from block import Block, Blockchain
from transaction import Transaction
from mining import Mining


class Node:

	def __init__(self, ip, port, is_bootstrap, max_nodes, NBC, capacity, difficulty, bootstrap_ip, bootstrap_port):
		self.ip = ip
		self.port = port
		self.bootstrap = is_bootstrap
		self.max_nodes = max_nodes
		self.NBC = NBC
		self.capacity = capacity
		self.difficulty = difficulty
		self.bootstrap_ip = bootstrap_ip
		self.bootstrap_port = bootstrap_port

		self.ring = {}
		self.wallet = Wallet()
		self.tx_pool = []
		self.node_dict = {'ip': self.ip, 'port': self.port, 'address': self.wallet.address, 'ready': False}

		self.mining_thread = None
		self.utxo_lock = Lock()
		self.tx_pool_lock = Lock()
		self.chain_lock = Lock()
		self.resolve_lock = Lock()

		if self.bootstrap:
			self.i_am_bootstrap()
		else:
			t = Thread(target=self.inform_bootstrap)
			t.start()


	def i_am_bootstrap(self):
		self.id = 0
		self.node_dict['utxos'] = OrderedDict()
		self.ring = OrderedDict({self.id: self.node_dict})
		self.blockchain = Blockchain([self.genesis_block()])

	def genesis_block(self):
		amount = self.NBC * self.max_nodes
		transactions = [Transaction(sender_address='0', sender_private_key=None, receiver_address=self.wallet.address, amount=amount, ring=self.ring).to_dict()]

		return Block(idx=0, transactions=transactions, previous_hash='1', nonce='0')

	def inform_bootstrap(self):
		url = 'http://' + self.bootstrap_ip + ':' + self.bootstrap_port + '/hello_bootstrap'
		while True:
			try:
				response = r.post(url, data={'node': json.dumps(self.node_dict)})
				code = response.status_code
			except r.exceptions.RequestException as e:
				print(e)
				code = 404
			if code != 404: break
			else: sleep(3)
		if response.status_code != 200:
			print('Bootstrap says: "' + json.loads(response.json())['msg'] + '"')
			exit()
		else:
			response = json.loads(response.json())
			self.id = response['id']
			self.blockchain = Blockchain(response['blockchain']['block_list'])
			self.node_dict['utxos'] = OrderedDict(response['utxos'])
			print("I am in with id " + str(self.id))

			valid, msg = self.blockchain.validate(self.difficulty)
			if not valid:
				print(msg)
				exit()
			while True:
				try:
					response = r.get('http://' + self.bootstrap_ip + ':' + self.bootstrap_port + '/broadcast_ring', params={'idx': self.id})
					code = response.status_code
				except r.exceptions.RequestException as e:
					print(e)
					code = 401
				sleep(3)
				if code == 200: break
			self.start_transactions()

	def node_already_exists(self, new_node):
		msg = None
		for node in self.ring.values():
			if new_node['ip'] == node['ip'] and new_node['port'] == node['port']:
				msg = "You are already in with another wallet"
			if new_node['address'] == node['address']:
				msg = "I already have your wallet's address"
		return msg

	def register_node_to_ring(self, node_dict):
		if not self.bootstrap:
			return 400, "I am sorry, bootstrap is not here", None, None, None
		if self.max_nodes == len(self.ring):
			return 400, "Sorry we are full, " + str(self.max_nodes) + " nodes at a time", None, None, None
		msg = self.node_already_exists(node_dict)
		if msg:
			return 400, msg, None, None, None

		idx = len(self.ring)
		node_dict['utxos'] = OrderedDict()
		self.ring[idx] = node_dict
		success, error = self.create_transaction(node_dict['address'], self.NBC)
		if not success:
			return 400, error, None, None, None
		else:
			return 200, "OK", idx, self.blockchain.to_dict(), self.ring[idx]['utxos']

	def broadcast(self, data, endpoint):
		node_list = [node for node_id, node in self.ring.items() if node_id != self.id and node['ready']]
		num_of_nodes = len(node_list)
		if num_of_nodes == 0:
			return True, []
		url_list = ['http://' + node['ip'] + ':' + node['port'] + endpoint for node in node_list]
		data_list = [data] * num_of_nodes

		p = Pool(num_of_nodes)

		try:
			successes, msg_list = list(zip(*p.starmap(send_stuff, zip(url_list, data_list))))
			p.close()
			p.join()
		except r.exceptions.RequestException as e:
			print(e)
			p.close()
			p.join()
			exit()
		
		successful = sum(successes) == num_of_nodes
		return successful, list(msg_list)

	def broadcast_ring(self):
		while len([node for node in self.ring.values() if node['ready']]) != self.max_nodes-1:
			print("Waiting for all nodes to get in")
			sleep(3)
		ring = self.ring.copy()
		ring[0]['ready'] = True
		success, msg_list = self.broadcast(data={'ring': json.dumps(ring)}, endpoint='/broadcast_ring')
		if not success:
			print("Failed broadcasting ring")
			exit()
		else:
			print("All nodes are informed, let\'s start")
			t = Thread(target=self.start_transactions)
			t.start()
			self.ring[0]['ready'] = True

	def broadcast_transaction(self, tx_dict):
		success, msg_list = self.broadcast(data={'tx': json.dumps(tx_dict)}, endpoint='/validate_transaction')
		if success:
			msg = ("All nodes know about transaction now")
		else:
			msg = "Failed broadcasting transaction"
			for m in msg_list:
				print(m)

		return success, msg

	def broadcast_block(self, block_dict):
		success, msg_list = self.broadcast(data={'block': json.dumps(block_dict)}, endpoint='/validate_block')
		if success:
			msg = ("All nodes know about block " + str(block_dict['idx']) + " now")
		else:
			msg = "Failed broadcasting block"
			for m in msg_list:
				print(m)

		return success, msg

	def start_transactions(self):
		filename = os.path.join('transactions',str(self.max_nodes)+'nodes','transactions'+str(self.id)+'.txt')
		with open(filename,'r') as tx_file:
			txs = tx_file.readlines()
		start_time = time()
		successes = []
		for tx in txs:
			recipient = self.ring[int(tx.split()[0].strip('id'))]['address']
			amount = int(tx.split()[1])
			success, msg = self.create_transaction(recipient, amount)
			print(msg)
			successes.append(success)
		sful = sum(successes)
		end_time = time()
		dirname = os.path.join('results',str(self.max_nodes)+'nodes')
		Path(dirname).mkdir(parents=True, exist_ok=True)
		filename = os.path.join(dirname,'tx_'+str(self.id)+'_'+str(self.capacity)+'_'+str(self.difficulty)+'.txt')
		with open(filename,'w') as file:
			file.write(str(sful) + ' Transactions in ' + str(end_time-start_time) + ' seconds, ' + str(len(txs) - sful) + ' failed\n')

	def create_transaction(self, recipient, amount):
		try:
			self.utxo_lock.acquire()
			tx_dict = Transaction(sender_address=self.wallet.address, sender_private_key=self.wallet.private_key,
							 receiver_address=recipient, amount=amount, ring=self.ring).to_dict()
		except ValueError as e:
			self.utxo_lock.release()
			return False, str(e)

		self.utxo_lock.release()
		s, m = self.broadcast_transaction(tx_dict)
		self.add_transaction_to_pool(tx_dict)
		return s, m

	def add_transaction_to_pool(self, tx_dict):
		with self.tx_pool_lock:
			if tx_dict not in self.tx_pool+self.blockchain.all_transactions():
				self.tx_pool.append(tx_dict)	
			poolsize = len(self.tx_pool)
			transactions = self.tx_pool[:self.capacity]
		if poolsize >= self.capacity:
			if (not self.mining_thread or not self.mining_thread.is_alive()) and self.ring:
				self.create_new_block(transactions)

	def create_new_block(self,transactions):
		with self.chain_lock:
			next_index = self.blockchain.next_index()
			last_hash = self.blockchain.last_hash()
			if [tx for tx in transactions if tx in self.blockchain.all_transactions()]:
				return
			block = Block(idx=next_index, transactions=transactions, previous_hash=last_hash)
		self.mining_thread = Mining(node=self, block=block)
		self.mining_thread.start()
		return

	def validate_transaction(self, tx_dict):
		try:
			self.utxo_lock.acquire()
			tx = Transaction(sender_address=tx_dict['sender_address'], sender_private_key=None, receiver_address=tx_dict['receiver_address'],
								amount=tx_dict['amount'], ring=self.ring, signature=tx_dict['signature'], inputs=tx_dict['inputs'], outputs=tx_dict['outputs'])
		except ValueError as e:
			self.utxo_lock.release()
			return 400, str(e)

		self.utxo_lock.release()
		self.add_transaction_to_pool(tx_dict)
		return 200, "Transaction validated"

	def validate_block(self, block_dict):
		block = Block(idx=block_dict['idx'], transactions=block_dict['transactions'], previous_hash=block_dict['prev_hash'],
							nonce=block_dict['nonce'], hash_=block_dict['hash'], timestamp=block_dict['timestamp'], start_time=block_dict['start_time'])
		if not hasattr(self, 'blockchain'):
			return 200, "I just came here, what are you expecting me to say?"
		self.chain_lock.acquire()
		valid, msg = block.validate(self.difficulty, self.blockchain.last_hash())
		if valid:
			# if self.ring:
			# 	with self.utxo_lock:
			# 		with self.tx_pool_lock:
			# 			if not self.resolve_tx(new_txs=block.transactions)[0]:
			# 				self.chain_lock.release()
			# 				return 400, "Block contains invalid transactions"
			with self.tx_pool_lock:
				self.tx_pool = [tx for tx in self.tx_pool if not tx in block_dict['transactions']]
			if self.mining_thread and self.mining_thread.is_alive():
				self.mining_thread.hash_found.set()
			self.blockchain.add_block(block)
			self.chain_lock.release()
			return 200, msg
		elif "Previous hash does not match" in msg:
			if block in self.blockchain.block_list:
				self.chain_lock.release()
				return 200, msg + ", but I already have this block"
			code, resolve_msg = self.resolve_conflicts()
			self.chain_lock.release()
			return code, msg + resolve_msg 
		else:
			self.chain_lock.release()
			return 400, msg

	def resolve_conflicts(self):
		success, conflict_data = self.broadcast(data={}, endpoint='/resolve_conflict')
		if success:
			conflict_data.sort(key=lambda x: x[0], reverse=True)
			for length, hashchain, node_index in conflict_data:
				if length <= self.blockchain.length():
					break
				idx = self.blockchain.index_of_fork(hashchain)
				try:
					response = r.get('http://' + self.ring[node_index]['ip'] + ':' + self.ring[node_index]['port'] + '/resolve_conflict', params={'idx': idx})
				except r.exceptions.RequestException as e:
					continue
				rest_of_the_blockchain = json.loads(response.json())['blockchain']
				blockchain = Blockchain(self.blockchain.block_list[:idx] + rest_of_the_blockchain, update_time=False)
				if blockchain.validate(self.difficulty)[0]:
					if self.mining_thread and self.mining_thread.is_alive():
						self.mining_thread.hash_found.set()
					with self.resolve_lock:
						old_txs = self.blockchain.all_transactions(idx)
						new_txs = self.blockchain.all_transactions()
						self.blockchain = blockchain
						with self.utxo_lock:
							with self.tx_pool_lock:
								self.ring = self.resolve_tx(old_txs=old_txs, new_txs=new_txs, resolve=True)[1]
					return 200, ", node " + str(node_index) + " gave me the correct blockchain"
			return 200, ", but it was just a false alarm, I have the largest valid blockchain"
		else:
			return 400, ", I couldn't ask all nodes to resolve the conflict"

	def resolve_tx(self, old_txs=[], new_txs=[], resolve=False):
		self.tx_pool = [tx for tx in self.tx_pool if not tx in new_txs]
		old_txs = [tx for tx in old_txs if not tx in new_txs]
		# self.tx_pool = old_txs + self.tx_pool

		temp_ring = deepcopy(self.ring)
		for node_dict in temp_ring.values():
			node_dict['utxos'] = OrderedDict()
		
		f = lambda tx : tx if isinstance(tx, dict) else tx.to_dict()
		transactions = [f(tx) for block in self.blockchain.block_list for tx in block.transactions]

		address_dict = {v['address']: int(k) for k, v in self.ring.items()}

		if resolve:
			transactions = transactions + self.tx_pool
		for tx in transactions:
			inputs = tx['inputs']
			outputs = tx['outputs']

			for out_id, tx_out in outputs.items():
				receiver = temp_ring[address_dict[tx_out['recipient']]]
				receiver['utxos'][out_id] = tx_out

			if tx['signature'] == "genesis":
				continue

			sender = temp_ring[address_dict[tx['sender_address']]]			
			for tx_in in inputs:
				if tx_in in sender['utxos']:
					del sender['utxos'][tx_in]
				else:
					return False, self.ring
		return True, temp_ring

	def write_block_times(self):
		avg, blocks = self.blockchain.block_time()
		dirname = os.path.join('results',str(self.max_nodes)+'nodes')
		Path(dirname).mkdir(parents=True, exist_ok=True)
		filename = os.path.join(dirname,'block_'+str(self.id)+'_'+str(self.capacity)+'_'+str(self.difficulty)+'.txt')
		with open(filename,'w') as file:
			file.write('Average block time is  ' + str(avg) + ' seconds, for ' + str(blocks) + 'blocks\n')

	def wallet_balance(self):
		with self.utxo_lock:
			balance = sum(utxo['amount'] for utxo in self.ring[self.id]['utxos'].values())
		return balance

	def view_transactions(self):
		with self.chain_lock:
			last = self.blockchain.last_transactions()
		return last


def send_stuff(url, data):
	response = r.post(url, data=data)
	return (response.status_code == 200), (json.loads(response.json())['msg'])
