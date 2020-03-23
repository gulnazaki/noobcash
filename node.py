from flask import jsonify, request
from os.path import exists
import requests as r
from collections import OrderedDict

from wallet import Wallet
from block import Block, Blockchain
from transaction import Transaction


class NewNode(Resource):

	def post(self):
        isbootstrap = request.form['is_bootstrap']
        if isbootstrap:
        	if not exists('bootstrapconfig.txt'):
        		response = {'msg': 'bootstrapconfig.txt not available'}
        		return jsonify(response), 400
        	with open('bootstrapconfig.txt','r') as b:
        		ip = b.readline().strip()
        		port = b.readline().strip()
        else:
        	ip = request.form['ip']
        	port = request.form['port']
        max_nodes = request.form['max_nodes']
        NBC = request.form['NBC']
        capacity = request.form['capacity']
        difficulty = request.form['difficulty']

        running = Node(ip, port, is_bootstrap, max_nodes, NBC, capacity, difficulty)

        response = {'msg': 'OK'}
        return jsonify(response), 200


class InformBootstrap(Resource):

	def post(self):
		node_dict = request.form

		code, msg, idx, blockchain = running.register_node_to_ring(node_dict)
		if code != 200:
			response = {'msg': msg}
		else:
			response = {'msg': msg, 'id': idx, 'blockchain': blockchain}
			if idx == running.max_nodes - 1:
				running.broadcast_ring()
		return jsonify(response), code


class BroadcastRing(Resource):

	def post(self):
		for idx, node in request.form.items():
			if idx in running.ring:
				msg = "I know about node " + str(idx) + " already"
				return jsonify({'msg': msg}), 400
			else:
				running.ring[idx] = node
		msg = "OK"
		return jsonify({'msg': msg}), 200

class Balance(Resource):

	def get(self):
		try:
			balance = running.wallet_balance()
		except:
			return jsonify({'msg': "Error"}), 400
		
		return jsonify({'msg': balance}), 200


class Node:

	def __init__(self, ip, port, is_bootstrap=False, max_nodes=5, NBC=100, capacity=1, difficulty=4):
		self.ip = ip
		self.port = port
		self.bootstrap = is_bootstrap
		self.max_nodes = max_nodes
		self.NBC = NBC
		self.capacity = capacity
		self.difficulty = difficulty
		self.wallet = Wallet()
		self.ring = OrderedDict()
		node_dict = {'ip': self.ip, 'port': self.port, 'address': self.wallet.address, 'utxos': OrderedDict()}

		if self.bootstrap:
			self.i_am_bootstrap()
		else:
			self.inform_bootstrap()
			self.blockchain.validate(self.difficulty)


	def i_am_bootstrap(self):
		self.id = 0
		self.current_nodes = 1
		self.blockchain = Blockchain([self.genesis_block()])
		self.ring[self.id] = node_dict

	def genesis_block(self):
		amount = self.NBC * self.max_nodes
		previous_hash = '1'
		nonce = '0'
		idx = 0
		timestamp = str(datetime.now())
		transactions = [Transaction(sender_address='0', sender_private_key=None, receiver_address=self.wallet.address, amount=amount, self.ring).to_dict()]
		return Block(idx, transactions, nonce, previous_hash, self.capacity)

	def inform_bootstrap(self):
		with open('bootstrapconfig.txt','r') as b:
        	ip = b.readline().strip()
        	port = b.readline().strip()
        url = 'http://' + ip + ':' + port + '/node/hello_bootstrap'
        response = r.post(url, data=node_dict)
        if response.status_code != 200:
        	print("Bootstrap says:\n" + response.json()['msg'])
        	exit()
        else:
        	self.id = response.json()['id']
        	self.blockchain = response.json()['blockchain']
        	print("I am in with id " + self.id)

	def node_already_exists(self, node_dict):
		msg = None
		for node in self.ring.values():
			if node_dict['ip'] == node.ip and node_dict['port'] == node.port:
				msg = "You are already in with another wallet"
			if node_dict['address'] == node.wallet.address:
				msg = "I already have your wallet's address"
		return msg

	def register_node_to_ring(self, node_dict):
		if not self.bootstrap:
			return 400, "I am sorry, bootstrap is not here", None, None
		if self.max_nodes == len(self.ring):
			return 400, "Sorry we are full, " + str(self.max_nodes) + " nodes at a time", None, None
		msg = self.node_already_exists(node_dict)
		if msg: return 400, msg, None, None

		idx = len(self.ring)
		self.ring[idx] = node_dict
		return 200, "OK", idx, self.blockchain

	def broadcast_ring(self):
		for node in self.ring.values()[1:]:
            url = 'http://' + node['ip'] + ':' + node['port'] + '/node/all_in'
            response = r.post(url, data=self.ring)
            if response.status_code != 200:
                print("Failed broadcasting ring, problem with " + node['ip'] + ":" + node['port'])
                print("Node says:\n" + response.json()['msg'])
                exit()
            else:
            	print("All nodes are informed, let\'s start")

	def create_transaction(self, recipient, amount):
        try:
            tx = Transaction(sender_address=self.wallet.address, sender_private_key=self.wallet.private_key, 
            				 receiver_address=recipient, amount=amount, ring=self.ring)
        except ValueError as e:
            return False, e
        
        self.add_transaction_to_pool(tx.to_dict())
        self.broadcast_transaction(tx.to_dict())
        return True, None

	def broadcast_transaction(self):
		data = {'tx_dict': json.dumps(tx_dict)}
        thread_list = []
        for i in range(0, len(self.ring)):
            if self.id != i:
                node = self.ring[i]
                url = 'http://'+node['ip']+':'+str(node['port'])+'/new_transaction'
                t = threading.Thread(target=self.thr_send_data, args=(url, data))
                t.start()
                thread_list.append(t)
        return



	def validate_transaction():
		#use of signature and NBCs balance


	def add_transaction_to_block():
		#if enough transactions  mine

	def wallet_balance(self):
		return sum(utxo['amount'] for utxo in self.ring[self.id]['utxos'].values())
	
	def create_new_block():


	def mine_block():



	def broadcast_block():


		

	def valid_proof(.., difficulty=MINING_DIFFICULTY):




	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		#resolve correct chain



