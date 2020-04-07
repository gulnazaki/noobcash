from time import time
from threading import Thread, Event

class Mining(Thread):

    def __init__(self, node, block):
        Thread.__init__(self)
        self.node = node
        self.block = block
        self.hash_found = Event()

    def run(self):
        nonce = 0
        difficulty = self.node.difficulty
        hash_block = self.block.my_hash
        while not self.hash_found.is_set():
            possible_hash = hash_block(nonce)
            if possible_hash.startswith('0'*difficulty):
                self.block.mined(nonce, possible_hash)
                # print("mine ent")
                self.node.chain_lock.acquire()
                # print("er")
                if self.hash_found.is_set() or self.block.previous_hash != self.node.blockchain.last_hash():
                    self.node.chain_lock.release()
                    break
                else:
                    self.node.blockchain.add_block(self.block)
                    with self.node.tx_pool_lock:
                        self.node.tx_pool = [tx for tx in self.node.tx_pool if not tx in self.block.transactions]
                        poolsize = len(self.node.tx_pool)
                        transactions = self.node.tx_pool[:self.node.capacity]
                    self.node.chain_lock.release()
                    success, msg = self.node.broadcast_block(self.block.to_dict())
                    print(msg)
                    if poolsize >= self.node.capacity:
                        self.node.create_new_block(transactions)
                    return
            else:
                nonce += 1

        with self.node.tx_pool_lock:
            self.node.tx_pool = [tx for tx in self.node.tx_pool if not tx in self.block.transactions+self.node.blockchain.all_transactions()]
            poolsize = len(self.node.tx_pool)
            transactions = self.node.tx_pool[:self.node.capacity]
        if poolsize >= self.node.capacity:
            self.node.create_new_block(transactions)
        return
