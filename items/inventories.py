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

    @commands.command(aliases=['inv', 'inventorysee',  'invsee'])
    async def inventory(self, ctx, user=None, page="1"):
        if len(ctx.message.mentions) == 0:
            if user is None:
                page = 1
            else:
                page = user
            user = ctx.author
            pass
        else:
            user = ctx.message.mentions[0]

        try:
            page = int(page)
        except Exception:
            return await ctx.send("Not a valid page number.")

        data = await self.bot.inventories.find(user.id)
        items = await self.bot.items.find("items")
        items = items["items"]

        if data is None:
            if user == ctx.author:
                data = []
                await ctx.send("It seems this is your first time checking your inventory, I'll give you a shopping cart and $`100` to get started!")
                item = items["shoppingcart"]
                del item["emoji"], item["value"], item["description"], item["rarity"]
                item["locked"] = False
                item["quantity"] = 1
                data.append(item)
                await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": 100})
                await self.bot.inventories.upsert({"_id": ctx.author.id, "bankbalance": 0})
                await self.bot.inventories.upsert({"_id": ctx.author.id, "banklimit": 0})
                await self.bot.inventories.upsert({"_id": ctx.author.id, "job": None})
                await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": data})
            else:
                return await ctx.send(f"**{user.name}** hasn't initialized their inventory yet.")

        data = await self.bot.inventories.find(user.id)
        items = await self.bot.items.find("items")
        items = items["items"]
        inventory = data["inventory"]
        bal = data["balance"]
        bankbal = data["bankbalance"]
        banklimit = data["banklimit"]

        pagelimit = 5 * round(len(inventory) / 5)
        if pagelimit < len(inventory): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        if page > pagelimit:
            if page == 1:
                return await ctx.send(f"**{user.name}'s** inventory is empty!")
            return await ctx.send(f"**{user.name}** doesn't have that many pages!")

        if user == ctx.author:
            color = discord.Color.blue()
        else:
            color = discord.Color.red()

        embed = discord.Embed(title=f":desktop: **{user.name}'s Inventory**", description=f"**Balance:** $`{bal}`\n**Bank:** $`{bankbal}`/`{banklimit}`", color=color)
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

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- BALANCE ------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['bal'])
    async def balance(self, ctx, user: discord.Member):
        data = await self.bot.inventories.find(user.id)

        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        balance = data["balance"]
        bankbalance = data["bankbalance"]
        banklimit = data["banklimit"]
        await ctx.send(f"**{user.name}'s** balance is $`{balance}` and $`{bankbalance}`/`{banklimit}` is stored in their bank.")

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            data = await self.bot.inventories.find(ctx.author.id)

            if data is None:
                return await ctx.send("You haven't initialized your inventory yet.")

            balance = data["balance"]
            bankbalance = data["bankbalance"]
            banklimit = data["banklimit"]
            await ctx.send(f"Your balance is $`{balance}` and $`{bankbalance}`/`{banklimit}` is stored in your bank.")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- ITEM INFO ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['ii', 'getinfo'])
    async def iteminfo(self, ctx, *, item):
        item = item.replace(" ", "").lower()
        items = await self.bot.items.find("items")
        items = items["items"]
        if item not in items:
            embed = discord.Embed(title="Item Doesn't Exist", color=discord.Colour.purple())
            return await ctx.send(embed=embed)
        item = items[item]

        name, desc, emoji, value, rarity = item["name"], item["description"], item["emoji"], item["value"], item["rarity"]
        embed = discord.Embed(
            title=f"{emoji} **{name}**",
            description=f"**Description:** `{desc}`\n**Rarity:** `{rarity}`\n**Value:** $`{value}`",
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
