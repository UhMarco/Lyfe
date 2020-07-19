import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Banking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Banking Cog loaded")

    @commands.command(aliases=['bank'])
    async def banks(self, ctx, *, item="n"):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        inventory = data["inventory"]
        bal = data["balance"]
        banklimit = data["banklimit"]

        item = item.replace(" ", "").lower()
        if item == "smallbankslot" or item == "smallbank":
            cost = 150
            if banklimit != 0:
                return await ctx.send("A bank slot of greater or equal value has already been purchased.")

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost
            banklimit = 500
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "banklimit": banklimit})
            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: :bank: **Small Bank Slot**\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)

        elif item == "mediumbankslot" or item == "mediumbank":
            cost = 300
            if banklimit > 500:
                return await ctx.send("A bank slot of greater or equal value has already been purchased.")

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost
            banklimit = 1000
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "banklimit": banklimit})
            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: :bank: **Medium Bank Slot**\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)

        elif item == "largebankslot" or item == "largebank":
            cost = 2500
            if banklimit > 1000:
                return await ctx.send("A bank slot of greater or equal value has already been purchased.")

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost
            banklimit = 10000
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "banklimit": banklimit})
            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: :bank: **Large Bank Slot**\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title=":bank: Banks", description="Protects your money from theives", color=discord.Color.gold())
            embed.add_field(name=":bank: Small Bank Slot", value=f"Store $`500` in the bank.\nCosts $`150`\n`{self.bot.prefix}bank small bank slot`", inline=False)
            embed.add_field(name=":bank: Medium Bank Slot", value=f"Store $`1000` in the bank.\nCosts $`300`\n`{self.bot.prefix}bank medium bank slot`", inline=False)
            embed.add_field(name=":bank: Large Bank Slot", value=f"Store $`10000` in the bank.\nCosts $`2500`\n`{self.bot.prefix}bank large bank slot`", inline=False)
            await ctx.send(embed=embed)



    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- DEPOSIT ------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['dep'])
    async def deposit(self, ctx, amount="null"):
        try:
            amount = int(amount)
        except Exception:
            amount.lower()
            if amount == "all":
                pass
            else:
                return await ctx.send(f"Usage: `{self.bot.prefix}deposit (amount)`")

        data = await self.bot.inventories.find(ctx.author.id)

        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        balance = data["balance"]
        bankbalance = data["bankbalance"]
        banklimit = data["banklimit"]
        if amount == "all":
            amount = int(balance)

        if banklimit == 0:
            return await ctx.send(f"A **:bank: Bank Slot** hasn't been bought yet. Do `{self.bot.prefix}banks`.")

        if bankbalance == banklimit:
            return await ctx.send(f"Your bank balance is full with $`{bankbalance}`. Purchase a larger bank slot at `{self.bot.prefix}banks`.")

        if balance == 0:
            return await ctx.send("Your balance is empty.")

        if amount + bankbalance > banklimit:
            return await ctx.send(f"This would put your bank balance over $`{banklimit}` which is your limit. Increase this limit by purchasing a larger bank slot at `{self.bot.prefix}banks`.")

        if amount > balance:
            return await ctx.send(f"You only have $`{balance}` available to deposit.")

        balance -= amount
        bankbalance += amount
        await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})
        await self.bot.inventories.upsert({"_id": ctx.author.id, "bankbalance": bankbalance})
        embed = discord.Embed(title=":bank: Deposit Successful", description=f"$`{amount}` has been deposited\nBank balance: $`{bankbalance}`/`{banklimit}`\nBalance: $`{balance}`", color=discord.Color.gold())
        await ctx.send(embed=embed)

    # ----- ERROR HANDLER ------------------------------------------------------

    @deposit.error
    async def deposit_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}deposit (amount)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- WITHDRAW -----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def withdraw(self, ctx, amount="null"):
        try:
            amount = int(amount)
        except Exception:
            amount.lower()
            if amount == "all":
                pass
            else:
                return await ctx.send(f"Usage: `{self.bot.prefix}withdraw (amount)`")

        data = await self.bot.inventories.find(ctx.author.id)

        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        balance = data["balance"]
        bankbalance = data["bankbalance"]
        banklimit = data["banklimit"]
        if amount == "all":
            amount = int(bankbalance)

        if banklimit == 0:
            return await ctx.send(f"A **:bank: Bank Slot** hasn't been bought yet. Do `{self.bot.prefix}banks`.")

        if amount > bankbalance:
            return await ctx.send(f"Insufficient funds. You only have $`{bankbalance}` stored in your bank.")

        bankbalance -= amount
        balance += amount
        await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})
        await self.bot.inventories.upsert({"_id": ctx.author.id, "bankbalance": bankbalance})
        embed = discord.Embed(title=":bank: Withdrawal Successful", description=f"$`{amount}` has been withdrawn\nBank balance: $`{bankbalance}`/`{banklimit}`\nBalance: $`{balance}`", color=discord.Color.gold())
        await ctx.send(embed=embed)

    # ----- ERROR HANDLER ------------------------------------------------------

    @withdraw.error
    async def withdraw_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}withdraw (amount)`")



def setup(bot):
    bot.add_cog(Banking(bot))
