from datetime import datetime
from time import time
from json import dumps
from hashlib import sha256
from collections import OrderedDict

class Block:

	def __init__(self, idx, transactions, previous_hash, nonce=None, hash_=None, timestamp=str(datetime.now()), start_time=time()):
		self.idx = idx
		self.transactions = transactions
		self.previous_hash = previous_hash
		self.nonce = nonce
		self.hash = hash_
		self.timestamp = timestamp
		self.start_time = start_time
		self.to_be_hashed = self.timestamp + self.previous_hash + ''.join([dumps(tx) for tx in self.transactions])
		if self.idx == 0:
			self.mined(nonce, self.my_hash(nonce))

	def my_hash(self, nonce):
		data = self.to_be_hashed + str(nonce)
		return sha256(data.encode('ascii')).hexdigest()

	def validate(self, difficulty, prev_hash):
		msg = "Block " + str(self.idx) + ": "
		if self.hash != self.my_hash(self.nonce):
			return False, msg + "False hash"
		if not self.hash.startswith('0'*difficulty):
			return False, msg + "Hash not solved"
		if prev_hash != self.previous_hash:
			return False, msg + "Previous hash does not match"
		return True, msg + "Validated"

	def to_dict(self):
		d = OrderedDict()
		d['idx'] = self.idx
		d['transactions'] = self.transactions
		d['prev_hash'] = self.previous_hash
		d['nonce'] = self.nonce
		d['hash'] = self.hash
		d['timestamp'] = self.timestamp
		d['start_time'] = self.start_time
		return d

	def mined(self, correct_nonce, correct_hash):
		self.nonce = correct_nonce
		self.hash = correct_hash


class Blockchain:

	def __init__(self, block_list, update_time=True):
		self.block_list = []
		for block in block_list:
			if isinstance(block, dict):
				block = Block(block['idx'], block['transactions'], block['prev_hash'], block['nonce'], block['hash'], block['timestamp'], block['start_time'])
			self.add_block(block, update_time)

	def validate(self, difficulty):
		for idx, block in enumerate(self.block_list[1:]):
			prev_hash = self.block_list[idx-1].hash
			valid, msg = block.validate(difficulty, prev_hash)
			if not valid:
				return False, msg
		return True, None

	def to_dict(self):
		d = OrderedDict()
		d['length'] = self.length()
		d['block_list'] = [block.to_dict() for block in self.block_list]
		return d

	def last_hash(self):
		return self.block_list[-1].hash

	def last_transactions(self):
		return self.block_list[-1].transactions

	def next_index(self):
		return self.block_list[-1].idx + 1

	def length(self):
		return len(self.block_list)

	def add_block(self, block, update_time=True):
		if update_time:
			block.block_time = time() - block.start_time
		self.block_list.append(block)

	def list_of_hashes(self):
		return [block.hash for block in self.block_list]

	def index_of_fork(self, other_hashchain):
		our_hashchain = self.list_of_hashes()
		for idx, hash_ in enumerate(our_hashchain):
			if hash_ != other_hashchain[idx]:
				return idx
		return self.length()

	def update_utxos(self, ring):
		for node_dict in ring:
			node_dict['utxos'] = OrderedDict()

		transactions = [[[transaction if isinstance(transaction, dict) else transaction.to_dict() for transaction in transactions]\
		 				for transactions in block] for block in self.block_list]
		address_dict = {v['address']: k for k, v in self.ring.items()}

		for tx in transactions:
			sender = ring[address_dict[tx['sender_address']]]
			receiver = ring[address_dict[tx['receiver_address']]]
			inputs = tx['inputs']
			outputs = tx['outputs']
			node = ring[self.address_dict[self.sender_address]]
			
			for tx_in in inputs:
				del node['utxos'][tx_input]
			for out_id, tx_out in outputs.items():
				node['utxos'][out_id] = tx_out
