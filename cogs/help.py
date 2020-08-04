import discord, platform, logging, random, os, asyncio
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate
from datetime import datetime

class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Help Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- ITEM LIST ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['commands'])
    async def help(self, ctx, section=None):
        if section is None:
            pass

        elif section.lower() == "inventory":
            embed = discord.Embed(title=":page_facing_up: Inventory Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Inventory command list")
            embed.add_field(name=f"`{self.bot.prefix}inv [page]/[user] [page]`", value="Open your inventory", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}claim`", value="Claim your hourly reward", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}daily`", value="Claim your daily reward", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}lock (item)`", value="Prevent an item from being traded or stolen, requires :lock: Lock", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}unlock (item)`", value="Allow an item to be traded or stolen, requires :key: Key", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "economy":
            embed = discord.Embed(title=":credit_card: Economy Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Economy command list")
            embed.add_field(name=f"`{self.bot.prefix}balance [user]`", value="View yours or someone else's balance", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}gamble`", value="Spend your money responsibly", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}shop`", value="Open the shop", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}buy`", value="Buy an item from the shop", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}sell`", value="Sell any item for 75% of its value to the shop", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}give (user) (item)`", value="Give someone an item", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pay (user) (amount)`", value="Pay someone money", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop`", value="Lists all the Player Shops", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop show (user)`", value="See a user's shop", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop buy (user) (item)`", value="Buys a user's item", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop add (item) (price) [quantity]`", value="Adds an item from your inventory to your shop. Default quantity : `1`", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop remove (item) [quantity]`", value="Removes a certain item from your shop. Default quantity : `1`", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}banks`", value="Shows all banks", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}bank (bank slot)`", value="Purchase a bank slot", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}deposit (amount)`", value="Deposit into your bank", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}withdraw (amoint)`", value="Withdraw from your bank", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "crime" or section.lower() == "robbery":
            embed = discord.Embed(title=":moneybag: Crime Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Crime command list")
            embed.add_field(name=f"`{self.bot.prefix}rob (user) (tool) (desired item)`", value="Rob another player of an item, requires a tool, leave blank to see owned tools", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}steal (user) (amount)`", value="Rob another player of money, requires a :gun: Gun, min=500 max=7500", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}dynamite (user)`", value="Blow up 20% of someone's balance, requires :firecracker: Dynamite", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}bomb (user)`", value="Blow up 10% of someone's bank balance, requires :bomb: Bomb", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}burn (user) (item)`", value="Burn another user's item, requires :fire: Fire", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}axe (user)`", value="Unlock another player's item, requires :axe: Axe", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "jobs":
            embed = discord.Embed(title=":card_box: Job Commands", color=discord.Color.purple())
            embed.set_footer(text="Job command list")
            embed.add_field(name=f"`{self.bot.prefix}jobs`", value="Shows the list of jobs", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}apply (job)`", value="You can apply for work here", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}work`", value="Do your job!", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}resign`", value="Promoting yourself to customer", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}beg`", value="Beg for money", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "trading":
            embed = discord.Embed(title=":scales: Trading Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Trading command list")
            embed.add_field(name=f"`{self.bot.prefix}trade (user) (owned item) (desired item)`", value="Offer to trade with another player", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}taccept (tradeid)`", value="Accepts a trade offer", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}tcancel (tradeid)`", value="Cancel a trade offer", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}give (user) (item) [quantity]`", value="Give an item to another player", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "research":
            embed = discord.Embed(title=":microscope: Research Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Research command list")
            embed.add_field(name=f"`{self.bot.prefix}iteminfo (item)`", value="Get information about an item", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}find (item)`", value="Find 5 random users and their IDs who own an item", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "misc":
            embed = discord.Embed(title=":game_die: Misc Commands", color=discord.Color.purple())
            embed.set_footer(text="Misc command list")
            embed.add_field(name=f"`{self.bot.prefix}feed`", value="Feed a frog to a dragon, there's a 1% chance of something special happening", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}avatar [user]`", value="Display the avatar of a user in full size", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}8ball (question)`", value="8ball lol", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "leaderboards" or section.lower() == "leaders":
            embed = discord.Embed(title=":medal: Leaderboards", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Leaderboards command list")
            embed.add_field(name=f"`{self.bot.prefix}leaderboard`", value="Show the top 10 players with the highest total value", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}baltop`", value="Show the top 10 total balances", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}frogtop`", value="Show the top 5 frog owners", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "bot":
            embed = discord.Embed(title=":robot: Bot", color=discord.Color.purple())
            embed.set_footer(text="Bot command list")
            embed.add_field(name=f"`{self.bot.prefix}info`", value="See bot info", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}diagnose`", value="See which modules are online and check for errors", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}ping`", value="Pong!", inline=False)
            return await ctx.send(embed=embed)

        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            embed = discord.Embed(title=":herb: Lyfé Command List", description=f"**Hey!** Initialize your inventory with `{self.bot.prefix}inv`", color=discord.Color.purple())
        else:
            embed = discord.Embed(title=":herb: Lyfé Command List", color=discord.Color.purple())
            embed.add_field(name=":page_facing_up: Inventory", value=f"`{self.bot.prefix}help inventory`", inline=False)
            embed.add_field(name=":credit_card: Economy", value=f"`{self.bot.prefix}help economy`", inline=False)
            embed.add_field(name=":moneybag: Crime", value=f"`{self.bot.prefix}help crime`", inline=False)
            embed.add_field(name=":card_box: Jobs", value=f"`{self.bot.prefix}help jobs`", inline=False)
            embed.add_field(name=":scales: Trading", value=f"`{self.bot.prefix}help trading`", inline=False)
            embed.add_field(name=":microscope: Research", value=f"`{self.bot.prefix}help research`", inline=False)
            embed.add_field(name=":game_die: Misc", value=f"`{self.bot.prefix}help misc`", inline=False)
            embed.add_field(name=":medal: Leaderboards", value=f"`{self.bot.prefix}help leaderboards`", inline=False)
            embed.add_field(name=":robot: Bot", value=f"`{self.bot.prefix}help bot`", inline=False)
        return await ctx.send(embed=embed)

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- INVITE -------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(title=":herb: Lyfé Invite Links", description=":mailbox_with_mail: [Invite me to other servers](https://discord.com/api/oauth2/authorize?client_id=730874220078170122&permissions=519232&scope=bot)\n<:discord:733776804904697886> [Lyfé Server](https://discord.gg/zAZ3vKJ)", color=discord.Color.purple())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
