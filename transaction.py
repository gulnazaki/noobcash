from collections import OrderedDict
from binascii import hexlify, unhexlify
from hashlib import sha256
from Cryptodome.Hash import SHA
from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.PublicKey import RSA
import json


class Transaction:

	def __init__(self, sender_address, sender_private_key, receiver_address, amount, ring, signature=None, inputs=None, outputs=None):
		self.sender_address = sender_address
		self.receiver_address = receiver_address
		self.amount = amount
		self.transaction_id = self.my_hash()
		self.address_dict = {v['address']: k for k, v in ring.items()}
		# creating a completely new transaction
		if not signature:
			self.inputs = []
			self.outputs = OrderedDict()
			# genesis block
			if self.sender_address == '0':
				self.add_output(self.receiver_address, self.amount)
				self.signature = "genesis"
				self.add_new_utxos(ring)
			else:
				self.choose_utxos(ring)
				self.sign_transaction(sender_private_key)
				self.remove_used_utxos(ring)
				self.add_new_utxos(ring)
		# creating one just to validate
		else:
			self.inputs = inputs
			self.outputs = outputs
			self.verify_signature(signature)
			# only transactions validated after full node participation have to check and update ring utxos
			if ring:
				self.remove_used_utxos(ring)
				self.add_new_utxos(ring)

	def choose_utxos(self, ring):
		current_amount = 0
		if self.amount == 0: return
		if self.sender_address not in self.address_dict:
			raise ValueError("Sender doesn't exist in ring")
		
		node = ring[self.address_dict[self.sender_address]]
		if not node['utxos']:
			raise ValueError("You have no UTXOs")

		for utxo_id, utxo in node['utxos'].items():
			self.inputs.append(utxo_id)
			change = current_amount + int(utxo['amount']) - int(self.amount)
			
			if change == 0:
				self.add_output(self.receiver_address, self.amount)
				return
			elif change > 0:
				self.add_output(self.receiver_address, self.amount)
				self.add_output(self.sender_address, change)
				return
			else:
				current_amount +=int(utxo['amount'])

		raise ValueError("You don't have enough NBCs for this transaction")

	def remove_used_utxos(self, ring):
		if not self.inputs:
			raise ValueError("Transactions require inputs")	
		if self.sender_address not in self.address_dict:
			raise ValueError("Sender doesn't exist in ring")

		node = ring[self.address_dict[self.sender_address]]
		for tx_input in self.inputs:
			if not tx_input in node['utxos']:
				raise ValueError("Transaction input with id " + tx_input + " is not an unspent transaction for " + str(self.transaction_id))
			else:
				del node['utxos'][tx_input]
		return

	def add_new_utxos(self, ring):	
		if not self.outputs:
			raise ValueError("Transactions require outputs")	
		for output_id, output in self.outputs.items():
			node = ring[self.address_dict[output['recipient']]]
			node['utxos'][output_id] = output
		return

	def add_output(self, recipient, amount):
		data = self.transaction_id + recipient + str(amount)
		idx = sha256(data.encode('ascii')).hexdigest()
		output = {'transaction_id': self.transaction_id, 'recipient': recipient, 'amount': amount}
		self.outputs[idx] = output
	
	def to_dict(self, to_be_hashed=False):
		d = OrderedDict()
		d['sender_address'] = self.sender_address
		d['receiver_address'] = self.receiver_address
		d['amount'] = self.amount
		if not to_be_hashed:
			d['transaction_id'] = self.transaction_id
			d['inputs'] = self.inputs
			d['outputs'] = self.outputs
			d['signature'] = self.signature
		return d

	def my_hash(self):
		data = self.sender_address + self.receiver_address + str(self.amount)
		return sha256(data.encode('ascii')).hexdigest()        

	def sign_transaction(self, sender_private_key):
		signer = PKCS1_v1_5.new(RSA.importKey(unhexlify(sender_private_key)))
		h = SHA.new(json.dumps(self.to_dict(to_be_hashed=True)).encode('utf8'))
		self.signature = hexlify(signer.sign(h)).decode('ascii')

	def verify_signature(self, signature):
		public_key = RSA.importKey(unhexlify(self.sender_address))
		verifier = PKCS1_v1_5.new(public_key)
		h = SHA.new(json.dumps(self.to_dict(to_be_hashed=True)).encode('utf8'))
		if not verifier.verify(h, unhexlify(signature)):
			raise ValueError("You are not who you appear to be, mister")