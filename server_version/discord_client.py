import discord
from discord.ext import commands
import json
from bc import Wallet
from cmd_client import Client as cmd_client

# Load configuration from config.json
with open('config/bot_config.json') as f:
    config = json.load(f)

# Create a new client instance
intents = discord.Intents.default()
client = discord.Client(intents=intents)
bot_client = cmd_client()

# Define commands
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # dont respond to ourselves the bot itself
    if message.author == client.user:
       
        return

    if message.content.startswith('$createwallet'):
    # Create a wallet using the wallet module
        wallet = bot_client.create_wallet()
        if isinstance(message.channel, discord.TextChannel):
            # Create a custom thread for the user
            thread = await message.channel.create_thread(name=f"Wallet Info - {message.author.name}", auto_archive_duration=60)
            # Dump the private key directly into a file
            
            with open("wallet.bc", "w") as f:
                f.write(wallet.get_private_key())
            
            # Send the file to the custom thread
            await thread.send(file=discord.File("wallet.bc"))
        else:
            # Handle the case where the channel is not a guild channel
            await message.channel.send(file=discord.File("wallet.bc"))
        
        


    if message.content.startswith('$loadwallet'):
        # Load the wallet using the wallet module
        bot_client.load_wallet()
        await message.channel.send('Wallet loaded!')

    elif message.content.startswith('!send'):
        # Send a transaction using the wallet module
        recipient, amount = message.content.split()[1:]
        bot_client.send_transaction(recipient, amount)
        await message.channel.send('Transaction sent!')


    elif message.content.startswith('!balance'):
        # Get the balance using the wallet module
        balance = bot_client.get_balance()
        await message.channel.send(f'Balance: {balance}')

# Run the client
client.run(config['token'])