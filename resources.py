from flask import jsonify
from flask_restful import Resource
from collections import OrderedDict


class CreateTransaction(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

    def post(self):
        recipient = request.form['recipient']
        amount = request.form['amount']

        success, msg = self.node.create_transaction(recipient, amount)
        if success: code = 200
        else:         code = 400

        return jsonify({'msg': msg}), code


class ViewTransactions(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.node.view_transactions()

    def get(self):
        return


class Balance(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

    def get(self):
        try:
            balance = self.node.wallet_balance()
        except:
            return jsonify({'msg': "Error"}), 400

        return jsonify({'msg': balance}), 200


class WelcomeNode(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

    def post(self):
        node_dict = json.loads(request.form['node'])
        node_dict['utxos'] = OrderedDict(node_dict['utxos'])

        code, msg, idx, blockchain = self.node.register_node_to_ring(node_dict)
        if code != 200:
            response = {'msg': msg}
        else:
            response = {'msg': msg, 'id': idx, 'blockchain': blockchain}
            if idx == self.node.max_nodes - 1:
                self.node.broadcast_ring()
        return jsonify(response), code


class AllNodesIn(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

    def post(self):
        ring = OrderedDict(json.loads(request.form['ring']))
        for node in ring:
            node['utxos'] = OrderedDict(node['utxos'])

        self.node.ring = ring
        return jsonify({'msg': "OK"}), 200


class ValidateTransaction(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

    def post(self):
        return


class ValidateBlock(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

    def post(self):
        return


class ResolveConflict(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

    def get(self):
        return
