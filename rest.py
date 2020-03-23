from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api

from wallets import WalletBalance
from transaction import CreateTransaction, ValidateTransaction, ViewTransactions
from block import ValidateBlock
from Node import NewNode, InformBootstrap


app = Flask(__name__)
CORS(app)

api = Api()

api.add_resource(NewNode, '/node/new')
api.add_resource(InformBootstrap, '/node/hello_bootstrap')
api.add_resource(BroadcastRing, '/node/all_in')
api.add_resource(WalletBalance, '/wallet/balance')
api.add_resource(CreateTransaction, '/transaction/create')
api.add_resource(ValidateTransaction, '/transaction/validate')
api.add_resource(ViewTransactions, '/transaction/view')
api.add_resource(ValidateBlock, '/block/validate')

api.init_app(app)

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-ip', '--ip-addr', default='127.0.0.1', type=str, help='IP address')
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-d', '--debug', action='store_true', help='Run Flask in debug mode')
    args = parser.parse_args()

    app.run(host=args.ip_addr, port=args.port, debug=args.debug)