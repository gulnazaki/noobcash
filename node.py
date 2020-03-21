from flask import make_response, abort, request
from wallet import Wallet
from block import Blockchain


class NewNode(Resource):

	def post(self):
		args = self.parser.parse_args()
		ip = args['ip']
		port = args['port']
        isbootstrap = args['is_bootstrap']
        max_nodes = args['max_nodes']
        NBC = args['NBC']

        n = Node(ip, port, is_bootstrap, max_nodes, NBC)


class Node:

	def __init__(self, ip, port, is_bootstrap=False, max_nodes=5, NBC=100):
		self.ip = ip
		self.port = port
		self.bootstrap = is_bootstrap
		self.max_nodes = max_nodes
		self.NBC = NBC
		self.wallet = Wallet()
		self.ring = []
		self.blockchain = Blockchain()

		if self.bootstrap:
			i_am_bootstrap()


		##set

		#self.chain
		#self.current_id_count
		#self.NBCs
		#self.wallet

		#slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 

	def i_am_bootstrap(self):
		self.id = 0
		self.current_nodes = 1
		node_dict = {'id': self.id, 'ip': self.ip, 'port': self.port, 'address': self.wallet.address, 'balance': self.wallet.balance()}
		self.ring.append(node_dict)
		self.blockchain.add_block(self.genesis_block())

	def genesis_block(self):
		amount = self.NBC * self.max_nodes
		

	def create_new_block():

	def create_wallet():
		#create a wallet for this node, with a public key and a private key

	def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs


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



