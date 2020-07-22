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
            embed = discord.Embed(title=":page_facing_up: Basic Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Basic command list")
            embed.add_field(name=f"`{self.bot.prefix}inv [user] [page]`", value="Open your inventory", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}bal [user]`", value="See your own or another's balance", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}baltop`", value="See the balance leaderboards", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}iteminfo (item)`", value=f"Look up information about an item", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}claim`", value="Claim your hourly reward", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}daily`", value="Claim your daily reward", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "shop":
            embed = discord.Embed(title=":shopping_cart: Shop Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Shop command list")
            embed.add_field(name=f"`{self.bot.prefix}shop`", value="Shows the shop", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}buy (item) [quantity]`", value="Buy something from the shop", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}sell (item) [quantity]`", value="Sell any item for 75% of its value to the shop", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "banks" or section.lower() == "banking":
            embed = discord.Embed(title=":bank: Banking Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Banks command list")
            embed.add_field(name=f"`{self.bot.prefix}banks`", value="Shows all banks", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}bank (bank slot)`", value="Purchase a bank slot", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "jobs":
            embed = discord.Embed(title=":card_box: Job Commands", color=discord.Color.purple())
            embed.set_footer(text="Job command list")
            embed.add_field(name=f"`{self.bot.prefix}jobs`", value="Shows the list of jobs", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}apply (job)`", value="You can apply for work here", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}resign`", value="Promoting yourself to customer", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}work`", value="Do your job!", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "trading":
            embed = discord.Embed(title=":scales: Trading Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Trading command list")
            embed.add_field(name=f"`{self.bot.prefix}trade (user) (owned item) (desired item)`", value="Offer to trade with another player", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}taccept (tradeid)`", value="Accepts a trade offer", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}tcancel (tradeid)`", value="Cancel a trade offer", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}give (user) (item) [quantity]`", value="Give an item to another player", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "robbery":
            embed = discord.Embed(title=":moneybag: Robbery Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Robbery command list")
            embed.add_field(name=f"`{self.bot.prefix}rob (user) (tool) (desired item)`", value="Rob another player of an item, requires a tool, leave blank to see owned tools", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}steal (user) (amount)`", value="Rob another player of money, requires a :gun: Gun, min=500 max=5000", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}dynamite (user)`", value="Blow up 20% of someone's balance, requires :firecracker: Dynamite", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}lock (item)`", value="Prevent an item from being traded or stolen, requires :lock: Lock", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}unlock (item)`", value="Allow an item to be traded or stolen, requires :key: Key", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "misc":
            embed = discord.Embed(title=":game_die: Misc Commands", color=discord.Color.purple())
            embed.set_footer(text="Misc command list")
            embed.add_field(name=f"`{self.bot.prefix}gamble`", value="See ways of spending money sensibly", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}feed`", value="Feed a frog to a dragon, there's a 1% chance of something special happening", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}find (item)`", value="Find 5 random users and their IDs who own an item", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}frogtop`", value="See who has the most frogs", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}avatar [user]`", value="Display the avatar of a user in full size", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}8ball (question)`", value="8ball lol", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "pshop" or section.lower() == "pshops":
            embed = discord.Embed(title=":credit_card: Player Shops", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            embed.set_footer(text="Player Shops command list")
            embed.add_field(name=f"`{self.bot.prefix}pshop`", value="Lists all the Player Shops", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop shoew (user)`", value="See a user's shop", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop buy (user) (item)`", value="Buys a user's item", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop add (item) (price) [quantity]`", value="Adds an item from your inventory to your shop. Default quantity : `1`", inline=False)
            embed.add_field(name=f"`{self.bot.prefix}pshop remove (item) [quantity]`", value="Removes a certain item from your shop. Default quantity : `1`", inline=False)
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
                            :mailbox_with_mail: [Bot Invite](https://discord.com/api/oauth2/authorize?client_id=730874220078170122&permissions=519232&scope=bot)
                            <:discord:733776804904697886> [Lyfé Server](https://discord.gg/zAZ3vKJ)
                            """,
                color=discord.Color.purple()
            )
            embed.set_footer(text="Built by NotStealthy#0001, Spook#4177 and hypews#2401")
            return await ctx.send(embed=embed)

        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            embed = discord.Embed(title=":herb: Lyfé Command List", description=f"**Hey!** Initialize your inventory with `{self.bot.prefix}inv`", color=discord.Color.purple())
        else:
            embed = discord.Embed(title=":herb: Lyfé Command List", color=discord.Color.purple())
            embed.add_field(name=":page_facing_up: Basic", value=f"`{self.bot.prefix}help basic`", inline=False)
            embed.add_field(name=":shopping_cart: Shop", value=f"`{self.bot.prefix}help shop`", inline=False)
            embed.add_field(name=":bank: Banks", value=f"`{self.bot.prefix}help banks`", inline=False)
            embed.add_field(name=":card_box: Jobs", value=f"`{self.bot.prefix}help jobs`", inline=False)
            embed.add_field(name=":scales: Trading", value=f"`{self.bot.prefix}help trading`", inline=False)
            embed.add_field(name=":moneybag: Robbery", value=f"`{self.bot.prefix}help robbery`", inline=False)
            embed.add_field(name=":game_die: Misc", value=f"`{self.bot.prefix}help misc`", inline=False)
            embed.add_field(name=":credit_card: Player Shops", value=f"`{self.bot.prefix}help pshop`", inline=False)
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
