import discord, json, platform, logging, os, time, motor.motor_asyncio
from discord.ext import commands
from pathlib import Path

import utils.json
from utils.mongo import Document

cwd = Path(__file__).parents[0]
cwd = str(cwd)

secret_file = json.load(open(cwd+"/bot_config/secrets.json"))
prefix = secret_file["prefix"]

bot = commands.Bot(command_prefix=prefix, case_insensitive=True, owner_id=259740408462966786, intents=discord.Intents.all())
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
        ctx = await bot.get_context(message)
        if ctx.valid:
            if message.content.lower().find("invite") != -1:
                embed = discord.Embed(title=":herb: Lyfé Invite Links", description=":mailbox_with_mail: [Invite me to other servers](https://discord.com/api/oauth2/authorize?client_id=730874220078170122&permissions=519232&scope=bot)\n<:discord:733776804904697886> [Lyfé Server](https://discord.gg/zAZ3vKJ)", color=discord.Color.purple())
                return await ctx.send(embed=embed)
            else:
                lockdownembed = discord.Embed(
                    title="Lyfe is currently in a lockdown",
                    description=f"At the moment, commands will not work due to an error we have encountered.\nPlease join our support server by doing `{bot.prefix}invite` for more info.",
                    color=discord.Color.red()
                )
                lockdownembed.set_thumbnail(url=bot.user.avatar_url)
                return await ctx.send(embed=lockdownembed)

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

if __name__ == '__main__':
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

bot.run(bot.config_token, reconnect=True)
