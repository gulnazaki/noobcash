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
                if self.hash_found.is_set():
                    break
                else:
                    self.node.lock.acquire()
                    self.node.blockchain.add_block(self.block)
                    self.node.broadcast_block(self.block.to_dict())
                    self.node.tx_pool = [tx for tx in self.node.tx_pool if not tx in self.block.transactions]

                    if len(self.node.tx_pool) >= CAPACITY:
                        self.node.create_new_block()
                    self.node.lock.release()
                    return
            else:
                nonce += 1

        self.node.lock.acquire()
        if len(self.node.tx_pool) >= CAPACITY:
            self.node.create_new_block()
        self.node.lock.release()
        return