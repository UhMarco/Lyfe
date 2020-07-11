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

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- DEPOSIT ------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def deposit(self, ctx, amount="null"):
        try:
            amount = int(amount)
        except Exception:
            return await ctx.send(f"Usage: `{self.bot.prefix}deposit (amount)`")

        data = await self.bot.inventories.find(ctx.author.id)

        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        balance = data["balance"]
        bankbalance = data["bankbalance"]
        banklimit = data["banklimit"]

        if banklimit == 0:
            return await ctx.send(f"A **:bank: Bank Slot** hasn't been bought yet. Do `{self.bot.prefix}shop`.")

        if bankbalance == banklimit:
            return await ctx.send(f"Your bank balance is full with $`{bankbalance}`. Purchase a larger bank slot at `{self.bot.prefix}shop`.")

        if balance == 0:
            return await ctx.send("Your balance is empty.")

        if amount + bankbalance > banklimit:
            return await ctx.send(f"This would put your bank balance over $`{banklimit}` which is your limit. Increase this limit by purchasing a larger bank slot at `{self.bot.prefix}shop`.")

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
            return await ctx.send(f"Usage: `{self.bot.prefix}withdraw (amount)`")

        data = await self.bot.inventories.find(ctx.author.id)

        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        balance = data["balance"]
        bankbalance = data["bankbalance"]
        banklimit = data["banklimit"]

        if banklimit == 0:
            return await ctx.send(f"A **:bank: Bank Slot** hasn't been bought yet. Do `{self.bot.prefix}shop`.")

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
