import discord, json, platform, logging, os, time, motor.motor_asyncio
from discord.ext import commands
from pathlib import Path

import utils.json, utils.functions, classes.user, classes.inventory
from utils.mongo import Document

cwd = Path(__file__).parents[0]
cwd = str(cwd)

# Opens secrets.json which contains all sensitive information as it was put in .gitignore
secret_file = json.load(open(cwd+"/bot_config/secrets.json"))
prefix = secret_file["prefix"]

bot = commands.Bot(command_prefix=prefix, case_insensitive=True, owner_id=259740408462966786) # <--- Put your id there

# Un-comment this when adding a help command.
# bot.remove_command("help")

# Mongo database connection variables
bot.config_token = secret_file["token"]
bot.connection_url = secret_file["mongo"]

# Variables stored in the bot object (attributes) so they can be accessed anywhere the bot object is.
bot.prefix = prefix
bot.blacklisted_users = []
bot.upsince = time.time()
bot.maintenancemode = False
bot.whitelisted = []
bot.lockdown = False

bot.errors = 0
bot.important_errors = 0

@bot.event
async def on_ready():
    print(f"-----\n{bot.user.name} Online\n-----\nPrefix: {bot.prefix}\n-----")

    status = secret_file["status"]
    # Bot sets its status depending on it's state
    if status == "online":
        await bot.change_presence(activity=discord.Game(name=f"{bot.prefix}help in {len(bot.guilds)} servers"))
    elif status == "idle":
        await bot.change_presence(activity=discord.Game(name=f"{bot.prefix}help in {len(bot.guilds)} servers"), status=discord.Status.idle)
    elif status == "streaming":
        await bot.change_presence(activity=discord.Streaming(name=f"{bot.prefix}help", url="https://twitch.tv/discord"))

    # Database connection
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["lyfe"]
    if status == "online":
        bot.db = bot.mongo["lyfe"]
    elif status == "idle":
        bot.db = bot.mongo["lyfebeta"]
    else:
        bot.db = bot.mongo["lyfeaqua"]

    # Imports all the functions for the database
    bot.inventories = Document(bot.db, "inventories")
    bot.items = Document(bot.db, "items")
    bot.trades = Document(bot.db, "trades")
    bot.playershops = Document(bot.db, "playershops")
    bot.cooldowns = Document(bot.db, "cooldowns")
    print("Initialized database\n-----")

    # Spreads the bot object into other files that require it
    utils.functions.bot = classes.user.bot = classes.inventory.bot = bot

@bot.event
async def on_message(message):
    # Ignore bots
    if message.author.id == bot.user.id or message.author.bot:
        return

    # Lockdown system
    if bot.lockdown and message.author.id not in json.load(open(cwd+"/bot_config/devs.json")):
        return

    # Blacklist system
    if secret_file["status"] != "idle":
        if message.author.id in bot.blacklisted_users:
            return
    else: # Whitelist system (for test bots)
        if message.author.id not in bot.whitelisted:
            return

    # Respond when tagged
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        try:
            if "help" in message.content.lower() or "info" in message.content.lower():
                await message.channel.send(f"My prefix is `{bot.prefix}`")
        except discord.Forbidden:
            pass

    # Still need to pass the message on to command handler
    await bot.process_commands(message)

# Load cogs
if __name__ == '__main__':
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

# You can guess what this does
bot.run(bot.config_token, reconnect=True)
