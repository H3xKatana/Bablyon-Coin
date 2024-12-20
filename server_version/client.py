import sys
sys.path.append('../')

from local_version.bc import Wallet
from local_version.bc import Transaction
from requests import get , post 
from Crypto.PublicKey import RSA 


class client:
    def __init__(self):
        action_map = {
            '1': self.create_wallet,
            '2': self.send_transaction,
            '3': self.get_balance,
            '4': self.check_transactions,
            '5': self.exit,
            '6': self.load_wallet,
        }
        while True:
            action = input ("""
                            1. Create Wallet
                            2. Send Transaction 
                            3. Get Balance
                            4. check transactions 
                            5. Exit
                            """)
            if action in action_map:
                action_map[action]()
                break
            print("Invalid Action")
        

    def create_wallet(self):
        wallet = Wallet()
        print(f"Your Public Key: {wallet.get_public_key()}")
        print(f"Your Private Key: {wallet.get_private_key()}")
        print(f"Your Address: {wallet.get_address()}")
        try:
            with open('wallet.bc', 'w') as f:
                f.write(wallet.get_private_key())
            print("Wallet created and saved to wallet.bc")
        except FileExistsError:
            print("File already exists")
            

    def load_wallet(self):
        try:
            with open('wallet.bc', 'r') as f:
                private_key = f.read()
                print('####DEBUG private_key:', private_key)
            return Wallet.load_wallet(private_key)
        except FileNotFoundError:
            print("Wallet file not found")
            return None

    def send_transaction(self):
        sender = self.load_wallet()
        if sender == None:
            print("Wallet not found")
            return
        receiver = input("Enter the receiver's address: ")
        amount = input("Enter the amount to send: ")
        tx = Transaction(sender.get_address(), receiver, amount)
        sender.sign_transaction(tx)
        print("Transaction signed")
       
        print("Transaction signature: ", str(tx))


    def get_balance(self):
        sender = self.load_wallet()
        address = sender.get_address()
        pass


    def check_transactions(self):
        sender = self.load_wallet()
        address = sender.get_address()
        pass


    def exit(self):
        print("Goodbye!")
        exit()



clinet = client() 