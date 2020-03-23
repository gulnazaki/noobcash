from collections import OrderedDict
from hashlib import sha256

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, receiver_address, amount, ring):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_id = self.my_hash()
        self.inputs = []
        self.outputs = OrderedDict()
        if self.sender_address == '0':
            self.add_output(self.receiver_address, self.amount)
            self.signature = "genesis"
        else:
            self.choose_utxos(ring)
            self.sign_transaction()

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
                    change = current_amount + utxo['amount'] - self.amount
                    
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
        data = self.transaction_id + recipient + amount
        idx = sha256(data.encode('ascii')).hexdigest()
        output = {'transaction_id': self.transaction_id, 'recipient': recipient, 'amount': amount}
        self.outputs[idx] = output
    
    def to_dict(self):
        d = OrderedDict()
        d['sender_address'] = self.sender_address
        d['receiver_address'] = self.receiver_address
        d['amount'] = self.amount
        return d

    def my_hash(self):
        data = self.self.sender_address + self.recipient_address + str(self.amount)
        return sha256(data.encode('ascii')).hexdigest()        

    def sign_transaction(self):
        signer = PKCS1_v1_5.new(self.sender_private_key)
        h = SHA.new(json.dumps(self.to_dict()).encode('utf8'))
        self.signature = hexlify(signer.sign(h)).decode('ascii')
       