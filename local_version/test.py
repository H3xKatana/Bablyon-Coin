from bc import BlockChain, Block, Transaction, Wallet
from rich.console import Console
from rich.table import Table
import time


console = Console()

def display_blockchain(blockchain):
        table = Table(title="Blockchain Visualization")

        table.add_column("Index", style="cyan", justify="center")
        table.add_column("Hash", style="green")
        table.add_column("Previous Hash", style="red")
        table.add_column("Transactions", style="yellow")
        table.add_column("Nonce", style="magenta", justify="center")

        for block in blockchain.chain:
            table.add_row(
                str(block.index),
                block.hash[:8] + "...",
                block.previous_hash[:8] + "...",
                str(len(block.transaction_list)) + " transactions",
                str(block.nonce),
            )

        console.print(table)

def main():
    # Create BlockChain
    

    wallet1 = Wallet()
    wallet2 = Wallet()

    # Create a new blockchain
    blockchain = BlockChain()

    # Create some transactions
    tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    time.sleep(2)
    tx2 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    wallet1.sign_transaction(tx1)
    wallet1.sign_transaction(tx2)

    
    # Add transactions to the blockchain
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)
    print("Pending transactions:", blockchain.pending_transactions)

    # Mine a new block
    blockchain.mine_block(wallet1.get_address())
    print("Pending transactions:", blockchain.pending_transactions)
    print("Pending transactions:", blockchain.valid_transactions)
    # Print the blockchain
   
    
    display_blockchain(blockchain)
    # Verify the blockchain
    print("Verifying blockchain...")
    if blockchain.validate_chain():
        print("Blockchain is valid!")
    else:
        print("Blockchain is invalid!")


if __name__ == "__main__":
    main()

