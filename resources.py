from flask import jsonify, request
from flask_restful import Resource
from collections import OrderedDict
import json


class CreateTransaction(Resource):

	def __init__(self, **kwargs):
		self.node = kwargs['node']

	def post(self):
		recipient = request.form['recipient']
		amount = request.form['amount']

		success, msg = self.node.create_transaction(recipient, amount)
		if success: code = 200
		else:         code = 400

		return json.dumps({'msg': msg}), code


class ViewTransactions(Resource):

	def __init__(self, **kwargs):
		self.node = kwargs['node']

	def get(self):
		try:
			tx_list = self.node.view_transactions()
		except:
			return json.dumps({'msg': "Error"}), 400

		return json.dumps({'msg': "OK", 'tx_list': tx_list}), 200


class Balance(Resource):

	def __init__(self, **kwargs):
		self.node = kwargs['node']

	def get(self):
		try:
			balance = self.node.wallet_balance()
		except:
			return json.dumps({'msg': "Error"}), 400

		return json.dumps({'msg': "OK", 'balance': balance}), 200


class WelcomeNode(Resource):

	def __init__(self, **kwargs):
		self.node = kwargs['node']

	def post(self):
		node_dict = json.loads(request.form['node'])

		code, msg, idx, blockchain, utxos = self.node.register_node_to_ring(node_dict)
		if code != 200:
			response = {'msg': str(msg)}
		else:
			response = {'msg': msg, 'id': idx, 'blockchain': blockchain.to_dict(), 'utxos' : utxos}
			if idx == self.node.max_nodes - 1:
				self.node.broadcast_ring()
		return json.dumps(response), code


class AllNodesIn(Resource):

	def __init__(self, **kwargs):
		self.node = kwargs['node']

	def post(self):
		ring = OrderedDict(json.loads(request.form['ring']))
		for node in ring:
			node['utxos'] = OrderedDict(node['utxos'])

		self.node.ring = ring
		return json.dumps({'msg': "OK"}), 200


class ValidateTransaction(Resource):

	def __init__(self, **kwargs):
		self.node = kwargs['node']

	def post(self):
		tx_dict = json.loads(request.form['tx'])
		code, msg = self.node.validate_transaction(tx_dict)
		print(msg)
		return json.dumps({'msg': msg}), code


class ValidateBlock(Resource):

	def __init__(self, **kwargs):
		self.node = kwargs['node']

	def post(self):
		return


class ResolveConflict(Resource):

	def __init__(self, **kwargs):
		self.node = kwargs['node']
		self.blockchain = 
	def get(self):
		return
