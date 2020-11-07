import discord, random, asyncio
from discord.ext import commands
from classes.user import User
from classes.phrases import Phrases
phrases = Phrases()

class Balance(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Balance Cog loaded")

    @commands.command(aliases=['bal'])
    async def balance(self, ctx, user: discord.Member):
        color = discord.Color.red()

        user = await User(user.id)

        if user.inventory is None:
            if user.discord != ctx.author:
                return await ctx.send(phrases.otherNoInventory)
            else:
                return await ctx.send(phrases.noInventory)

        a = "their"
        if user.discord == ctx.author:
            color = discord.Color.blue()
            a = "your"

        embed = discord.Embed(
                title=":moneybag: **Balance**",
                description=":dollar: **{}**'s balance is $`{:,}`\n:bank: $`{:,}`/`{:,}` is stored in {} bank".format(user.discord.name, user.balance, user.bank.balance, user.bank.limit, a),
                color=color
            )
        return await ctx.send(embed=embed)

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            user = await User(ctx.author.id)
            embed = discord.Embed(
                title=":moneybag: **Balance**",
                description=":dollar: **{}**'s balance is $`{:,}`\n:bank: $`{:,}`/`{:,}` is stored in your bank".format(user.discord.name, user.balance, user.bank.balance, user.bank.limit),
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)


    @commands.command()
    async def pay(self, ctx, user: discord.Member, amount=None):
        user = await User(user.id)
        if user.inventory is None: return await ctx.send(phrases.otherNoInventory)
        author = await User(ctx.author.id)
        if author.inventory is None: return await ctx.send(phrases.noInventory)

        if user == ctx.author:
            return await ctx.send("That's pointless.")

        try:
            amount = int(amount)
            if amount <= 0:
                return await ctx.send("Please enter a valid quantity.\n**Tip:** Items in commands generally don't contain spaces!")
        except Exception:
            return await ctx.send(f"Enter a valid amount. Usage: `{self.bot.prefix}pay (user) (amount)`")

        if author.balance < amount:
            return await ctx.send(f"Insufficient funds, you only have $`{author_balance}`")

        author.balance -= amount
        user.balance += amount
        await ctx.send(f"Paid **{user.discord.name}** $`{amount}`")
        await user.update()
        await author.update()

    @pay.error
    async def pay_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}pay (user) (amount)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(phrases.userNotFound)

def setup(bot):
    bot.add_cog(Balance(bot))
