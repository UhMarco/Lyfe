import discord, platform, logging, random, os, asyncio, time
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate
from datetime import datetime

class Bot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Bot Cog loaded")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)} ms")

    @commands.command(aliases=['diagnosis'])
    async def diagnose(self, ctx):
        modules = []
        items = []
        message = "\n"
        count = 0
        icount = 0

        for file in os.listdir(cwd+"/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                done = False
                try:
                    self.bot.load_extension(f"cogs.{file[:-3]}")
                    self.bot.unload_extension(f"cogs.{file[:-3]}")
                except commands.ExtensionAlreadyLoaded:
                    name = file[:-3]
                    name = f"`✔ {name[:1].upper()}{name[1:]}`"
                    modules.append(name)
                    count += 1
                    done = True

                if not done:
                    name = file[:-3]
                    name = f"`✘ {name[:1].upper()}{name[1:]}`"
                    modules.append(name)

                if not done:
                    name = file[:-3]
                    name = f"`✘ {name[:1].upper()}{name[1:]}`"
                    items.append(name)

        embed = discord.Embed(title="Diagnosis", description=f"**Extensions:**\n{message.join(modules)}\n**Errors since startup:** `{self.bot.important_errors}/{self.bot.errors}`", color=discord.Color.blue())
        await ctx.send(embed=embed)
    @commands.command(aliases=['stats'])
    async def info(self,ctx):
        m, s = divmod(time.time() - self.bot.upsince, 60)
        h, m = divmod(m, 60)
        if int(h) == 0 and int(m) == 0:
            uptime = f"{int(s)} seconds"
        elif int(h) == 0 and int(m) != 0:
            uptime = f"{int(m)} minutes and {int(s)} seconds"
        else:
            uptime = f"{int(h)} hours, {int(m)} minutes and {int(s)} seconds"
        embed = discord.Embed(
            title=":robot: Bot Info",
            description=f"""
                Uptime: `{uptime}`
                Running: `python {platform.python_version()}`, `d.py {discord.__version__}`
                Servers: `{len(self.bot.guilds)}`
                Invite: `{self.bot.prefix}invite`
                """,
            color=discord.Color.purple()
        )
        embed.set_footer(text="Built by NotStealthy#0001, Spook#4177 and hypews#0001")
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Bot(bot))
