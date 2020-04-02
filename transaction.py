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
        if signature:
            self.inputs = inputs
            self.outputs = outputs
            self.verify_signature(signature)
            self.signature = signature
        else:
            self.inputs = []
            self.outputs = OrderedDict()
            if self.sender_address == '0':
                self.add_output(self.receiver_address, self.amount)
                self.signature = "genesis"
            else:
                self.choose_utxos(ring)
                self.sign_transaction(sender_private_key)

            self.update_ring_utxos(ring)

    def choose_utxos(self, ring):
        current_amount = 0
        if self.amount == 0: return
        for node in ring.values():
            if self.sender_address == node['address']:
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

                raise ValueError("You don't have enough NBCs for this transaction")

        raise ValueError("Sender doesn't exist in ring")

    def update_ring_utxos(self, ring):
        for output_id, output in self.outputs.items():
            for node in ring.values():
                if output['recipient'] == node['address']:
                    node['utxos'][output_id] = output
                    break

        for node in ring.values():
            if node['address'] == self.sender_address:
                for utxo in self.inputs:
                    node['utxos'].pop(utxo)
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
            raise ValueError("You are no who you appear to be mister")