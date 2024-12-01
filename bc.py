from hashlib import sha256
from Crypto.PublicKey import RSA
import time
import random
import json


# Bablyon  
# Block Class
class Block:
    def __init__(self, id, previous_hash,transaction_list,notes,miner_address,difficulty,reward):
        """
        1 - identifier
            a- block hash 
            b - id
        2- header 
            a. 4-byte Version
            b. 4-byte Timestamp
            c. 4-byte Difficulty Target
            d. 4-byte Nonce
            e. 32-byte Previous Block Hash
            f. 32-byte Merkle Root
        """
        ### identifier 
        self.hash = self.calculate_block_hash()
        self.id = id 
        ### header 
        self.version = 1
        self.timestamp = self.set_block_time()
        self.previous_hash = previous_hash 
        self.difficulty_target = difficulty # changes will be made
        self.nonce = 0 # 32 bit value used to solve the POW 
        self.merkle_hash = self.calculate_merkle_root(self.transaction_list)
        ### Transactions
        self.coinbase_transaction = {
            "from": "Bablyon core",
            "to": miner_address,
            "amount": reward # Initial mining reward
        }
        transaction_list.insert(0, self.coinbase_transaction)
        self.transaction_list = transaction_list 
        self.data = '-'.join(transaction_list)
                
        
        self.note = notes
        
    def set_block_time(self):
        return time.time()

    def calculate_block_hash(self):
        return sha256(str(self).encode()).hexdigest()

    def calculate_merkle_root(self, transactions):
        if not transactions:
            return sha256(b'').hexdigest()

        hashes = [sha256(tx.encode()).hexdigest() for tx in transactions]

        while len(hashes) > 1:
            if len(hashes) % 2 != 0:  # Duplicate the last hash if odd
                hashes.append(hashes[-1])

            # Combine pairs and hash
            hashes = [sha256((hashes[i] + hashes[i + 1]).encode()).hexdigest()
                      for i in range(0, len(hashes), 2)]

        return hashes[0]

        
    def __repr__(self):
        return f"{self.index}, {self.previous_hash}, {self.timestamp}, {self.data}, {self.hash}, {self.nonce}"
    
    def __str__(self):
        return f"{self.index}-{self.previous_hash}-{self.timestamp}-{self.data}-{self.merkle_hash}-{self.nonce}"
    