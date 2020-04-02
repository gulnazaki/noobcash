from binascii import hexlify
from Cryptodome.PublicKey import RSA


class Wallet:

	def __init__(self):

		key = RSA.generate(4096)
		self.private_key = hexlify(key.exportKey(format='DER')).decode('ascii')
		public_key = key.publickey()
		self.address = hexlify(public_key.exportKey(format='DER')).decode('ascii')
