
from hashlib import sha256
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
import time
import random
import json
import base64 



# Bablyon  
# Block Class

class Block:
    def __init__(self, index, previous_hash, transaction_list, miner_address, difficulty, reward):
        """Block initialization with header, identifier, and transactions."""
    def __init__(self, index, previous_hash,transaction_list,miner_address,difficulty,reward):
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
        3-Transcations
            a-coinbase transaction
            b-pending transcations
        """
        ### identifier 
        self.hash = self.calculate_block_hash()
        self.index = index
        self.previous_hash = previous_hash
        self.difficulty_target = difficulty
        self.nonce = 0
        self.timestamp = int(time.time())
        ### header 
        self.version = 1
        self.timestamp = self.set_block_time()
        self.previous_hash = previous_hash 
        self.difficulty_target = difficulty # changes will be made
        self.nonce = 0 # 32 bit value used to solve the POW 
        self.merkle_hash = self.calculate_merkle_root(transaction_list)
        ### Transactions
        self.coinbase_transaction = {
            "from": "Bablyon core",
            "to": miner_address,
            "amount": reward # Initial mining reward
        }
        
        self.coinbase_transaction = {
            "from": "Bablyon core",
            "to": miner_address,
            "amount": reward
        }
        transaction_list.insert(0, self.coinbase_transaction)
        self.transaction_list = transaction_list
        self.data = json.dumps(transaction_list, separators=(',', ':'))

        
        self.merkle_hash = self.calculate_merkle_root(transaction_list)
        self.hash = self.calculate_block_hash()
        
    def set_block_time(self):
        return int(time.time())
        return time.time()

    def calculate_block_hash(self):
        return sha256(self.__str__().encode()).hexdigest()
        return sha256(str(self).encode()).hexdigest()

    def calculate_merkle_root(self, transactions):
        if not transactions:
            return sha256(b'').hexdigest()

        hashes = [sha256(str(tx).encode()).digest() for tx in transactions]


        while len(hashes) > 1:
            if len(hashes) % 2 != 0:  # Duplicate the last hash if odd
                hashes.append(hashes[-1])

            # Combine pairs and hash
            hashes = [sha256(hashes[i] + hashes[i + 1]).digest()
            
                      for i in range(0, len(hashes), 2)]

        return hashes[0].hex()

    
    def calculate_block_hash(self):
        return sha256(f"{self.previous_hash}-{self.timestamp}-{self.data}-{self.merkle_hash}-{self.nonce}".encode()).hexdigest()
    
    def  check_hash(self):
        return self.hash == self.calculate_block_hash()
        

    def calculate_merkle_root(self, transactions):
        hashes = [sha256(str(tx).encode()).digest() for tx in transactions]
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            hashes = [sha256(hashes[i] + hashes[i + 1]).digest() for i in range(0, len(hashes), 2)]
        return hashes[0].hex() if hashes else sha256(b'').hexdigest()
    def __repr__(self):
        return f"{self.index}, {self.previous_hash}, {self.timestamp}, {self.data}, {self.hash}, {self.nonce}"
    
    def __str__(self):

    def check_hash(self):
        return self.hash == self.calculate_block_hash()
    
    def __repr__(self):
        return f"{self.index}, {self.previous_hash}, {self.timestamp}, {self.data}, {self.hash}, {self.nonce}"
    
    def __str__(self):
        return f"{self.previous_hash}-{self.timestamp}-{self.data}-{self.merkle_hash}-{self.nonce}"

class BlockChain:
    
    def __init__(self) -> None:
        self.reward = 50 
        self.difficulty = 4
        genesis_block = Block(0, '0'*256, [], "satoshi", self.difficulty, self.reward)
        self.chain = [genesis_block]
        self.node_pending_transactions = []
        


class Wallet:
    def __init__(self):
        """Initialize a wallet with an RSA key pair."""
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.private_key = self.key.export_key()

    def get_public_key(self):
        """Get the public key encoded in Base64 format."""
        return base64.b64encode(self.public_key).decode()

    def get_address(self):
        """Generate a wallet address as a SHA-256 hash of the public key."""
        return sha256(self.public_key).hexdigest()
    
    def sign_transaction(self, transaction):
        transaction_hash = sha256(str(transaction).encode()).hexdigest()

        # The hash is padded according to PKCS#1 v1.5
        #the padeed signature is then encrypted with our private key
        # then it can be decrypted with our publickey
        # and we can compare the hash with the hash of the transaction 
        signature = PKCS1_v1_5.new(self.key).sign(transaction_hash)

        return base64.b64encode(signature).decode()
    

    @staticmethod
    def verify_transaction( transaction, signature, address) -> bool:
        """
        Verify a transaction signature using public key.
        
        Args:
            transaction: Transaction data (will be converted to string)
            signature: Base64 encoded signature
            address: Base64 encoded public key
        Returns:
            bool: True if signature is valid
        """
        key = RSA.import_key(base64.b64decode(address))
        transaction_hash = sha256(str(transaction).encode()).digest()
        signature_bytes = base64.b64decode(signature)

        try:
            PKCS1_v1_5.new(key).verify(transaction_hash, signature_bytes)
            return True
        except (ValueError, TypeError):
            return False



class Transaction:


    __slots__ = ('sender', 'recipient', 'amount')

    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount


    def __str__(self):
        return f"{self.sender}:{self.recipient}:{self.amount}"

    def __repr__(self):
        return str(self)
    
    def verify(self, signature, address):
        return Wallet.verify_transaction(self, signature, address)
