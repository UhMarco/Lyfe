import discord, platform, datetime, logging, random
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
            embed = discord.Embed(title=":game_die: **Gambling**", description="Spend your money sensibly by doing some gambling!`", color=discord.Color.dark_teal())
            embed.add_field(name=":package: Three Boxes", value=f"Choose a prize from 3 mystery boxes! Costs $`750`\n`{self.bot.prefix}gamble boxes`", inline=False)
            embed.add_field(name=":question: Guess the number", value=f"Guess the correct number to double however much you enter\n`{self.bot.prefix}gamble number`", inline=False)
            embed.add_field(name="<:coin:733930163817152565> Coin Flip", value=f"50% chance of doubling your money\n`{self.bot.prefix}gamble coinflip`", inline=False)
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
                message = await self.bot.wait_for('message', check=check)
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
            embed = discord.Embed()

        elif game.replace(" ", "").lower() == "coinflip" or game.replace(" ", "").lower() == "coin" or game.replace(" ", "").lower() == "flip":
            if balance < 1:
                return await ctx.send("Now how are you going to do that?")
            #balance -= amount
            embed = discord.Embed(f"You have bet {amount}", description = "Flipping coin <a:loading:733746914109161542>")
            embed = discord.Embed(f"You have bet {amount}", description = "Coin has been flipped")
            await self.bot.edit_message(msg, embed=embed)

def setup(bot):
    bot.add_cog(Gambling(bot))
