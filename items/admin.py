import discord, platform, datetime, logging
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Admin Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- ITEM LIST ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['li', 'listitems', 'il'])
    @commands.is_owner()
    async def itemlist(self, ctx, page=1):
        items = await self.bot.items.find("items")
        items = items["items"]
        embed = discord.Embed(title="**Item List**", color=discord.Color.purple())

        pagelimit = 5 * round(len(items) / 5)
        if pagelimit < len(items): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        if page > pagelimit:
            if page == 1:
                return await ctx.send("Empty!")
            return await ctx.send("There aren't that many pages!")

        count = 0
        for item in items:
            item = items[item]
            count += 1
            if count > page * 5 - 5:
                name, desc, emoji, value, rarity = item["name"], item["description"], item["emoji"], item["value"], item["rarity"]
                embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Rarity:** `{rarity}`\n**Value:** $`{value}`", inline=False)

            if count == page * 5:
                break

        embed.set_footer(text=f"Item List | Page: {page}/{pagelimit}")
        await ctx.send(embed=embed)

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- SPAWN ITEM ---------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['si', 'gi'])
    @commands.is_owner()
    async def spawnitem(self, ctx, item, user: discord.Member):
        data = await self.bot.inventories.find(user.id)
        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        inventory = data["inventory"]
        item = items[item.lower()]
        name, emoji = item["name"], item["emoji"]

        for i in inventory:
            if i["name"] == name:
                i["quantity"] += 1
                await self.bot.inventories.update_by_id({"_id": ctx.author.id, "inventory": inventory})
                return await ctx.send(f"Given **{emoji} {name}** to **{user.name}**")

        del item["emoji"], item["value"], item["description"], item["rarity"]
        item["locked"] = False
        item["quantity"] = 1
        inventory.append(item)
        await ctx.send(f"Given **{emoji} {name}** to **{user.name}**.")
        await self.bot.inventories.upsert({"_id": user.id, "inventory": inventory})

    # ----- ERROR HANDLER ------------------------------------------------------

    @spawnitem.error
    async def spawnitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}spawnitem (item) (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- REMOVE ITEM --------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['ri'])
    @commands.is_owner()
    async def removeitem(self, ctx, item, user: discord.Member):
        data = await self.bot.inventories.find(user.id)
        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        inventory = data["inventory"]
        item = items[item.lower()]
        name, emoji = item["name"], item["emoji"]

        change = False
        for i in inventory:
            if i["name"] == name:
                if i["quantity"] == 1:
                    inventory.remove(i)
                    change = True
                else:
                    i["quantity"] -= 1
                    change = True
        if not change:
            return await ctx.send(f"**{user.name}** doesn't have a **{emoji} {name}**.")
        await ctx.send(f"Removed **{emoji} {name}** from **{user.name}**.")
        await self.bot.inventories.upsert({"_id": user.id, "inventory": inventory})

    # ----- ERROR HANDLER ------------------------------------------------------

    @removeitem.error
    @commands.is_owner()
    async def removeitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}removeitem (item) (user)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    # Abandoning format for this as I honestly can't be bothered

    @commands.command(aliases=['sb'])
    async def setbalance(self, ctx, user: discord.Member, amount="n"):
        data = await self.bot.inventories.find(user.id)
        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        try:
            amount = int(amount)
        except Exception:
            return await ctx.send("Enter a valid amount")

        await self.bot.inventories.upsert({"_id": user.id, "balance": amount})
        await ctx.send(f"Set **{user.name}'s** balance to $`{amount}`")


def setup(bot):
    bot.add_cog(Admin(bot))
