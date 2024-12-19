
from hashlib import sha256
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
import time
import json
import base64 



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
        self.data = json.dumps(transaction_list, separators=(',', ':'))
        self.merkle_hash = self.calculate_merkle_root(transaction_list)
        self.hash = self.calculate_block_hash()
        
    def set_block_time(self):
        return int(time.time())
        
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
    
    def  check_hash(self):
        return self.hash == self.calculate_block_hash()
        
    def set_nonce(self,nonce):
        self.nonce = nonce

    def calculate_merkle_root(self, transactions):
        hashes = [sha256(str(tx).encode()).digest() for tx in transactions]
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            hashes = [sha256(hashes[i] + hashes[i + 1]).digest() for i in range(0, len(hashes), 2)]
        return hashes[0].hex() if hashes else sha256(b'').hexdigest()
    
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
        genesis_block = Block(0, 'f'*64, [], "satoshi", self.difficulty, self.reward)
        genesis_block.previous_hash = '0'*256
        print(genesis_block)
        self.chain = [genesis_block]
        
        self.pending_transactions = []
        self.valid_transactions =[]
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def get_last_block_hash(self):
        return self.chain[-1].hash
    
    def verify_transactions(self):
        for i in range(1,len(self.pending_transactions)):
            tx = self.pending_transactions[i]
            if tx.verify_transaction():
                self.valid_transactions.append(tx)
            
        return self.valid_transactions
  
    def mine_block(self, miner_address):
        self.verify_transaction(self)
        if not self.valid_transactions:
            print("No valid transactions to mine")
            return
        
        nonce = 0
        new_block = Block(len(self.chain), self.get_last_block_hash(), self.valid_transactions, miner_address, self.difficulty, self.reward)
        
        target = '0' * self.difficulty
        calculate_hash = new_block.calculate_block_hash
        
        max_nonce = 2**32  # max size of the integer 4 bytes
        while new_block.hash[:self.difficulty] != target:
            if nonce >= max_nonce:
                print("Failed to find a valid nonce")
                return
            nonce += 1
            new_block.set_nonce(nonce)
            new_block.hash = calculate_hash()
        
        if new_block.hash[:self.difficulty] == target:  
            print("found a valid block hash :",new_block.hash)
            self.chain.append(new_block)
            self.valid_transactions = []      

    def validate_chain(self):
        if not self.chain:
            return False
        
        for i in range(1, len(self.chain)):

            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if not current_block or not previous_block:
                return False
            previous_hash = previous_block.hash
            if current_block.previous_hash != previous_hash:
                return False
        return True


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
        """
        # The hash is padded according to PKCS#1 v1.5
        #the padeed signature is then encrypted with our private key
        # then it can be decrypted with our publickey
        # and we can compare the hash with the hash of the transaction 
        """
        transaction_hash = sha256(str(transaction).encode()).digest()
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
    def __init__(self, sender, recipient, amount ):
        self.timestamp = int(time.time())
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = None


    def __str__(self):
        return f"{self.timestamp}|{self.sender}:{self.recipient}:{self.amount}"

    def __repr__(self):
        return str(self)
    
    @staticmethod
    def verify_transaction(self):
        if self.signature is None:
            return False
        return Wallet.verify_transaction(self, self.signature, self.sender)



def main():
    # Create a new wallet
    wallet1 = Wallet()
    wallet2 = Wallet()
    print("Wallet public key:", wallet1.get_public_key())
    print("Wallet address:", wallet1.get_address())
    print("Wallet public key:", wallet2.get_public_key())
    print("Wallet address:", wallet2.get_address())

    # Create a new blockchain
    blockchain = BlockChain()

    # Create some transactions
    tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    tx2 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    print(tx1)
    wallet1.sign_transaction(tx1)
    wallet1.sign_transaction(tx1)
    # Add transactions to the blockchain
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)


    # Mine a new block
    blockchain.mine_block(wallet1.get_address())

    # Print the blockchain
    print("Blockchain:")
    for block in blockchain.chain:
        print(block)

    # Verify the blockchain
    print("Verifying blockchain...")
    if blockchain.validate_chain():
        print("Blockchain is valid!")
    else:
        print("Blockchain is invalid!")

    # Try to tamper with the blockchain
    blockchain.chain[1].transaction_list[0].amount = 100
    print("Tampering with blockchain...")
    if blockchain.validate_chain():
        print("Blockchain is still valid!")
    else:
        print("Blockchain is invalid!")

if __name__ == "__main__":
    main()
