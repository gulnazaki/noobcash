from datetime import datetime
from time import time
from json import dumps
from hashlib import sha256
from collections import OrderedDict

class Block:

	def __init__(self, idx, transactions, previous_hash, nonce=None, hash_=None, timestamp=str(datetime.now()), start_time=time(), block_time=None):
		self.idx = idx
		self.transactions = transactions
		self.previous_hash = previous_hash
		self.nonce = nonce
		self.hash = hash_
		self.timestamp = timestamp
		self.start_time = start_time
		self.to_be_hashed = self.timestamp + self.previous_hash + ''.join([dumps(tx) for tx in self.transactions])
		if block_time:
			self.block_time = block_time
		if self.previous_hash == '1':
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
		if hasattr(self,'block_time'):
			d['block_time'] = self.block_time
		return d

	def mined(self, correct_nonce, correct_hash):
		self.nonce = correct_nonce
		self.hash = correct_hash


class Blockchain:

	def __init__(self, block_list, update_time=True):
		self.block_list = []
		for block in block_list:
			if isinstance(block, dict):
				block = Block(block['idx'], block['transactions'], block['prev_hash'], block['nonce'], block['hash'], block['timestamp'], block['start_time'], block['block_time'])
			self.add_block(block, update_time)

	def validate(self, difficulty):
		for idx, block in enumerate(self.block_list):
			if block.previous_hash == '1':
				continue
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

	def all_transactions(self, idx=0):
		f = lambda tx : tx if isinstance(tx, dict) else tx.to_dict()
		if idx >= 0:
			return [f(tx) for block in self.block_list[idx:] for tx in block.transactions]
		else:
			return [f(tx) for block in self.block_list[:-idx] for tx in block.transactions]

	def next_index(self):
		return self.block_list[-1].idx + 1

	def length(self):
		return len(self.block_list)

	def add_block(self, block, update_time=True):
		if update_time:
			block.block_time = time() - block.start_time
		self.block_list.append(block)

	def block_time(self):
		blocks = [block for block in self.block_list if hasattr(block,'block_time')]
		total_time = sum([block.block_time for block in blocks])
		return total_time/len(blocks), len(blocks)

	def list_of_hashes(self):
		return [block.hash for block in self.block_list]

	def index_of_fork(self, other_hashchain):
		our_hashchain = self.list_of_hashes()
		for idx, hash_ in enumerate(our_hashchain):
			if hash_ != other_hashchain[idx]:
				return idx
		return self.length()
