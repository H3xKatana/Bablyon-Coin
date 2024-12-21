import discord
from discord.ext import commands
import json
from bc import Wallet
from cmd_client import Client as cmd_client

# Load configuration from config.json
with open('config/bot_config.json') as f:
    config = json.load(f)

# Create a new bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='$', intents=intents)
bot_client = cmd_client()

# Global variable to store the wallet object
wallet = None


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(
        title="Bot Information",
        description="This is a client implementation for the Bablyon Blockchain",
        color=0x3498db,
    )
    embed.set_author(name="0xkatana")
    embed.add_field(name="Blockchain Name", value="Bablyon", inline=False)
    embed.add_field(name="Block Size", value="1MB", inline=True)
    embed.add_field(name="Block Time", value="10 minutes", inline=True)
    embed.add_field(name="Consensus Algorithm", value="Proof of Work", inline=True)
    await ctx.send(embed=embed)

# Command: createwallet
@bot.command()
async def createwallet(ctx):
    global wallet
    # Create a wallet using the wallet module
    wallet = bot_client.create_wallet()
    wallet_info = f"Wallet created!\nYour Address: {wallet.get_address()}"

    if isinstance(ctx.channel, discord.TextChannel):
        # Create a custom thread for the user
        thread = await ctx.channel.create_thread(
            name=f"Wallet Info - {ctx.author.name}",
            auto_archive_duration=60
        )
        await thread.send(wallet_info)
        await thread.send(file=discord.File("wallet.bc"))
    else:
        # Handle the case where the channel is not a guild channel
        await ctx.send(wallet_info)
        await ctx.send(file=discord.File("wallet.bc"))

# Command: loadwallet
@bot.command()
async def loadwallet(ctx):
    global wallet
    # Load the wallet using the wallet module
    if len(ctx.message.attachments) == 0:
        await ctx.send('Please attach a wallet file to load.')
        return
    
    attachment = ctx.message.attachments[0]
    if attachment.filename.endswith('.bc'):
        with open(attachment.filename, 'r') as f:
            wallet_data = f.read()
    else:
        await ctx.send('Please attach a wallet file to load.')
        return
    
    wallet = bot_client.load_wallet(wallet_data)
    if wallet is None:
        await ctx.send('Wallet not found. Use $createwallet to create a new one.')
    else:
        await ctx.send('Wallet loaded!')
        await ctx.send(f"Your Address: {wallet.get_address()}")

@bot.command()
async def wallet_info(ctx):
    global wallet
    # Display wallet information
    if wallet is None:
        await ctx.send('Wallet not created or loaded. Use $createwallet or $loadwallet.')
    else:
        
        await ctx.send(f"Your Address: {wallet.get_address()}")
        await ctx.send(f"Wallet loaded at : {wallet.get_creation_time()}")

# Command: send
@bot.command()
async def send(ctx, recipient, amount):
    global wallet
    # Send a transaction using the wallet module
    try:
        if wallet is None:
            await ctx.send('Wallet not created or loaded. Use $createwallet or $loadwallet.')
        else:
            bot_client.send_transaction(wallet, recipient, amount)
            await ctx.send('Transaction sent!')
    except ValueError:
        await ctx.send('Invalid command format. Use: $send <recipient> <amount>')

# Command: balance
@bot.command()
async def balance(ctx):
    global wallet
    # Get the balance using the wallet module
    if wallet is None:
        await ctx.send('Wallet not created or loaded. Use $createwallet or $loadwallet.')
    else:
        balance = bot_client.get_balance(wallet)
        await ctx.send(f'Balance: {balance}')

# Event: on_ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Run the bot
bot.run(config['token'])
