from bc import BlockChain, Transaction,Block
from node import Node
import sys
import time
from datetime import datetime
import logging
from colorama import init, Fore, Style
import threading
import json
from flask import jsonify,request

class EnhancedNode(Node):
    def __init__(self, port: int, blockchain: BlockChain):
        super().__init__(port, blockchain)
        init()  # Initialize colorama
        self.setup_logging()
        self.my_mined_blocks = 0
        self.start_time = time.time()
        
    def setup_logging(self):
        """Setup enhanced logging with colors"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(f'Node-{self.port}')
        
    def log_status(self):
        """Print periodic status updates"""
        while True:
            uptime = time.time() - self.start_time
            hours, remainder = divmod(int(uptime), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            self.logger.info(f"{Fore.CYAN}Node Status:")
            self.logger.info(f"├── Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.logger.info(f"├── Blocks Mined: {self.my_mined_blocks}")
            self.logger.info(f"├── Chain Length: {len(self.blockchain.chain)}")
            self.logger.info(f"├── Pending Transactions: {len(self.blockchain.pending_transactions)}")
            self.logger.info(f"└── Connected Peers: {len(self.peers)}{Style.RESET_ALL}")
            self.logger.info(f"└── Current reward: {len(self.blockchain.reward)}{Style.RESET_ALL}")
            self.logger.info(f"└── Connected difficulty : {len(self.blockchain.difficulty)}{Style.RESET_ALL}")
            time.sleep(50)  # Update every 5 minutes

    def new_transaction(self):
        """Enhanced transaction logging"""
        tx_data = request.json
        try:
            tx = Transaction(
                sender=tx_data['sender'],
                recipient=tx_data['recipient'],
                amount=float(tx_data['amount']),
                fee=float(tx_data.get('fee', 0))
            )
            
            if self.blockchain.add_transaction(tx):
                self.logger.info(
                    f"{Fore.GREEN}New Transaction:"
                    f"\n├── From: {tx.sender[:10]}..."
                    f"\n├── To: {tx.recipient[:10]}..."
                    f"\n├── Amount: {tx.amount}"
                    f"\n└── Fee: {tx.fee}{Style.RESET_ALL}"
                )
                self.broadcast_to_peers('/transaction/new', tx_data)
                return jsonify({"message": "Transaction added successfully"})
            return jsonify({"message": "Invalid transaction"}), 400
            
        except (KeyError, ValueError) as e:
            return jsonify({"message": f"Invalid transaction data: {str(e)}"}), 400

    def _mine_continuously(self):
        """Enhanced mining process with detailed logging"""
        while self.mining:
            with self.chain_lock:
                try:
                    start_time = time.time()
                    self.logger.info(f"{Fore.YELLOW}Starting mining round...{Style.RESET_ALL}")
                    
                    # Get pending transactions if any
                    transactions = list(self.blockchain.pending_transactions.values())
                    
                    # Create and mine new block
                    new_block = self.blockchain.mine_block(self.miner_address)
                    
                    if new_block:
                        mining_time = time.time() - start_time
                        self.my_mined_blocks += 1
                        
                        # Log success with details
                        self.logger.info(
                            f"{Fore.GREEN}Successfully Mined Block:"
                            f"\n├── Block #: {new_block.index}"
                            f"\n├── Hash: {new_block.hash[:15]}..."
                            f"\n├── Transactions: {len(new_block.transaction_list)}"
                            f"\n├── Mining Time: {mining_time:.2f}s"
                            f"\n├── Reward: {new_block.coinbase_transaction['amount']}"
                            f"\n└── Difficulty: {new_block.difficulty_target}{Style.RESET_ALL}"
                        )
                        
                        # Convert block to dictionary for broadcasting
                        block_data = {
                            'index': new_block.index,
                            'previous_hash': new_block.previous_hash,
                            'transactions': new_block.transaction_list,
                            'miner_address': self.miner_address,
                            'difficulty': new_block.difficulty_target,
                            'reward': new_block.coinbase_transaction['amount'],
                            'hash': new_block.hash,
                            'nonce': new_block.nonce,
                            'timestamp': new_block.timestamp
                        }
                        
                        # Broadcast new block
                        self.broadcast_to_peers('/block/new', block_data)
                        
                except Exception as e:
                    self.logger.error(f"{Fore.RED}Mining error: {e}{Style.RESET_ALL}")
                    
            time.sleep(1)

    def new_block(self):
        """Enhanced block reception logging"""
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
                
                if block.validate_block()[0] and block.previous_hash == self.blockchain.chain[-1].hash:
                    self.blockchain.chain.append(block)
                    self._remove_mined_transactions(block.transaction_list)
                    
                    self.logger.info(
                        f"{Fore.BLUE}New Block Received:"
                        f"\n├── Block #: {block.index}"
                        f"\n├── Miner: {block_data['miner_address'][:10]}..."
                        f"\n├── Transactions: {len(block.transaction_list)}"
                        f"\n└── Hash: {block.hash[:15]}...{Style.RESET_ALL}"
                    )
                    
                    self.broadcast_to_peers('/block/new', block_data)
                    return jsonify({"message": "Block added successfully"})
                return jsonify({"message": "Invalid block"}), 400
                
            except (KeyError, ValueError) as e:
                return jsonify({"message": f"Invalid block data: {str(e)}"}), 400

    def run(self):
        """Enhanced node startup"""
        self.logger.info(f"{Fore.CYAN}Starting node on port {self.port}")
        self.logger.info(f"├── Genesis Block: {self.blockchain.chain[0].hash[:15]}...")
        self.logger.info(f"├── Initial Difficulty: {self.blockchain.difficulty}")
        self.logger.info(f"└── Initial Reward: {self.blockchain.reward}{Style.RESET_ALL}")
        
        # Start status logging in background
        status_thread = threading.Thread(target=self.log_status)
        status_thread.daemon = True
        status_thread.start()
        
        self.app.run(host='0.0.0.0', port=self.port)

def start_node(port: int):
    """Start an enhanced blockchain node"""
    with open('config/node_config.json') as f:
        config = json.load(f)
        blockchain_local = config.get('blockchain_local')
        if blockchain_local:
            blockchain_file = config.get('blockchain_file')
            blockchain = BlockChain.load_chain(blockchain_file)
        else:
            blockchain = BlockChain()
    
    node = EnhancedNode(port, blockchain)
    node.start_mining()
    node.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_node.py <port>")
        sys.exit(1)
        
    try:
        port = int(sys.argv[1])
        start_node(port)
    except ValueError:
        print("Port must be a number")
        sys.exit(1)