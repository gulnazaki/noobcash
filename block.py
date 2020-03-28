from datetime import datetime
from json import dumps
from hashlib import sha256
from collections import OrderedDict

class Block:

	def __init__(self, idx, transactions, previous_hash, capacity, nonce=None, timestamp=str(datetime.now())):
		self.idx = idx
		self.transactions = transactions
		self.previous_hash = previous_hash
		self.capacity = capacity
		self.timestamp = timestamp
		self.to_be_hashed = self.previous_hash + ''.join([dumps(tx) for tx in self.transactions])
		if nonce: 
			self.nonce = nonce
			self.hash = self.my_hash(nonce)
	
	def my_hash(self, nonce):
		data = self.to_be_hashed + nonce
		return sha256(data.encode('ascii')).hexdigest()


	def add_transaction(transaction, blockchain ):
		#add a transaction to the block
		return

	def validate(self, difficulty, prev_hash):
		return self.hash.startswith('0'*difficulty) and prev_hash == self.previous_hash

	def to_dict(self):
		d = OrderedDict()
		d['idx'] = self.idx
		d['transactions'] = self.transactions
		d['prev_hash'] = self.previous_hash
		d['capacity'] = self.capacity
		d['timestamp'] = self.timestamp
		d['nonce'] = self.nonce
		d['hash'] = self.hash
		return d


class Blockchain:

	def __init__(self, block_list=[]):
		self.block_list = block_list
		for block in block_list:
			if isinstance(block, dict):
				block = Block(block['idx'], block['transactions'], block['prev_hash'], block['capacity'], block['nonce'], block['timestamp'])
		self.size = len(self.block_list)

	def validate(self, difficulty):
		valid = True
		for idx, block in enumerate(self.block_list[1:]):
			prev_hash = self.block_list[idx-1].hash
			valid = block.validate(difficulty, prev_hash)
		return valid

	def to_dict(self):
		d = OrderedDict()
		d['size'] = self.size
		d['block_list'] = [block.to_dict() for block in self.block_list]
		return d
