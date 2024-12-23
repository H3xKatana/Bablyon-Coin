import discord
from discord.ext import commands
import json
from bc import Wallet
from cmd_client import Client as CmdClient
import requests
# Load configuration from config.json
with open('config/bot_config.json') as f:
    config = json.load(f)

# Create a new bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='$', intents=intents)

# Initialize the command client
bot_client = CmdClient()

# Global variable to store the wallet object
wallet = None


# Event: Bot ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')



@bot.command(
    help="Checks the bot's responsiveness and displays latency in milliseconds.",
    description="Use this command to test if the bot is online and responsive.")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    bot_ip = requests.get('https://api.ipify.org').text
    print(bot_ip)
    embed = discord.Embed(title="IP Addresses", color=0x3498db)
    embed.add_field(name="Bot IP Address", value=bot_ip, inline=False)
    embed.add_field(name = f"Pong! Latency:", value=latency  )
    await ctx.send(embed=embed)



# Command: Bot Info
@bot.command(
    help="Displays detailed information about the bot and the blockchain it connects to.",
    description="Provides basic information about the bot and the Babylon Blockchain."
)
async def botinfo(ctx):
    """Display information about the bot."""
    embed = discord.Embed(
        title="Bot Information",
        description="This is a client implementation for the Babylon Blockchain.",
        color=0x3498db,
    )
    embed.set_author(name="0xkatana")
    embed.add_field(name="Blockchain Name", value="Babylon", inline=False)
    embed.add_field(name="Block Size", value="1MB", inline=True)
    embed.add_field(name="Block Time", value="10 minutes", inline=True)
    embed.add_field(name="Consensus Algorithm", value="Proof of Work", inline=True)
    await ctx.send(embed=embed)


# Command: Create Wallet
@bot.command(
    help="Creates a new blockchain wallet and returns wallet details.",
    description="Generates a new wallet for the Babylon Blockchain and provides its address."
)
async def createwallet(ctx):
    """Create a new wallet."""
    global wallet
    wallet = bot_client.create_wallet()
    wallet_info = f"Your Address: {wallet.get_address()}"
    
    embed = discord.Embed(
        title="Wallet Information",
        description=wallet_info,
        color=0x3498db,
    )
    embed.add_field(name="Creation Time", value=wallet.get_creation_time(), inline=False)

    if isinstance(ctx.channel, discord.TextChannel):
        thread = await ctx.channel.create_thread(
            name=f"Wallet Info - {ctx.author.name}",
            auto_archive_duration=60
        )
        await thread.send(embed=embed)
        await thread.send(file=discord.File("wallet.bc"))
    else:
        await ctx.send("Wallet created successfully")
        await ctx.send(embed=embed)
        await ctx.send(file=discord.File("wallet.bc"))


# Command: Load Wallet
@bot.command(
    help="Loads an existing wallet from an attached file.",
    description="Loads a Babylon Blockchain wallet from a .bc file."
)
async def loadwallet(ctx):
    """Load a wallet from a file."""
    global wallet

    if not ctx.message.attachments:
        await ctx.send('Please attach a wallet file to load.')
        return

    attachment = ctx.message.attachments[0]
    if attachment.filename.endswith('.bc'):
        await attachment.save(attachment.filename)
        with open(attachment.filename, 'r') as f:
            wallet_data = f.read()
    else:
        await ctx.send('Invalid wallet file format. Please attach a .bc file.')
        return

    wallet = bot_client.load_wallet(wallet_data)
    if wallet:
        await ctx.send('Wallet loaded successfully!')
        await ctx.send(f"Your Address: {wallet.get_address()}")
    else:
        await ctx.send('Wallet not found. Use $createwallet to create a new one.')


# Command: Wallet Info
@bot.command(
    help="Displays the current wallet's information.",
    description="Provides the address and creation time of the loaded or created wallet."
)
async def wallet_info(ctx):
    """Display the current wallet's information."""
    global wallet

    if wallet is None:
        await ctx.send('Wallet not created or loaded. Use $createwallet or $loadwallet.')
    else:
        await ctx.send(f"Your Address: {wallet.get_address()}")
        await ctx.send(f"Wallet Creation Time: {wallet.get_creation_time()}")


# Command: Send Transaction
@bot.command(
    help="Sends a specified amount to a recipient's address.",
    description="Executes a blockchain transaction to transfer funds to another wallet."
)
async def send(ctx, recipient: str, amount: float):
    """Send a transaction."""
    global wallet

    if wallet is None:
        await ctx.send('Wallet not created or loaded. Use $createwallet or $loadwallet.')
        return

    try:
        bot_client.send_transaction(wallet, recipient, amount)
        await ctx.send('Transaction sent successfully!')
    except ValueError:
        await ctx.send('Invalid command format. Use: $send <recipient> <amount>')


# Command: Check Balance
@bot.command(
    help="Checks the balance of the current wallet.",
    description="Retrieves and displays the balance of the loaded or created wallet."
)
async def balance(ctx):
    """Check the wallet's balance."""
    global wallet

    if wallet is None:
        await ctx.send('Wallet not created or loaded. Use $createwallet or $loadwallet.')
    else:
        balance = bot_client.get_balance(wallet)
        await ctx.send(f'Balance: {balance}')


# Run the bot

bot.run(config['token'])
