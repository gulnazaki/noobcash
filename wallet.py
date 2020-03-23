from binascii import hexlify

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class Wallet:

	def __init__(self):
		##set

		#self.public_key
		#self.private_key
		#self_address
		#self.transactions
		key = RSA.generate(4096)
		self.private_key = key
		self.public_key = key.public_key()
		self.address = hexlify(self.public_key.exportKey(format='DER')).decode('ascii')
		self.utxos = dict()

	def balance(self):
		return sum([nbc for _, recipient, nbc in self.utxos.values() if recipient == self.address])
