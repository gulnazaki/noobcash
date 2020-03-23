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
        if self.sender_address == '0':
            self.inputs = []
            idx, output = self.output(self.receiver_address, self.amount)
            self.outputs = {idx: output}
            self.signature = "genesis"
            self.update_utxos(ring)
        else:
            if not utxos:
                raise ValueError("You have to provide a non-empty utxos dictionary")
            if not self.choose_utxos(utxos):
                raise ValueError("You don't have enough money, I am sorry")


    def choose_utxos(self, utxos):


    def update_utxos(self, ring):
        for output_id, output in self.outputs.items():
            for node in ring.values():
                if output['recipient'] == node['address']:
                    node['utxos'][output_id] = 

    def output(self, recipient, amount):
        data = self.transaction_id + recipient + amount
        idx = sha256(data.encode('ascii')).hexdigest()
        output = {'transaction_id': self.transaction_id, 'recipient': recipient, 'amount': amount}
        return idx, output    
    
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
       