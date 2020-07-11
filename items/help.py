import discord, platform, datetime, logging, time
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

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

    @commands.command()
    async def help(self, ctx, section=None):
        if section is None:
            pass

        elif section.lower() == "basic":
            embed = discord.Embed(title=":page_facing_up: Basic Commands", description="**Note:** Items in commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="basic command list")
            embed.add_field(name=f"`{self.bot.prefix}inv [page]`", value="Open your inventory", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}bal [user]`", value="See your own or another's balance", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}invsee (user) [page]`", value="See other people's Inventories", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}iteminfo (item)`", value=f"Look up information about an item", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}claim`", value="Claim your hourly reward", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "shop":
            embed = discord.Embed(title=":shopping_cart: Shop Commands", description="**Note:** Items in commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="shop command list")
            embed.add_field(name=f"`{self.bot.prefix}shop`", value="Shows the shop", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}buy (item)`", value="Buy something from the shop, you can have spaces!", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}sell (item)`", value="Sell any item for its value to the shop", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "trading":
            embed = discord.Embed(title=":scales: Trading Commands", description="**Note:** Items in commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="trading command list")
            embed.add_field(name=f"`{self.bot.prefix}trade (user) (owned item) (desired item)`", value="Offer to trade with another player", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}taccept (tradeid)`", value="Accepts a trade offer", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}tcancel (tradeid)`", value="Cancel a trade offer", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}give (user) (item)`", value="Give an item to another player", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "robbery":
            embed = discord.Embed(title=":moneybag: Robbery Commands", description="**Note:** Items in commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="robbery command list")
            embed.add_field(name=f"`{self.bot.prefix}rob (user) (tool) (desired item)`", value="Rob another player of an item, requires a tool, leave blank to see owned tools", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}lock (item)`", value="Prevent an item from being traded or stolen, requires :lock: Lock", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}unlock (item)`", value="Allow an item to be traded or stolen, requires :key: Key", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "bot":
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
                            I need a head of marketing for a description lol
                            Lyfé is a discord bot to bring some fun to your server with a unique inventory system and interactions with others\n
                            Uptime: `{uptime}`
                            Running: `python {platform.python_version()}`, `dpy {discord.__version__}`
                            Servers: `{len(self.bot.guilds)}`\n
                            <:github:731220198539133040> [Github](https://github.com/UhMarco)
                            <:trello:731219464758231080> [Trello](https://trello.com/b/vY8Vx2PW/lyfe-bot)
                            :mailbox_with_mail: [Invite](https://discord.com/api/oauth2/authorize?client_id=730874220078170122&permissions=519232&scope=bot)
                            """,
                color=discord.Color.purple()
            )
            embed.set_footer(text="built by NotStealthy#0001")
            return await ctx.send(embed=embed)

        embed = discord.Embed(title=":herb: Lyfé Command List", color=discord.Color.purple())
        embed.add_field(name=":page_facing_up: Basic", value=f"`{self.bot.prefix}help basic`", inline=False)
        embed.add_field(name=":shopping_cart: Shop", value=f"`{self.bot.prefix}help shop`", inline=False)
        embed.add_field(name=":scales: Trading", value=f"`{self.bot.prefix}help trading`", inline=False)
        embed.add_field(name=":moneybag: Robbery", value=f"`{self.bot.prefix}help robbery`", inline=False)
        embed.add_field(name=":robot: Bot", value=f"`{self.bot.prefix}help bot`", inline=False)
        return await ctx.send(embed=embed)

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- INVITE -------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(description=":mailbox_with_mail: [Invite me to other servers](https://discord.com/api/oauth2/authorize?client_id=730874220078170122&permissions=519232&scope=bot)", color=discord.Color.purple())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
