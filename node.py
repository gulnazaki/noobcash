import requests as r
from collections import OrderedDict
from multiprocessing import Pool
import json

from wallet import Wallet
from block import Block, Blockchain
from transaction import Transaction


class Node:

    def __init__(self, ip, port, is_bootstrap, max_nodes, NBC, capacity, difficulty, bootstrap_ip, bootstrap_port):
        self.ip = ip
        self.port = port
        self.bootstrap = is_bootstrap
        self.max_nodes = max_nodes
        self.NBC = NBC
        self.capacity = capacity
        self.difficulty = difficulty
        self.bootstrap_ip = bootstrap_ip
        self.bootstrap_port = bootstrap_port

        self.wallet = Wallet()
        self.tx_pool = OrderedDict()
        self.node_dict = {'ip': self.ip, 'port': self.port, 'address': self.wallet.address, 'utxos': OrderedDict()}

        self.mine_process = None

        if self.bootstrap:
            self.i_am_bootstrap()
        else:
            self.inform_bootstrap()
            self.blockchain.validate(self.difficulty)


    def i_am_bootstrap(self):
        self.id = 0
        self.ring = OrderedDict({self.id: self.node_dict})
        self.blockchain = Blockchain([self.genesis_block()])

    def genesis_block(self):
        amount = self.NBC * self.max_nodes
        transactions = [Transaction(sender_address='0', sender_private_key=None, receiver_address=self.wallet.address, amount=amount, ring=self.ring).to_dict()]

        return Block(idx=0, transactions=transactions, previous_hash='1', capacity=self.capacity, nonce='0')

    def inform_bootstrap(self):
        url = 'http://' + self.bootstrap_ip + ':' + self.bootstrap_port + '/hello_bootstrap'
        response = r.post(url, data={'node': json.dumps(self.node_dict)})
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
        if msg:
            return 400, msg, None, None

        idx = len(self.ring)
        self.ring[idx] = node_dict
        success, error = self.create_transaction(node_dict['address'], self.NBC)
        if not success:
            return 400, error, None, None
        else:
            return 200, "OK", idx, self.blockchain

    def broadcast(self, data, endpoint):
        node_list = [node for node_id, node in self.ring.items() if node_id != self.id]
        num_of_nodes = len(node_list)
        url_list = ['http://' + node['ip'] + ':' + node['port'] + endpoint for node in node_list]
        data_list = [data] * num_of_nodes

        p = Pool(num_of_nodes)

        def send_stuff(url, data):
            response = r.post(url, data=data)
            return response.status_code == 200

        successful = sum(p.starmap(send_stuff, zip(url_list, data_list)))

        return successful == num_of_nodes

    def broadcast_ring(self):
        success = self.broadcast(data={'ring': json.dumps(self.ring)}, endpoint='/broadcast_ring')
        if not success:
            print("Failed broadcasting ring")
            exit()
        else:
               print("All nodes are informed, let\'s start")

    def create_transaction(self, recipient, amount):
        try:
            tx = Transaction(sender_address=self.wallet.address, sender_private_key=self.wallet.private_key,
                             receiver_address=recipient, amount=amount, ring=self.ring).to_dict
        except ValueError as e:
            return False, e

        self.add_to_pool(tx)
        return self.broadcast_transaction(tx)

    def add_to_pool(self, tx):
        self.tx_pool[tx['transaction_id']] = tx

        if len(self.tx_pool) >= self.capacity:
            if not self.mine_process or not self.mine_process.is_alive():
                self.create_new_block()

    def broadcast_transaction(self, tx):
        success = self.broadcast(data={'tx': json.dumps(tx)}, endpoint='/validate_transaction')
        if success:
            msg = ("All nodes know about transaction " + tx['transaction_id'] + " now")
        else:
               msg = "Failed broadcasting transaction"

        return success, msg

    def validate_transaction():
        #use of signature and NBCs balance
        return

    def add_transaction_to_block():
        #if enough transactions  mine
        return

    def create_new_block():
    	return

    def mine_block():
    	return

    def broadcast_block():
    	return

    def wallet_balance(self):
        return sum(utxo['amount'] for utxo in self.ring[self.id]['utxos'].values())

    def view_transactions(self):
        return self.blockchain.block_list[-1]

    #def valid_proof(.., difficulty=MINING_DIFFICULTY):
    #	return

    #consensus functions


    def valid_chain(self, chain):
        #check for the longer chain accroose all nodes
    	return

    def resolve_conflicts(self):
        #resolve correct chain
    	return
