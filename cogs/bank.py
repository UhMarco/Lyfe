import discord, random, asyncio
from discord.ext import commands
from classes.user import User
from tabulate import tabulate
from classes.phrases import Phrases
phrases = Phrases()

def makeCapital(string: str):
    return f"{string[:1].upper()}{string[1:]}"

class Bank(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Bank Cog loaded")

    @commands.command(aliases=['bank'])
    async def banks(self, ctx, *, bank=None):
        author = await User(ctx.author.id)
        if author.inventory is None: return await ctx.send(phrases.noInventory)

        price = {"small": 1250, "medium": 2500, "large": 5000, "massive": 10000}
        limit = {"small": 2500, "medium":7500 , "large": 20000, "massive": 50000}

        if bank is None: # Bank shop
            entries = []
            for i in price:
                entries.append([f"{makeCapital(i)} Bank Slot", "${:,}".format(limit[i]), f"{self.bot.prefix}bank {i} bank slot"])
            output = ("Protect your money from thieves\n```" + tabulate(entries, tablefmt="simple", headers=["Item", "Cost", "Stores", "Command"]) + "```")
            embed = discord.Embed(title=":bank: Banks:", description=output, color=discord.Color.gold())
            await ctx.send(embed=embed)

        else: # Buy a bank
            bank = bank.replace(" ", "").lower()
            for name in price.keys():
                if name in bank: bank = name

            if bank not in price.keys(): return await ctx.send("Bank not found.")

            if price[bank] > author.balance:
                return await ctx.send("$`{:,}` is required to purchase this. You only have $`{:,}` and need another $`{:,}` to afford this.".format(price[bank], author.balance, price[bank] - author.balance))

            author.bank.limit += limit[bank]
            author.balance -= price[bank]
            await author.update()
            embed = discord.Embed(
                title=f"Purchase Successful",
                description="Purchased: :bank: **Small Bank Slot**\nMoney spent: $`{:,}`\nNew balance: $`{:,}`".format(price[bank], author.balance),
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)


    @commands.command(aliases=['dep'])
    async def deposit(self, ctx, amount):
        author = await User(ctx.author.id)
        if author.inventory is None: await ctx.send(phrases.noInventory)

        if author.bank.limit == 0:
            return await ctx.send(f"You don't have a **:bank: Bank**. Do `{self.bot.prefix}banks`.")

        if amount == "all":
            amount = author.balance
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send("Enter an amount greater than $`0` to deposit.")

            if amount <= 0:
                return await ctx.send("Enter an amount greater than $`0` to deposit.")
            elif amount > author.balance:
                return await ctx.send("Insufficient funds. You only have $`{:,}` available to deposit.".format(author.balance))

        if amount + author.bank.balance > author.bank.limit:
            return await ctx.send("This would put your bank balance over $`{:,}` which is your limit. Increase this limit by purchasing a larger bank slot at `{}banks`.".format(author.bank.limit, self.bot.prefix))

        author.balance -= amount
        author.bank.balance += amount
        await author.update()
        embed = discord.Embed(title=":bank: Deposit Successful",
            description="$`{:,}` has been deposited\nBank balance: $`{:,}`/`{:,}`\nBalance: $`{:,}`".format(amount, author.bank.balance, author.bank.limit, author.balance),
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @deposit.error
    async def deposit_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}deposit (amount)`")


    @commands.command()
    async def withdraw(self, ctx, amount):
        author = await User(ctx.author.id)
        if author.inventory is None: return await ctx.send("You haven't initialized your inventory yet.")

        if author.bank.limit == 0:
            return await ctx.send(f"You don't have a **:bank: Bank**. Do `{self.bot.prefix}banks`.")

        if amount == "all":
            amount = author.bank.balance
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send("Enter an amount greater than $`0` to withdraw.")
            if amount <= 0:
                return await ctx.send("Enter an amount greater than $`0` to withdraw.")
            elif amount > author.bank.balance or author.bank.balance == 0:
                return await ctx.send("Insufficient funds. You only have $`{:,}` stored in your bank.".format(author.bank.balance))

        author.bank.balance -= amount
        author.balance += amount
        await author.update()
        embed = discord.Embed(
            title=":bank: Withdrawal Successful",
            description="$`{:,}` has been withdrawn\nBank balance: $`{:,}`/`{:,}`\nBalance: $`{:,}`".format(amount, author.bank.balance, author.bank.limit, author.balance),
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @withdraw.error
    async def withdraw_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}withdraw (amount)`")

def setup(bot):
    bot.add_cog(Bank(bot))
