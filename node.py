import requests as r
from collections import OrderedDict
from multiprocessing import Pool
from threading import Thread, Lock
import json
from time import sleep

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

		self.ring = None
		self.wallet = Wallet()
		self.tx_pool = []
		self.node_dict = {'ip': self.ip, 'port': self.port, 'address': self.wallet.address}

		self.mining_thread = None
		self.lock = Lock()

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
		try:
			response = r.post(url, data={'node': json.dumps(self.node_dict)})
		except r.exceptions.RequestException as e:
			print(e)
			exit()
		while response.status_code == 404:
			try:
				sleep(2)
				response = r.post(url, data={'node': json.dumps(self.node_dict)})
			except r.exceptions.RequestException as e:
				print(e)
				exit()
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
			return 400, "I am sorry, bootstrap is not here", None, None
		if self.max_nodes == len(self.ring):
			return 400, "Sorry we are full, " + str(self.max_nodes) + " nodes at a time", None, None
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
		node_list = [node for node_id, node in self.ring.items() if node_id != self.id]
		num_of_nodes = len(node_list)
		url_list = ['http://' + node['ip'] + ':' + node['port'] + endpoint for node in node_list]
		data_list = [data] * num_of_nodes

		p = Pool(num_of_nodes)

		try:
			successes, msg_list = list(zip(*p.starmap(send_stuff, zip(url_list, data_list))))
		except r.exceptions.RequestException as e:
			print(e)
			exit()
		
		successful = sum(successes) == num_of_nodes
		return successful, msg_list

	def broadcast_ring(self):
		success, msg_list = self.broadcast(data={'ring': json.dumps(self.ring)}, endpoint='/broadcast_ring')
		if not success:
			print("Failed broadcasting ring")
			exit()
		else:
			print("All nodes are informed, let\'s start")

	def create_transaction(self, recipient, amount):
		try:
			tx_dict = Transaction(sender_address=self.wallet.address, sender_private_key=self.wallet.private_key,
							 receiver_address=recipient, amount=amount, ring=self.ring).to_dict()
		except ValueError as e:
			return False, str(e)

		self.add_transaction_to_pool(tx_dict)
		return self.broadcast_transaction(tx_dict)

	def add_transaction_to_pool(self, tx_dict):
		self.tx_pool.append(tx_dict)

		if len(self.tx_pool) >= self.capacity:
			if not self.mining_thread or not self.mining_thread.is_alive():
				self.create_new_block()

	def broadcast_transaction(self, tx_dict):
		success, msg_list = self.broadcast(data={'tx': json.dumps(tx_dict)}, endpoint='/validate_transaction')
		if success:
			msg = ("All nodes know about transaction " + tx_dict['transaction_id'] + " now")
		else:
			msg = "Failed broadcasting transaction"
			for m in msg_list:
				print(m)

		return success, msg

	def validate_transaction(self, tx_dict):
		try:
			tx = Transaction(sender_address=tx_dict['sender_address'], sender_private_key=None, receiver_address=tx_dict['receiver_address'],
								amount=tx_dict['amount'], ring=None, signature=tx_dict['signature'], inputs=tx_dict['inputs'], outputs=tx_dict['outputs'])
		except ValueError as e:
			return 400, str(e)
		if hasattr(self, 'blockchain'):
			self.add_transaction_to_pool(tx_dict)
		return 200, "Transaction validated"

	def create_new_block(self):
		block = Block(idx=self.blockchain.next_index(), transactions=self.tx_pool[:self.capacity], previous_hash=self.blockchain.last_hash())
		self.mining_thread = Mining(node=self, block=block)
		self.mining_thread.start()
		return

	def broadcast_block(self, block_dict):
		success, msg_list = self.broadcast(data={'block': json.dumps(block_dict)}, endpoint='/validate_block')
		if success:
			msg = ("All nodes know about block " + str(block_dict['idx']) + " now")
		else:
			msg = "Failed broadcasting block"
			for m in msg_list:
				print(m)

		return success, msg

	def validate_block(self, block_dict):
		block = Block(idx=block_dict['idx'], transactions=block_dict['transactions'], previous_hash=block_dict['prev_hash'],
							nonce=block_dict['nonce'], hash_=block_dict['hash'], timestamp=block_dict['timestamp'], start_time=block_dict['start_time'])
		if not hasattr(self, 'blockchain'):
			return 200, "I just came here, what are you expecting me to say?"
		valid, msg = block.validate(self.difficulty, self.blockchain.last_hash())
		if valid:
			if self.mining_thread and self.mining_thread.is_alive():
				self.mining_thread.hash_found.set()
			self.blockchain.add_block(block)
			return 200, msg
		elif "Previous hash does not match" in msg:
			if block in self.blockchain.block_list:
				return 200, msg + ", but I already have this block"
			code, resolve_msg = self.resolve_conflicts(block_dict)
			return code, msg + resolve_msg 
		else:
			return 400, msg

	def wallet_balance(self):
		return sum(utxo['amount'] for utxo in self.node_dict['utxos'].values())

	def view_transactions(self):
		return self.blockchain.last_transactions()

	def resolve_conflicts(self, block_dict):
		success, conflict_data = self.broadcast(data={}, endpoint='/resolve_conflict')
		if success:
			conflict_data.sort(key=lambda x: x[0], reverse=True)
			for length, hashchain, block_index, node_index in conflict_data:
				if length <= self.blockchain.length():
					break
				idx = self.blockchain.index_of_fork(hashchain)
				try:
					response = r.get('http://' + self.ring[node_index]['ip'] + ':' + self.ring[node_index]['port'] + '/resolve_conflict', params={'idx': idx})
				except r.exceptions.RequestException as e:
					return 400, ", I couldn't ask all nodes to resolve the conflict"
				else:
					rest_of_the_blockchain = json.loads(response.json())['blockchain']
					blockchain = Blockchain(self.blockchain.block_dict[:idx] + rest_of_the_blockchain, update_time=False)
					if blockchain.validate()[0]:
						if self.mining_thread and self.mining_thread.is_alive():
							self.mining_thread.hash_found.set()
						self.blockchain = blockchain
						self.blockchain.update_utxos(ring)
						return 200, ", node " + node_index + " gave me the correct blockchain"
			return 200, ", but it was just a false alarm, I have the largest valid blockchain"
		else:
			return 400, ", I couldn't ask all nodes to resolve the conflict"


def send_stuff(url, data):
	response = r.post(url, data=data)
	return (response.status_code == 200), (json.loads(response.json())['msg'])
