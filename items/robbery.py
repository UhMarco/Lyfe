import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate

robberytools = ['gun', 'hammer', 'knife']

class Robbery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Robbery Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- ROBBERY ------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['rob', 'burgle'])
    async def robbery(self, ctx, user: discord.Member, tool=None, item=None):
        if user.id == ctx.author.id:
            return await ctx.send("You can't rob yourself.")

        mydata = await self.bot.inventories.find(ctx.author.id)
        if mydata is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        yourdata = await self.bot.inventories.find(user.id)
        if yourdata is None:
            return await ctx.send(f"**{user.name}** hasn't initialized their inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]
        if not item:
            return await ctx.send("Usage: `.robbery [victim] [tool] [item]`")
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")
        if tool.lower() not in items:
            return await ctx.send("That tool does not exist.")

        if tool.lower() not in robberytools:
            return await ctx.send("That is not a valid tool.")

        item = items[item.lower()]
        tool = items[tool.lower()]
        myinventory = mydata["inventory"]
        yourinventory = yourdata["inventory"]

        # Check if robber has the tool
        found = False
        for i in myinventory:
            if i["name"] == tool["name"]:
                found = True
                break
        if not found:
            return await ctx.send("You don't have that tool in your inventory.")

        # Check if victim has the item
        found = False
        for i in yourinventory:
            if i["name"] == item["name"]:
                if i["locked"]:
                    emoji, name = item["emoji"], i["name"]
                    return await ctx.send(f"**{emoji} {name}** has been locked in **{user.name}**'s inventory.")
                found = True
                break
        if not found:
            emoji, name = item["emoji"], item["name"]
            return await ctx.send(f"**{user.name}** doesn't have **{emoji} {name}**.")

        # Robber's tool has been used
        for i in myinventory:
            if i["name"] == tool["name"]:
                if i["quantity"] == 1:
                    myinventory.remove(i)
                else:
                    i["quantity"] -= 1

        # Check probability of successful robbery
        rand = random.randint(0, 100)
        chance = int(tool["description"][:3].strip("% "))

        toolname, itemname = tool["name"], item["name"]
        toolemoji, itememoji = items[toolname.replace(" ", "").lower()]["emoji"], items[itemname.replace(" ", "").lower()]["emoji"]

        if rand <= chance: # Success
            for i in yourinventory:
                if i["name"] == item["name"]:
                    if i["quantity"] == 1:
                        yourinventory.remove(i)
                    else:
                        i["quantity"] -= 1

            given = False
            for i in myinventory:
                if i["name"] == item["name"]:
                    i["quantity"] += 1
                    given = True

            if not given:
                del item["emoji"], item["value"], item["description"], item["rarity"]
                item["locked"] = False
                item["quantity"] = 1
                myinventory.append(item)

            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name}'s robbery from {user.name}",
                description=f"**Robbery Succeeded**\n**{ctx.author.name}** gained **{itememoji} {itemname}** from **{user.name}**.\n**{ctx.author.name}** used **{toolemoji} {toolname}** to commit the robbery.",
                color=discord.Color.green()
            )
            await ctx.send(embed = embed)
            try:
                embed = discord.Embed(
                    title=f":moneybag: {ctx.author.name} has robbed you!",
                    description=f"**Robbery Succeeded**\n**{ctx.author.name}** gained **{itememoji} {itemname}** from **{user.name}**.\n**{ctx.author.name}** used **{toolemoji} {toolname}** to commit the robbery.",
                    color=discord.Color.red()
                )
                await user.send(embed=embed)
            except Forbidden:
                pass

        else: # Fail
            failureReasons = utils.json.read_json("robbery")
            failureReason = random.choice(failureReasons["failureReasons"])
            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name}'s robbery from {user.name}",
                description=f"{failureReason}\n**{ctx.author.name}** lost **{toolemoji} {toolname}** while trying to steal **{itememoji} {itemname}** from **{user.name}**.",
                color=discord.Color.red()
            )
            await ctx.send(embed = embed)
            try:
                embed = discord.Embed(
                    title=f":moneybag: {ctx.author.name} attempted to rob you!",
                    description=f"{failureReason}\n**{ctx.author.name}** lost **{toolemoji} {toolname}** while trying to steal **{itememoji} {itemname}** from **{user.name}**.",
                    color=discord.Color.green()
                )
                await user.send(embed=embed)
            except Forbidden:
                pass

        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": myinventory})
        await self.bot.inventories.upsert({"_id": user.id, "inventory": yourinventory})

    # ----- ERROR HANDLER ------------------------------------------------------

    @robbery.error
    async def robbery_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            data = await self.bot.inventories.find(ctx.author.id)
            if data is None:
                return await ctx.send("You haven't initialized your inventory yet.")

            items = await self.bot.items.find("items")
            items = items["items"]
            inventory = data["inventory"]

            embed = discord.Embed(title=f":hammer_pick: **{ctx.author.name}'s Robbery Tools**", color=discord.Color.blue())
            empty = True
            for i in inventory:
                name = i["name"]
                if any(ele in name.lower() for ele in robberytools):
                    locked, quantity = i["locked"], i["quantity"]
                    item = items[name.replace(" ", "").lower()]
                    desc, emoji, value = item["description"], item["emoji"], item["value"]
                    embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`\n**Quantity:** `{quantity}`", inline=False)
                    empty = False

            if empty:
                embed.add_field(name="You don't have any robbery tools!", value="`No robbing for you :(`", inline=False)
            embed.add_field(name="Usage:", value=f"`{self.bot.prefix}robbery [victim] [tool] [item]`", inline=False)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- DYNAMITE -----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def dynamite(self, ctx, user: discord.Member):
        author_data = await self.bot.inventories.find(ctx.author.id)
        if author_data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        if user == ctx.author:
            return await ctx.send("Consider yourself blown up. I'm not actually going to do anything though.")

        user_data = await self.bot.inventories.find(user.id)
        if user_data is None:
            return await ctx.send(f"**{user.name}** hasn't initialized their inventory yet.")

        inventory = author_data["inventory"]
        balance = user_data["balance"]
        bankbal = user_data["bankbalance"]

        if balance < 10:
            if bankbal == 0:
                return await ctx.send(f"**{user.name}** is incredibly poor, leave them alone will ya?")
            else:
                return await ctx.send(f"**{user.name}** doesn't have enough money in their inventory for you to blow up. Maybe check their bank account :smirk:")

        found = False
        for i in inventory:
            if i["name"] == "Dynamite":
                if i["quantity"] != 1:
                    i["quantity"] -= 1
                else:
                    inventory.remove(i)
                found = True

        if not found:
            return await ctx.send("You don't have a :firecracker: **Dynamite** in your inventory.")

        originalbalance = balance
        balance = int(balance * 0.8)

        await ctx.send(f":firecracker: You blew up $`{int(originalbalance * 0.2)}` of **{user.name}'s** money.")
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
        await self.bot.inventories.upsert({"_id": user.id, "balance": balance})
        try:
            await user.send(f"**{ctx.author}** blew up $`{int(originalbalance * 0.2)}` of your money!")
        except Forbidden:
            pass

    # ----- ERROR HANDLER ------------------------------------------------------

    @dynamite.error
    async def dynamite_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}dynamite (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- STEAL --------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=["mug"])
    async def steal(self, ctx, user: discord.Member, amount=1):
        author_data = await self.bot.inventories.find(ctx.author.id)
        if author_data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        if user == ctx.author:
            return await ctx.send("You put the money in the bag and then took it back home.")

        user_data = await self.bot.inventories.find(user.id)
        if user_data is None:
            return await ctx.send(f"**{user.name}** hasn't initialized their inventory yet.")

        inventory = author_data["inventory"]
        balance = user_data["balance"]
        bankbal = user_data["bankbalance"]
        amount = int(amount)

        if balance < 10:
            if bankbal == 0:
                return await ctx.send(f"**{user.name}** is practically broke, leave them alone will ya?")
            else:
                return await ctx.send(f"**{user.name}** doesn't have enough money in their inventory for you to yoink. Maybe check their bank account :smirk:")

        found = False
        for i in inventory:
            if i["name"] == "Gun":
                if i["quantity"] != 1:
                    i["quantity"] -= 1
                else:
                    inventory.remove(i)
                found = True

        if not found:
            return await ctx.send("You don't have a :gun: **Gun** in your inventory.")

        random1 = random.randint(0, 100)

        if amount > 5000:
            return await ctx.send("Don't be so greedy! The maxmimum is $`5000`")
        if amount < 500:
            return await ctx.send("What's the point of that? The minimum is $`500`")

        threshold = float((amount - 500) * 0.0003)

        if random1 > float(85 - threshold):
            failureReasons = utils.json.read_json("robbery")
            failureReason = random.choice(failureReasons["failureReasons"])
            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name}'s robbery from {user.name}",
                description=f"{failureReason}\n**{ctx.author.name}** lost **:gun: Gun** while trying to steal $`{amount}` from **{user.name}**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

            try:
                embed = discord.Embed(
                    title=f":moneybag: {ctx.author.name} attempted to rob you!",
                    description=f"{failureReason}\n**{ctx.author.name}** lost **:gun: Gun** while trying to steal $`{amount}` from **{user.name}**.",
                    color=discord.Color.green()
                )
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

            return await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})

        authorBalance = author_data["balance"]
        authorBalance = int(authorBalance + amount)

        originalbalance = balance

        balance = int(balance - amount)

        embed = discord.Embed(
            title=f":moneybag: {ctx.author.name}'s robbery from {user.name}",
            description=f"**{ctx.author.name}** stole $`{amount}` from **{user.name}** with a :gun: **Gun**.",
            color=discord.Color.green()
        )

        await ctx.send(f":gun: You stole up $`{amount}` of **{user.name}'s** money.")
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
        await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})
        await self.bot.inventories.upsert({"_id": user.id, "balance": balance})
        try:
            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name} has robbed you!",
                description=f"**{ctx.author.name}** stole $`{amount}` from **{user.name}** with a :gun: **Gun**.",
                color=discord.Color.red()
            )

            await user.send(f"**{ctx.author}** stole $`{amount}` of your money!")
        except Forbidden:
            pass

    # ----- ERROR HANDLER ------------------------------------------------------

    @steal.error
    async def steal_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}steal (user) (amount)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user or I couldnt find the amount idk")

def setup(bot):
    bot.add_cog(Robbery(bot))
