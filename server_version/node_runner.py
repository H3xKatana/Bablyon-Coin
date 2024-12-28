from bc import BlockChain
from node import Node 
import sys
def start_node(port: int):
    """Start a blockchain node on the specified port"""
    # Initialize blockchain
    blockchain = BlockChain()
    
    # Create and start node
    node = Node(port, blockchain)
    
    print(f"Node starting on port {port}")
    node.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_node.py <port>")
        sys.exit(1)
        
    port = int(sys.argv[1])
    start_node(port)