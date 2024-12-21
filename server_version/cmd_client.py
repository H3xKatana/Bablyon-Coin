from bc import Wallet,Transaction
from requests import get , post 
from Crypto.PublicKey import RSA 


class Client:
    
    def action_list(self):
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

    def create_wallet(self,wallet_file=None):
        wallet = Wallet()
        print(f"Your Public Key: {wallet.get_public_key()}")
        print(f"Your Private Key: {wallet.get_private_key()}")
        print(f"Your Address: {wallet.get_address()}")
        try:
            if wallet_file != None:
                with open(wallet_file, 'w') as f:
                    f.write(wallet.get_private_key())
                print(f"Wallet created and saved to {wallet_file}")
                return wallet
            else:
                with open('wallet.bc', 'w') as f:
                    f.write(wallet.get_private_key())
                print("Wallet created and saved to wallet.bc")
                return wallet
        except FileExistsError:
            print("File already exists")
            

    def load_wallet(self):
        try:
            with open('wallet.bc', 'r') as f:
                private_key = f.read()
            return Wallet.load_wallet(private_key)
        except FileNotFoundError:
            print("Wallet file not found")
            return None

    def send_transaction(self):
        """
        this function broadcast the transaction to the network
        """
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


def main():
    clinet = Client() 
    while True:
        clinet.action_list()
