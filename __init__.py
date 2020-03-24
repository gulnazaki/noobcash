from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api
from os.path import exists

from resources import *


app = Flask(__name__)
CORS(app)
api = Api()

running = None

api.add_resource(InformBootstrap, '/hello_bootstrap', resource_class_kwargs={'node': running})
api.add_resource(BroadcastRing, '/all_in', resource_class_kwargs={'node': running})
api.add_resource(Balance, '/balance', resource_class_kwargs={'node': running})
api.add_resource(CreateTransaction, '/transaction/create', resource_class_kwargs={'node': running})
api.add_resource(ValidateTransaction, '/transaction/validate', resource_class_kwargs={'node': running})
api.add_resource(ViewTransactions, '/transaction/view', resource_class_kwargs={'node': running})
api.add_resource(ValidateBlock, '/block/validate', resource_class_kwargs={'node': running})

api.init_app(app)

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-ip', '--ip-addr', default='127.0.0.1', type=str, help='IP address')
    parser.add_argument('-p', '--port', default=5000, type=int, help='Port to listen on')
    parser.add_argument('-bp', '--bootstrap', action='store_true', help='This node will be bootstrap')
    parser.add_argument('-mn', '--max-nodes', default=5, , type=int, help='The number of nodes the network will consist of')
    parser.add_argument('-nbc', '--NBC', default=100, , type=int, help='The number of NBCs each node will have when they all connect')
    parser.add_argument('-c', '--capacity', default=1, , type=int, help='How many transactions per block')
    parser.add_argument('-df', '--difficulty', default=4, , type=int, help='How many zeros a block\'s hash must start with to be considered solved')
    parser.add_argument('-d', '--debug', action='store_true', help='Run Flask in debug mode')
    args = parser.parse_args()

	if not exists('bootstrapconfig.txt'):
		print('Provide bootstrap\'s external IP and port at bootstrapconfig.txt')
		exit()
	with open('bootstrapconfig.txt','r') as b:
		bootstrap_ip = b.readline().strip()
		bootstrap_port = b.readline().strip()

    running = Node(args.bootstrap, args.max_nodes, args.NBC, args.capacity, args.difficulty, bootstrap_ip, bootstrap_port)


    app.run(host=args.ip_addr, port=args.port, debug=args.debug)