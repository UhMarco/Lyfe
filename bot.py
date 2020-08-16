import discord, json, platform, logging, os, time, motor.motor_asyncio
from discord.ext import commands
from pathlib import Path

import utils.json
from utils.mongo import Document

cwd = Path(__file__).parents[0]
cwd = str(cwd)

secret_file = json.load(open(cwd+"/bot_config/secrets.json"))
prefix = secret_file["prefix"]

bot = commands.Bot(command_prefix=prefix, case_insensitive=True, owner_id=259740408462966786)
bot.remove_command("help")

bot.config_token = secret_file["token"]
bot.connection_url = secret_file["mongo"]
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
    if status == "online":
        await bot.change_presence(activity=discord.Game(name=f"{bot.prefix}help in {len(bot.guilds)} servers"))
    elif status == "idle":
        await bot.change_presence(activity=discord.Game(name=f"{bot.prefix}help in {len(bot.guilds)} servers"), status=discord.Status.idle)
    elif status == "streaming":
        await bot.change_presence(activity=discord.Streaming(name=f"{bot.prefix}help", url="https://twitch.tv/discord"))

    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["lyfe"]
    if status == "online":
        bot.db = bot.mongo["lyfe"]
    elif status == "idle":
        bot.db = bot.mongo["lyfebeta"]
    else:
        bot.db = bot.mongo["lyfeaqua"]
    bot.inventories = Document(bot.db, "inventories")
    bot.items = Document(bot.db, "items")
    bot.trades = Document(bot.db, "trades")
    bot.playershops = Document(bot.db, "playershops")
    bot.cooldowns = Document(bot.db, "cooldowns")
    print("Initialized database\n-----")

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
    else:
        if message.author.id not in bot.whitelisted:
            return

    # Auto responses go here
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        try:
            if "help" in message.content.lower() or "info" in message.content.lower():
                await message.channel.send(f"My prefix is `{bot.prefix}`")
        except discord.Forbidden:
            pass

    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        imageURL = "https://images-ext-1.discordapp.net/external/rhRbquJhkxJMxDjv0uYMe6j0X9hoMJiFRROxJQMX1FA/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/730874220078170122/049bcf53fba266166c69b09e0f97dcab.webp?width=677&height=677"
        welcomebed = discord.Embed(
            title="Thank you for inviting me!",
            description=f"A few things about myself: \n \nMy prefix is `{self.bot.prefix}`\nYou can find help by doing `{self.bot.prefix}help`\nYou can join the support server by doing `{self.bot.prefix}invite`",
            color=discord.Color.green()
        )
        welcomebed.set_thumbnail(url=imageURL)
        return await ctx.send(embed=welcomebed)

if __name__ == '__main__':
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

bot.run(bot.config_token, reconnect=True)
