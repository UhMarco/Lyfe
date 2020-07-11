import discord, platform, datetime, logging
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Inventories(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Inventories Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- INVENTORY ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, page="1"):
        try:
            page = int(page)
        except Exception:
            return await ctx.send("Not a valid page number.")
            
        data = await self.bot.inventories.find(ctx.author.id)
        items = await self.bot.items.find("items")
        items = items["items"]

        if data is None:
            data = []
            await ctx.send("It seems this is your first time checking your inventory, I'll give you a shopping cart and $`100` to get started!")
            item = items["shoppingcart"]
            del item["emoji"], item["value"], item["description"]
            item["locked"] = False
            item["quantity"] = 1
            data.append(item)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": 100})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": data})

        # Reset variables
        data = await self.bot.inventories.find(ctx.author.id)
        items = await self.bot.items.find("items")
        items = items["items"]
        inventory = data["inventory"]
        bal = data["balance"]

        pagelimit = 5 * round(len(inventory) / 5)
        if pagelimit < len(inventory): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        if page > pagelimit:
            if page == 1:
                return await ctx.send("Your inventory is empty!")
            return await ctx.send("You don't have that many pages!")

        embed = discord.Embed(title=f":desktop: **{ctx.author.name}'s Inventory**", description=f"**Balance:** $`{bal}`", color=discord.Color.blue())
        count = 0
        for i in inventory:
            count += 1
            if count > page * 5 - 5:
                name, locked, quantity = i["name"], i["locked"], i["quantity"]
                item = items[name.replace(" ", "").lower()]
                desc, emoji, value = item["description"], item["emoji"], item["value"]
                embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`\n**Quantity:** `{quantity}`", inline=False)

            if count == page * 5:
                break

        embed.set_footer(text=f"{ctx.author.id} | Page: {page}/{pagelimit}")
        await ctx.send(embed=embed)

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- INVENTORY SEE ------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['invsee'])
    async def inventorysee(self, ctx, user: discord.Member, page=1):
        data = await self.bot.inventories.find(user.id)

        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        inventory = data["inventory"]
        bal = data["balance"]
        items = await self.bot.items.find("items")
        items = items["items"]

        pagelimit = 5 * round(len(inventory) / 5)
        if pagelimit < len(inventory): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        if page > pagelimit:
            if page == 1:
                return await ctx.send(f"**{user.name}'s** inventory is empty!")
            return await ctx.send(f"**{user.name}** doesn't have that many pages!")

        embed = discord.Embed(title=f":desktop: **{user.name}'s Inventory**", description=f"**Balance:** $`{bal}`", color=discord.Color.red())
        count = 0
        for i in inventory:
            count += 1
            if count > page * 5 - 5:
                name, locked, quantity = i["name"], i["locked"], i["quantity"]
                item = items[name.replace(" ", "").lower()]
                desc, emoji, value = item["description"], item["emoji"], item["value"]
                embed.add_field(name=f"{emoji} {name}", value=f"**Description:** `{desc}`\n**Locked:** `{locked}`\n**Value:** $`{value}`\n**Quantity:** `{quantity}`", inline=False)

            if count == page * 5:
                break

        embed.set_footer(text=f"{user.id} | Page: {page}/{pagelimit}")
        await ctx.send(embed=embed)

    # ----- ERROR HANDLER ------------------------------------------------------

    @inventorysee.error
    async def inventorysee_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}inventorysee (user) [page]`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- ITEM INFO ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['ii', 'getinfo'])
    async def iteminfo(self, ctx, item):
        items = await self.bot.items.find("items")
        items = items["items"]
        if item.lower() not in items:
            embed = discord.Embed(title="Item Doesn't Exist", color=discord.Colour.purple())
            return await ctx.send(embed=embed)
        item = items[item.lower()]

        name, desc, emoji, value = item["name"], item["description"], item["emoji"], item["value"]
        embed = discord.Embed(
            title=f"{emoji} **{name}**",
            description=f"**Description:** `{desc}`\n**Value:** $`{value}`",
            color=discord.Colour.purple()
        )
        await ctx.send(embed=embed)

    # ----- ERROR HANDLER ------------------------------------------------------

    @iteminfo.error
    async def iteminfo_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix} iteminfo (item)`")


def setup(bot):
    bot.add_cog(Inventories(bot))
