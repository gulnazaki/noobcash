from flask import jsonify
from flask_restful import Resource

class InformBootstrap(Resource):
    
    def __init__(self, **kwargs):
        self.node = kwargs['node']

	def post(self):
		node_dict = request.form

		code, msg, idx, blockchain = self.node.register_node_to_ring(node_dict)
		if code != 200:
			response = {'msg': msg}
		else:
			response = {'msg': msg, 'id': idx, 'blockchain': blockchain}
			if idx == self.node.max_nodes - 1:
				self.node.broadcast_ring()
		return jsonify(response), code


class BroadcastRing(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

	def post(self):
		for idx, node in request.form.items():
			if idx in self.node.ring:
				msg = "I know about node " + str(idx) + " already"
				return jsonify({'msg': msg}), 400
			else:
				self.node.ring[idx] = node
		msg = "OK"
		return jsonify({'msg': msg}), 200


class Balance(Resource):

    def __init__(self, **kwargs):
        self.node = kwargs['node']

	def get(self):
		try:
			balance = self.node.wallet_balance()
		except:
			return jsonify({'msg': "Error"}), 400
		
		return jsonify({'msg': balance}), 200