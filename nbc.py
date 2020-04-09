from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from os.path import exists
from argparse import ArgumentParser
import requests
from time import sleep
from threading import Thread
import signal

from resources import *
from node import Node

app = Flask(__name__)
CORS(app)
api = Api()

@app.before_first_request
def initialize_node():
	running = Node(ip, port, args.bootstrap, args.max_nodes, args.NBC, args.capacity, args.difficulty, bootstrap_ip, bootstrap_port, args.transactions)

	api.add_resource(CreateTransaction, '/create_transaction', resource_class_kwargs={'node': running})
	api.add_resource(ViewTransactions, '/view_transactions', resource_class_kwargs={'node': running})
	api.add_resource(Balance, '/balance', resource_class_kwargs={'node': running})

	api.add_resource(WelcomeNode, '/hello_bootstrap', resource_class_kwargs={'node': running})
	api.add_resource(AllNodesIn, '/broadcast_ring', resource_class_kwargs={'node': running})
	api.add_resource(ValidateTransaction, '/validate_transaction', resource_class_kwargs={'node': running})
	api.add_resource(ValidateBlock, '/validate_block', resource_class_kwargs={'node': running})
	api.add_resource(ResolveConflict, '/resolve_conflict', resource_class_kwargs={'node': running})

	api.init_app(app)

	@app.route('/avg_block')
	def avg_block():
		running.write_block_times()
		return ("written")

@app.route('/')
def hello():
	return "hello"

def wake_up_the_server():
	def waking_the_server():
		sleeping = True
		while sleeping:
			try:
				requests.get('http://' + ip + ':' + port + '/')
				sleeping = False
			except:
				sleep(2)
	Thread(target=waking_the_server).start()

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('-ip', '--ip-addr', required=True, type=str, help='IP address')
	parser.add_argument('-p', '--port', default='5000', type=str, help='Port to listen on')
	parser.add_argument('-bp', '--bootstrap', action='store_true', help='This node will be bootstrap')
	parser.add_argument('-mn', '--max-nodes', default=5, type=int, help='The number of nodes the network will consist of')
	parser.add_argument('-nbc', '--NBC', default=100, type=int, help='The number of NBCs each node will have when they all connect')
	parser.add_argument('-c', '--capacity', default=1, type=int, help='How many transactions per block')
	parser.add_argument('-df', '--difficulty', default=4, type=int, help='How many zeros a block\'s hash must start with to be considered solved')
	parser.add_argument('-tx', '--transactions', action='store_true', help='Start running the transactions txts')
	parser.add_argument('-d', '--debug', action='store_true', help='Run Flask in debug mode')
	args = parser.parse_args()

	ip = args.ip_addr
	port = args.port
	
	def signal_handler(signum, frame):
		requests.get('http://' + ip + ':' + port + '/avg_block')
		exit()

	signal.signal(signal.SIGINT, signal_handler)
	
	if not exists('bootstrapconfig.txt'):
		print('Provide bootstrap\'s IP and port at bootstrapconfig.txt')
		exit()
	with open('bootstrapconfig.txt','r') as b:
		bootstrap_ip = b.readline().split(" ")[1].strip()
		bootstrap_port = b.readline().split(" ")[1].strip()

	if args.bootstrap and (ip != bootstrap_ip or port != bootstrap_port):
		print('Updating bootstrapconfig.txt')
		with open('bootstrapconfig.txt','w') as b:
			b.write('IP ' + ip + '\n')
			b.write('PORT ' + port + '\n')

	wake_up_the_server()
	app.run(host=ip, port=port, debug=args.debug)
