from flask import Flask, request, jsonify
import requests
from threading import Lock
import json
from typing import Set, Dict, List
import time
from bc import BlockChain, Block,Transaction,Wallet
from hashlib import sha256

class Node:
    def __init__(self, port: int, blockchain: BlockChain):
        self.app = Flask(__name__)
        self.port = port
        self.blockchain = blockchain
        self.peers: Set[str] = set()  # Set of peer URLs
        self.chain_lock = Lock()  # For thread safety
        self.setup_routes()
        
    def setup_routes(self):
        # Peer Management
        self.app.route('/peers', methods=['GET'])(self.get_peers)
        self.app.route('/peers/register', methods=['POST'])(self.register_peer)
        
        # Blockchain Routes
        self.app.route('/chain', methods=['GET'])(self.get_chain)
        self.app.route('/chain/length', methods=['GET'])(self.get_chain_length)
        self.app.route('/block/last', methods=['GET'])(self.get_last_block)
        
        # Transaction Routes
        self.app.route('/transaction/new', methods=['POST'])(self.new_transaction)
        self.app.route('/transaction/pending', methods=['GET'])(self.get_pending_transactions)
        
        # Block Routes
        self.app.route('/block/new', methods=['POST'])(self.new_block)
        
        # Sync Route
        self.app.route('/chain/sync', methods=['GET'])(self.sync_chain)

    def broadcast_to_peers(self, endpoint: str, data: dict = None, method: str = 'POST') -> List[dict]:
        """Broadcast data to all peers"""
        responses = []
        for peer in self.peers:
            try:
                url = f"{peer}{endpoint}"
                if method == 'POST':
                    response = requests.post(url, json=data, timeout=5)
                else:
                    response = requests.get(url, timeout=5)
                responses.append(response.json())
            except requests.RequestException as e:
                print(f"Failed to broadcast to {peer}: {e}")
        return responses

    def get_peers(self):
        """Return list of all peers"""
        return jsonify(list(self.peers))

    def register_peer(self):
        """Register a new peer"""
        peer_url = request.json.get('url')
        if peer_url and peer_url not in self.peers:
            self.peers.add(peer_url)
            # Notify the new peer about us
            try:
                requests.post(f"{peer_url}/peers/register", 
                            json={'url': f"http://localhost:{self.port}"})
            except requests.RequestException as e:
                print(f"Failed to notify peer {peer_url}: {e}")
            return jsonify({"message": "Peer registered successfully"})
        return jsonify({"message": "Invalid peer URL"}), 400

    def get_chain(self):
        """Return the full blockchain"""
        chain_data = []
        for block in self.blockchain.chain:
            chain_data.append({
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': block.transaction_list,
                'hash': block.hash,
                'previous_hash': block.previous_hash,
                'nonce': block.nonce
            })
        return jsonify(chain_data)

    def get_chain_length(self):
        """Return the length of the chain"""
        return jsonify({'length': len(self.blockchain.chain)})

    def get_last_block(self):
        """Return the last block"""
        block = self.blockchain.chain[-1]
        return jsonify({
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': block.transaction_list,
                'hash': block.hash,
                'previous_hash': block.previous_hash,
                'nonce': block.nonce
        })

    def new_transaction(self):
        """Add new transaction and broadcast to peers"""
        tx_data = request.json
        try:
            # Create transaction from request data
            tx = Transaction(
                sender=tx_data['sender'],
                recipient=tx_data['recipient'],
                amount=float(tx_data['amount']),
                fee=float(tx_data.get('fee', 0))
            )
            tx.signature = tx_data.get('signature')
            tx.sender_public_key = tx_data.get('sender_public_key')
            
            # Add to local pending transactions
            if self.blockchain.add_transaction(tx):
                # Broadcast to peers
                self.broadcast_to_peers('/transaction/new', tx_data)
                return jsonify({"message": "Transaction Broadcated Succs"})
            return jsonify({"message": "Invalid transaction"}), 400
            
        except (KeyError, ValueError) as e:
            return jsonify({"message": f"Invalid transaction data: {str(e)}"}), 400

    def get_pending_transactions(self):
        """Return all pending transactions"""
        return jsonify(list(self.blockchain.pending_transactions.values()))

    def new_block(self):
        """Add new block and broadcast to peers"""
        block_data = request.json
        with self.chain_lock:
            try:
                # Create block from request data
                block = Block(
                    index=block_data['index'],
                    previous_hash=block_data['previous_hash'],
                    transaction_list=block_data['transactions'],
                    miner_address=block_data['miner_address'],
                    difficulty=block_data['difficulty'],
                    reward=block_data['reward']
                )
                
                # Validate and add block
                if  block.previous_hash == self.blockchain.chain[-1].hash:
                    self.blockchain.chain.append(block)

                    # Broadcast to peers
                    self.broadcast_to_peers('/block/new', block_data)
                    return jsonify({"message": "Block added successfully"})
                return jsonify({"message": "Invalid block"}), 400
                
            except (KeyError, ValueError) as e:
                return jsonify({"message": f"Invalid block data: {str(e)}"}), 400

    def sync_chain(self):
        """Synchronize chain with peers"""
        max_length = len(self.blockchain.chain)
        best_chain = None
        
        # Get chains from all peers
        for peer in self.peers:
            try:
                response = requests.get(f"{peer}/chain", timeout=5)
                chain = response.json()
                
                # Validate received chain
                if len(chain) > max_length and self._is_valid_chain(chain):
                    max_length = len(chain)
                    best_chain = chain
                    
            except requests.RequestException as e:
                print(f"Failed to sync with peer {peer}: {e}")
                
        # Update our chain if we found a better one
        if best_chain:
            self.blockchain.chain = self._convert_chain_data(best_chain)
            return jsonify({"message": "Chain updated successfully"})
            
        return jsonify({"message": "Chain is already up to date"})

    def _is_valid_chain(self, chain_data: List[dict]) -> bool:
        """Validate a chain received from peers"""
        for i in range(1, len(chain_data)):
            if chain_data[i]['previous_hash'] != chain_data[i-1]['hash']:
                return False
        return True

    def _convert_chain_data(self, chain_data: List[dict]) -> List[Block]:
        """Convert chain data from JSON to Block objects"""
        return [Block(
            index=block['index'],
            previous_hash=block['previous_hash'],
            transaction_list=block['transactions'],
            miner_address=block['miner_address'],
            difficulty=block['difficulty'],
            reward=block['reward']
        ) for block in chain_data]

    def _remove_mined_transactions(self, transactions: List[Transaction]):
        """Remove transactions that were included in a block"""
        for tx in transactions:
            if isinstance(tx, dict):  # Skip coinbase transaction
                continue
            tx_hash = sha256(str(tx).encode()).hexdigest()
            self.blockchain.pending_transactions.pop(tx_hash, None)

    def run(self):
        """Start the node server"""
        self.app.run(host='0.0.0.0', port=self.port)