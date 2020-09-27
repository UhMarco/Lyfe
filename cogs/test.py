import discord, platform, logging, random, os, time, asyncio
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json, utils.functions
from tabulate import tabulate

from classes.user import User

class Test(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ TEST Cog loaded")

    @commands.command()
    async def owns(self, ctx, user, item):
        user = await User(await utils.functions.getUser(user))
        if user is None:
            return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")

        item = await utils.functions.getItem(item)
        if item is None:
            return await ctx.send("Item does not exist.")

        if await user.hasItem(item):
            await ctx.send("True")
        else:
            await ctx.send("False")

def setup(bot):
    bot.add_cog(Test(bot))
