import requests as r
from collections import OrderedDict
from multiprocessing import Process, Pool
from threading import Thread
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
        self.node_dict = {'ip': self.ip, 'port': self.port, 'address': self.wallet.address}

        self.mine_process = None

        if self.bootstrap:
            self.i_am_bootstrap()
        else:
            t = Thread(target=self.inform_bootstrap)
            t.start()


    def i_am_bootstrap(self):
        self.id = 0
        self.node_dict['utxos']: OrderedDict()
        self.ring = OrderedDict({self.id: self.node_dict})
        self.blockchain = Blockchain([self.genesis_block()])

    def genesis_block(self):
        amount = self.NBC * self.max_nodes
        transactions = [Transaction(sender_address='0', sender_private_key=None, receiver_address=self.wallet.address, amount=amount, ring=self.ring).to_dict()]

        return Block(idx=0, transactions=transactions, previous_hash='1', capacity=self.capacity, nonce='0')

    def inform_bootstrap(self):
        url = 'http://' + self.bootstrap_ip + ':' + self.bootstrap_port + '/hello_bootstrap'
        try:
            response = r.post(url, data={'node': json.dumps(self.node_dict)})
        except r.exceptions.RequestException as e:
        	print(e)
        	exit()
        if response.status_code != 200:
            print('Bootstrap says: "' + json.loads(response.json())['msg'] + '"')
            exit()
        else:
        	response = json.loads(response.json())
        	self.id = response['id']
        	self.blockchain = Blockchain(response['blockchain']['block_list'])
        	self.node_dict['utxos'] = OrderedDict(response['utxos'])
        	print("I am in with id " + str(self.id))

        	self.blockchain.validate(self.difficulty)

    def node_already_exists(self, new_node):
        msg = None
        for node in self.ring.values():
            if new_node['ip'] == node['ip'] and new_node['port'] == node['port']:
                msg = "You are already in with another wallet"
            if new_node['address'] == node['address']:
                msg = "I already have your wallet's address"
        return msg

    def register_node_to_ring(self, node_dict):
        if not self.bootstrap:
            return 400, "I am sorry, bootstrap is not here", None, None
        if self.max_nodes == len(self.ring):
            return 400, "Sorry we are full, " + str(self.max_nodes) + " nodes at a time", None, None
        msg = self.node_already_exists(node_dict)
        if msg:
            return 400, msg, None, None, None

        idx = len(self.ring)
   		node_dict['utxos'] = OrderedDict()
        self.ring[idx] = node_dict
        success, error = self.create_transaction(node_dict['address'], self.NBC)
        if not success:
            return 400, error, None, None, None
        else:
            return 200, "OK", idx, self.blockchain, self.ring[idx]['utxos']

    def send_stuff(self, url, data):
            response = r.post(url, data=data)
            return response.status_code == 200

    def broadcast(self, data, endpoint):
        node_list = [node for node_id, node in self.ring.items() if node_id != self.id]
        num_of_nodes = len(node_list)
        url_list = ['http://' + node['ip'] + ':' + node['port'] + endpoint for node in node_list]
        data_list = [data] * num_of_nodes

        p = Pool(num_of_nodes)

        successful = sum(p.starmap(self.send_stuff, zip(url_list, data_list)))

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
                             receiver_address=recipient, amount=amount, ring=self.ring).to_dict()
        except ValueError as e:
            return False, str(e)

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

    def validate_transaction(self, tx_dict):
        try:
        	tx = Transaction(sender_address=tx_dict['sender_address'], sender_private_key=None, receiver_address=tx_dict['receiver_address'],
        						amount=tx_dict['amount'], ring=self.ring, signature=tx_dict['signature'], inputs=tx_dict['inputs'], outputs=tx_dict['outputs'])
        except ValueError as e:
        	return 400, str(e)
        return 200, "Transaction validated"

    def add_transaction_to_block(self):
        #if enough transactions  mine
        return

    def create_new_block(self):
        return

    def mine_block(self):
        return

    def broadcast_block(self):
        return

    def wallet_balance(self):
        return sum(utxo['amount'] for utxo in self.node_dict['utxos'].values())

    def view_transactions(self):
        return self.blockchain.block_list[-1].transactions

    #def valid_proof(.., difficulty=MINING_DIFFICULTY):
    #    return

    #consensus functions


    def valid_chain(self, chain):
        #check for the longer chain accroose all nodes
        return

    def resolve_conflicts(self, **kwargs):
        new_block = kwargs['new_block']
        my_blockchain = self.blockchain
        iamwrong = False
        my_length = len(my_blockchain.block_list)
        for node in nodes:
            # call Resolve conflict
            found, l, position = Resolve
            if found & l > my_length:
                iamwrong = True

        if iamwrong:
            #request missing blocks

        #resolve correct chain

        return
