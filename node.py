from flask import jsonify, request
from os.path import exists

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
		args = self.parser.parse_args()
		node_dict = request.form['node_dict']

		code, msg, idx, blockchain = running.register_node_to_ring(node_dict)
		if code == 200:
			response = {'msg': msg, 'id': idx, 'blockchain': blockchain}
		else:
			response = {'msg': msg}
		return jsonify(response), 200



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
		self.ring = []

		if self.bootstrap:
			i_am_bootstrap()
		else:



		##set

		#self.chain
		#self.current_id_count
		#self.NBCs
		#self.wallet

		#slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 

	def i_am_bootstrap(self):
		self.id = 0
		self.current_nodes = 1
		node_dict = {'id': self.id, 'ip': self.ip, 'port': self.port, 'address': self.wallet.address, 'utxos': ?}
		self.ring.append(node_dict)
		self.blockchain = Blockchain([self.genesis_block()])

	def genesis_block(self):
		amount = self.NBC * self.max_nodes
		previous_hash = '1'
		nonce = '0'
		idx = 0
		timestamp = str(datetime.now())
		transactions = [Transaction()]
		return Block(idx, transactions, nonce, previous_hash, self.capacity)

	def node_already_exists(self, node_dict):
		msg = None
		for node in self.ring:
			if node_dict['ip'] == node.ip and node_dict['port'] == node.port:
				msg = "You are already in with another wallet"
			if node_dict['address'] == node.wallet.address:
				msg = "I already have your wallet's address"
		return msg

	def create_new_block():

	def create_wallet():
		#create a wallet for this node, with a public key and a private key

	def register_node_to_ring(self, node_dict):
		if not self.bootstrap:
			return 400, "I am sorry, bootstrap is not here", None, None
		if self.max_nodes == len(self.ring):
			return 400, "Sorry we are full, " + str(self.max_nodes) + " nodes at a time", None, None
		msg = self.node_already_exists(node_dict)
		if msg: return 400, msg, None, None

		idx = len(self.ring)
		node_dict['id': idx]
		self.ring.append(node_dict)
		return 200, "OK", idx self.blockchain


	def create_transaction(sender, receiver, signature):
		#remember to broadcast it


	def broadcast_transaction():





	def validdate_transaction():
		#use of signature and NBCs balance


	def add_transaction_to_block():
		#if enough transactions  mine



	def mine_block():



	def broadcast_block():


		

	def valid_proof(.., difficulty=MINING_DIFFICULTY):




	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		#resolve correct chain



