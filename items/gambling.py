import discord, platform, datetime, logging, random, asyncio
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Gambling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Gambling Cog loaded")

    @commands.command(aliases=['gambling'])
    async def gamble(self, ctx, game=None, amount="n"):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        inventory = data["inventory"]
        balance = data["balance"]
        items = await self.bot.items.find("items")
        items = items["items"]

        if game is None:
            embed = discord.Embed(title=":game_die: **Gambling**", description="Spend your money sensibly by doing some gambling!", color=discord.Color.dark_teal())
            embed.add_field(name=":package: Three Boxes", value=f"Choose a prize from 3 mystery boxes! Costs $`750`\n`{self.bot.prefix}gamble boxes`", inline=False)
            embed.add_field(name=":question: Number Guesser", value=f"Guess the correct number to triple however much you enter\n`{self.bot.prefix}gamble number (amount)`", inline=False)
            embed.add_field(name="<:coin:733930163817152565> Coin Flip", value=f"50% chance of doubling your money, 50% chance of losing double! You win on heads\n`{self.bot.prefix}gamble coinflip (amount)`", inline=False)
            return await ctx.send(embed=embed)

        elif game.replace(" ", "").lower() == "threeboxes" or game.replace(" ", "").lower() == "boxes":
            if balance < 750:
                return await ctx.send("Insufficient funds.")
            balance -= 750
            await ctx.send("$`750` has been taken from your account\n**Three Boxes:**")
            await ctx.send(":package: :package: :package:")
            await ctx.send("**   1^             2^            3^**\nChoose a box:")

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author
            numbers = ['1', '2', '3']
            while True:
                try:
                    message = await self.bot.wait_for('message', check=check, timeout=10)
                except asyncio.TimeoutError:
                    return await ctx.send("You ran out of time! Refunding $`750`")

                if any(ele in message.content for ele in numbers):
                    break
                else:
                    await ctx.send("Please enter 1, 2 or 3.")


            randomrarity = random.randint(1, 100)
            if 0 < randomrarity <= 30:
                randomrarity = "common"
            elif 30 < randomrarity <= 80:
                randomrarity = "uncommon"
            else:
                randomrarity = "rare"

            while True:
                item = items[random.choice(list(items))]
                if item["rarity"] == randomrarity:
                    item = item
                    break

            name, emoji = item["name"], item["emoji"]

            given = False
            for i in inventory:
                if i["name"] == name:
                    i["quantity"] += 1
                    given = True

            if not given:
                del item["emoji"], item["value"], item["description"], item["rarity"]
                item["locked"] = False
                item["quantity"] = 1
                inventory.append(item)

            embed = discord.Embed(title=":package: **Three Boxes**", description=f"You got **{emoji} {name}**!", color=discord.Color.dark_teal())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})


        elif game.replace(" ", "").lower() == "number" or game.replace(" ", "").lower() == "number guess":
            try:
                amount = int(amount)
            except Exception:
                return await ctx.send("Enter a valid amount.")

            if amount > balance:
                return await ctx.send("You don't have that much money!")

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author

            num = random.randint(1, 10)

            win = False
            for i in range(3):
                while True:
                    if i == 0:
                        embed = discord.Embed(title=":question: Number Guesser (1 to 10)", description=f"You have 3 guesses!", color=discord.Color.dark_teal())
                    else:
                        embed = discord.Embed(title=":question: Incorrect!", description=f"{3 - i} guesses remaining!", color=discord.Color.dark_teal())
                    await ctx.send(embed=embed)
                    try:
                        message = await self.bot.wait_for('message', check=check, timeout=10)
                    except asyncio.TimeoutError:
                        return await ctx.send(f"You ran out of time! Refunding $`{amount}`")

                    try:
                        input = int(message.content)
                        if 0 < input <= 10:
                            break
                        else:
                            await ctx.send("Enter a number between 1 and 10.")
                    except Exception:
                        await ctx.send("Enter a number between 1 and 10.")

                if input == num:
                    win = True
                    break
                #else:
                    #await ctx.send("**Incorrect!**")

            if win:
                balance += int(amount * 3)
                embed = discord.Embed(title=":question: Number Guesser", description=f"**Correct!** Your earned $`{int(amount * 3)}`", color=discord.Color.dark_teal())
            else:
                balance -= amount
                embed = discord.Embed(title=":question: Number Guesser", description=f"**Incorrect!** The number was `{num}`. Your lost $`{amount}`", color=discord.Color.dark_teal())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})


        elif game.replace(" ", "").lower() == "coinflip" or game.replace(" ", "").lower() == "coin" or game.replace(" ", "").lower() == "flip":
            try:
                amount = int(amount * 2)
            except Exception:
                return await ctx.send(f"Usage: `{self.bot.prefix}gamble coinflip (amount)`")

            if balance < amount:
                return await ctx.send(f"Insufficient funds! You need at least $`{amount}` to do that")

            balance - amount / 2

            embed = discord.Embed(title=f"<:coin:733930163817152565> You have bet $`{amount}`", description=f"Taken $`{amount}` and flipping coin <a:loading:733746914109161542>", color=discord.Color.dark_teal())
            message = await ctx.send(embed=embed)
            await asyncio.sleep(2)
            coin = ['heads', 'tails']
            coin = random.choice(coin)
            if coin == 'heads':
                balance += amount
                embed = discord.Embed(title=f"<:coin:733930163817152565> You have bet $`{amount}`", description=f"Coin has been flipped! It's **heads**, you win! You gained $`{amount * 2}`", color=discord.Color.dark_teal())
            else:
                balance -= amount
                embed = discord.Embed(title=f"<:coin:733930163817152565> You have bet $`{amount}`", description=f"Coin has been flipped! It's **tails**, you lose! You lost $`{amount}`", color=discord.Color.dark_teal())
            await message.edit(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

def setup(bot):
    bot.add_cog(Gambling(bot))
