from hashlib import sha256
from Crypto.PublicKey import RSA
import time
import random
import json


# Bablyon  
# Block Class
class Block:
    def __init__(self, id, previous_hash,transaction_list,notes):
        self.id = id 
        self.previous_hash = previous_hash 
        self.timestamp = self.get_time()
        self.transaction_list = transaction_list 
        self.data = '-'.join(transaction_list)
        self.merkle_hash = self.calculate_merkle_root(self.transaction_list)
        self.hash = self.calculate_block_hash()
        self.nonce = 0 # 32 bit value used to solve the POW 
        self.note = notes
        
    def get_time(self):
        return time.time()

    def calculate_block_hash(self):
        return sha256((str(self.index) + str(self.previous_hash) + str(self.timestamp) + str(self.merkle_hash)+str(self.data) + str(self.nonce)).encode()).hexdigest()

    def calculate_merkle_root(transactions):
    # hash value let you verify all transcations easily with a single hash
    
        hashes = [sha256(tx) for tx in transactions]

        if len(transactions) == 1:
            return sha256(transactions[0])
        
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:  # Duplicate the last hash if odd
                hashes.append(hashes[-1])

            # Combine pairs and hash
            new_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_level.append(sha256(combined))

            hashes = new_level

        return hashes[0]
        
    def __repr__(self):
        return f"Block({self.index}, {self.previous_hash}, {self.timestamp}, {self.data}, {self.hash}, {self.nonce})"
    
    def __str__(self):
        return f"{self.index}-{self.previous_hash}-{self.timestamp}-{self.data}-{self.hash}-{self.merkle_hash}-{self.nonce})"
    

