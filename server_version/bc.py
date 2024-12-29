
# Copyright (c) M_k(0xkatana) 2025
# Licensed under the MIT License 

from hashlib import sha256
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
import time
import base64 
import os
import pickle

# Bablyon  
# Block Class

class Block:
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
        self.index = index
        ### header
        self.version = 1 
        self.previous_hash = previous_hash
        self.difficulty_target = difficulty
        self.timestamp = self.set_block_time() 
        self.difficulty_target = difficulty # changes will be made
        self.nonce = 0 # 32 bit value used to solve the POW 
        self.merkle_hash = self.calculate_merkle_root(transaction_list)
        ### Transactions
        self.coinbase_transaction = {
            "from": "Bablyon core",
            "to": miner_address,
            "amount": reward # Initial mining reward
        }
        transaction_list.insert(0, self.coinbase_transaction)
        self.transaction_list = transaction_list
        self.data = [str(transaction) for transaction in transaction_list]
        self.total_fees = sum(tx.fee for tx in transaction_list if hasattr(tx, 'fee'))
        self.merkle_hash = self.calculate_merkle_root(transaction_list)
        self.hash = self.calculate_block_hash()
        self.size = len(self.data)

        # data maybe needed later 
        self.creation_time = time.time()
        self.mining_time = None
        self.propagation_delay = None
     
    def set_block_time(self):
        return int(time.time())
    
    def set_nonce(self,nonce):
        self.nonce =nonce
    def calculate_block_hash(self):
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
    
    def check_hash(self):
        return self.hash == self.calculate_block_hash()
        
    def set_nonce(self,nonce):
        self.nonce = nonce

    
    def calculate_block_reward(self) -> float:
        """Calculate total block reward including fees."""
        return self.reward + self.total_fees

    def __repr__(self):
        return f"{self.index}, {self.previous_hash}, {self.timestamp}, {self.data}, {self.hash}, {self.nonce}"
    
    def __str__(self):
        return f"{self.previous_hash}-{self.timestamp}-{self.data}-{self.merkle_hash}-{self.nonce}"
    
class Wallet:
    def __init__(self):
        """Initialize a wallet with an RSA key pair."""
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.private_key = self.key.export_key()
        self.create_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
    @staticmethod
    def load_wallet(private_key):
    
        private_key = base64.b64decode(private_key)
        if not private_key:
            raise ValueError("Private key is required to load wallet.")

        try:
            key = RSA.import_key(private_key)
        except (ValueError, IndexError) as e:
            raise ValueError("Invalid private key provided.") from e


        public_key = key.publickey().export_key()
        wallet = Wallet()
        wallet.key = key
        wallet.public_key = public_key
        wallet.private_key = private_key
        return wallet

    def get_public_key(self):
        """Get the public key encoded in Base64 format."""
        return base64.b64encode(self.public_key).decode()

    def get_private_key(self):
        """Get the private key encoded in Base64 format."""
        return base64.b64encode(self.private_key).decode()
    
    def get_address(self):
        """Generate a wallet address as a SHA-256 hash of the public key."""
        return sha256(self.public_key).hexdigest()
    
    def sign_transaction(self, transaction):
        """
        # The hash is padded according to PKCS#1 v1.5
        #the padeed signature is then encrypted with our private key
        # then it can be decrypted with our publickey
        # and we can compare the hash with the hash of the transaction 
        """
        digest = SHA256.new()
        digest.update(str(transaction).encode())
        signer = PKCS1_v1_5.new(self.key)
        signature = signer.sign(digest)
        transaction.signature = base64.b64encode(signature).decode()
        transaction.sender_public_key = self.get_public_key()

    @staticmethod
    def verify_transaction(transaction, signature, address) -> bool:
        """
        Verify a transaction signature using public key.
        
        Args:
            transaction: Transaction data (will be converted to string)
            signature: Base64 encoded signature
            address: Base64 encoded public key
        Returns:
            bool: True if signature is valid
        """
        key = RSA.import_key(base64.b64decode(address.encode()))
        digest = SHA256.new()
        digest.update(str(transaction).encode())
        signature_bytes = base64.b64decode(signature.encode())
        
        try:
            PKCS1_v1_5.new(key).verify(digest, signature_bytes)
            return True
        except (ValueError, TypeError):
            return False
    
    def get_creation_time(self):
        """Return the creation time of the wallet."""
        return self.create_time

class Transaction:
    def __init__(self, sender, recipient, amount ,fee=0):
        self.timestamp = int(time.time())
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.fee = fee
        self.signature = None
        self.sender_public_key = None
    
    def set_transaction(self,sender_public_key):
        self.sender_public_key  = sender_public_key
        
    def set_signature(self,signature):
        self.signature = signature

    def get_address(self):
        return self.sender
    
    def get_recpient(self):
        return self.recipient
     
    def get_amount(self):
        return self.amount

    def __str__(self):
        return f"{self.timestamp}|{self.sender}:{self.recipient}:{self.amount}-{self.fee}"

    def __repr__(self):
        return str(self)
    
    def verify_tx(self) -> bool:
        """Verify transaction signature and validity"""
        if None in (self.signature, self.sender_public_key):
            return False
            
        # Verify amount and fee are positive
        if self.amount <= 0 or self.fee < 0:
            return False
            
        # Verify signature
        return Wallet.verify_transaction(
            self,
            self.signature,
            self.sender_public_key
        )

class BlockChain:
    def __init__(self) -> None:
        # Configuration
        self.MAX_CHAIN_LENGTH = 1000000  # Maximum blocks in memory
        self.BLOCK_REWARD_HALVING_INTERVAL = 40  # Blocks until reward halves
        self.TARGET_BLOCK_TIME = 10  #  in seconds
        self.DIFFICULTY_ADJUSTMENT_WINDOW = 20  # Number of blocks for difficulty adjustment
        self.MAX_FUTURE_BLOCK_TIME = 60  # in seconds
        
        # Initialize chain state
        self.reward = 50
        self.difficulty = 4
        self.last_difficulty_adjustment = 0
        self.block_times = []
        self.total_work = 0  # Cumulative proof of work
        self.balances = {}
        # Create genesis block
        genesis_block = self._create_genesis_block()
        self.chain = [genesis_block]
        
        # Transaction pools
        self.pending_transactions = {}  # Hash -> Transaction
        self.valid_transactions = []
        
        # Initialize thread pool for parallel validation
        
        
        # Cache frequently accessed data
        self._cache = {}
        
    def _create_genesis_block(self) -> Block:
        """Create and return genesis block"""
        genesis = Block(
            index=0,
            previous_hash='0' * 64,
            transaction_list=[],
            miner_address="a65cbc8301aa2922c141dee61df860a0a407fce7581a2d8af098699f332856f9",
            difficulty=self.difficulty,
            reward=self.reward
        )
        genesis.previous_hash = '0' * 256
        return genesis
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add transaction to pending pool with validation"""
        try:
            # Basic validation
            if not transaction.verify_tx():
                print(f"Invalid transaction signature: {transaction}")
                return False
                
            # Check if transaction already exists
            tx_hash = sha256(str(transaction).encode()).hexdigest()
            if tx_hash in self.pending_transactions:
                print(f"Duplicate transaction: {tx_hash}")
                return False
            
            # Add to pending pool
            self.pending_transactions[tx_hash] = transaction
            print(f"Added transaction {tx_hash} to pending pool")
            return True
            
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def mine_block(self, miner_address: str) :
        """Mine a new block with improved difficulty adjustment"""
        try:
            # Verify and select transactions
            valid_txs = self._select_transactions()
            
            # Create new block
            new_block = Block(
                index=len(self.chain),
                previous_hash=self.get_last_block_hash(),
                transaction_list=valid_txs,
                miner_address=miner_address,
                difficulty=self.difficulty,
                reward=self._calculate_reward()
            )
            
            # Mine block
            start_time = time.time()
            if self._mine_block(new_block):
                # Update chain state
                new_block.mining_time = time.time() - start_time
                self.chain.append(new_block)
                self._update_chain_state(new_block)
                self._remove_mined_transactions(valid_txs)
                self.save_chain("blockchain.dat")
                print(f"Successfully mined block {new_block.hash}")
                return new_block
            
            return None
            
        except Exception as e:
            print(f"Error mining block: {e}")
            return None
    
    def _calculate_balances(self):
        """Calculate the balance of each address"""
        self.balances = {}
        for block in self.chain:
            for tx in block.transaction_list:
                if tx.sender not in self.balances:
                    self.balances[tx.sender] = 0
                if tx.receiver not in self.balances:
                    self.balances[tx.receiver] = 0
                self.balances[tx.sender] -= tx.amount 
                self.balances[tx.receiver] += tx.amount
        return self.balances
    
    def _has_sufficient_balance(self, tx):
        
        """Check if the sender has enough balance for the transaction"""
        return self.balances.get(tx.sender, 0) >= tx.amount + tx.fee
    
    def _select_transactions(self) :
        
            """Select and validate transactions for new block"""
            valid_txs = []
            total_size = 0

            # Sort by fee per byte
            sorted_txs = sorted(
                self.pending_transactions.values(),
                key=lambda tx: tx.fee / len(str(tx))
            )

            for tx in sorted_txs:
                tx_size = len(str(tx))
                if total_size + tx_size > Block.MAX_BLOCK_SIZE:
                    break
                if  self._has_sufficient_balance(tx):
                    if tx.verify_tx():
                        valid_txs.append(tx)
                        total_size += tx_size

            return valid_txs       
    
    def _mine_block(self, block: Block) -> bool:
        """Perform proof-of-work mining"""
        target = '0' * self.difficulty
        max_nonce = 2**32
        
        for nonce in range(max_nonce):
            block.nonce = nonce
            block_hash = block.calculate_block_hash()
            
            if block_hash[:self.difficulty] == target:
                block.hash = block_hash
                return True
                
        return False
    
    def _update_chain_state(self, block: Block) -> None:
        """Update blockchain state each  new block appended """
        # Update difficulty
        if len(self.chain) % self.DIFFICULTY_ADJUSTMENT_WINDOW == 0:
            self._adjust_difficulty()
        
        # Update reward
        if len(self.chain) % self.BLOCK_REWARD_HALVING_INTERVAL == 0:
            self.reward /= 2
        
        # Total work of the chain will be used for consexne algorithm
        self.total_work += 2 ** self.difficulty
        
        # Record block time
        self.block_times.append(block.timestamp)
        
        
        self._calculate_balances()
    
    def _adjust_difficulty(self) -> None:
        """Adjust mining difficulty based on block times"""
        if len(self.block_times) < self.DIFFICULTY_ADJUSTMENT_WINDOW:
            return
            
        time_taken = self.block_times[-1] - self.block_times[-self.DIFFICULTY_ADJUSTMENT_WINDOW] # retrive the last blocks for adjusment 
        expected_time = self.TARGET_BLOCK_TIME * self.DIFFICULTY_ADJUSTMENT_WINDOW # total time that was initily needed 
        
        if time_taken < expected_time / 2:
            self.difficulty += 1
        elif time_taken > expected_time * 2:
            self.difficulty = max(1, self.difficulty - 1)
            
        print(f"Adjusted difficulty to {self.difficulty}")
    
    def get_address_balance(self,address):
        return self.balances.get(address,0)

    def _calculate_reward(self) -> float:
        """Calculate current block reward"""
        # each time length of the chain reach BlOCK_REWARD_Halving the reward will be halved 
        return self.reward / (2 ** (len(self.chain) // self.BLOCK_REWARD_HALVING_INTERVAL))
    
    def validate_chain(self, chain = None) -> bool:
        """Validate entire blockchain"""
        chain = chain or self.chain
        
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i-1]
            
            # Validate block order
            if current.index != previous.index + 1:
                return False
            
            # Validate hash linkage
            if current.header.previous_hash != previous.hash:
                return False
            
            # Validate block hash
            if current.hash != current.calculate_block_hash():
                return False
            
            # Validate merkle root
            if not current.validate_merkle_root():
                return False
            
            # Validate timestamp
            if current.header.timestamp <= previous.header.timestamp:
                return False
            
            # Validate transactions
            try:
                current._validate_transactions(current.transaction_list)
            except ValueError:
                return False
        
        return True

    def save_chain(self, filepath):
        """Save the blockchain to a file."""
        with open(filepath, 'wb') as file:
            pickle.dump(self.chain, file)
        print(f"Blockchain saved to {filepath}")

    @staticmethod
    def load_chain(filepath) :
        """Load the blockchain from a file."""
        if not os.path.exists(filepath):
            chain = BlockChain()
            return chain

    
        with open(filepath, 'rb') as file:
            chain = pickle.load(file)
        print(f"Blockchain loaded from {filepath}")

        return chain

    def get_last_block_hash(self):
        self.chain[-1].hash


    def is_valid_block(self,block):
        """
        :param block: The block to check
        :return: True if the block is valid, False otherwise
        """
        # Check if the block index is valid
        if block.index < 0:
            return False

        # Check if the block hash is valid
        if block.hash != block.calculate_block_hash():
            return False

        # Check if the block timestamp is valid
        if block.timestamp < 0:
            return False

        # Check if the block nonce is valid
        if block.nonce < 0:
            return False

        # Check if the block previous hash is valid
        if block.previous_hash is None or len(block.previous_hash) != 256 // 8:
            return False



        # Check if the block merkle root is valid
        if not block.validate_merkle_root():
            return False

        return True



