import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

robberytools = ['Gun', 'Hammer', 'Knife']

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
            return await ctx.send("This user hasn't initialized their inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]
        if not item:
            return await ctx.send("Usage: `.robbery [victim] [tool] [item]`")
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")
        if tool.lower() not in items:
            return await ctx.send("That tool does not exist.")

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

        else: # Fail
            embed = discord.Embed(
                title=f":moneybag: {ctx.author.name}'s robbery from {user.name}",
                description=f"**Robbery Failed**\n**{ctx.author.name}** lost **{toolemoji} {toolname}** while trying to steal **{itememoji} {itemname}** from **{user.name}**.",
                color=discord.Color.red()
            )
            await ctx.send(embed = embed)

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
                if any(ele in name for ele in robberytools):
                    locked, quantity = i["locked"], i["quantity"]
                    item = items[name.replace(" ", "").lower()]
                    desc, emoji, value = item["description"], item["emoji"], item["value"]
                    embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`\n**Quantity:** `{quantity}`", inline=False)
                    empty = False

            if empty:
                embed.add_field(name="You don't have any robbery tools!", value="`No robbing for you :(`", inline=False)
            embed.add_field(name="Usage:", value="`.robbery [victim] [tool] [item]`", inline=False)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")


def setup(bot):
    bot.add_cog(Robbery(bot))
