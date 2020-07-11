import discord, platform, datetime, logging
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Shop Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- SELL ---------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def sell(self, ctx, item):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

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
            return await ctx.send(f"You don't have a **{emoji} {name}**.")

        value = item["value"]
        balance = data["balance"]
        balance += value
        await ctx.send(f"You sold **{emoji} {name}** for $`{value}`. Your balance is now $`{balance}`.")
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
        await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

    # ----- ERROR HANDLER ------------------------------------------------------

    @sell.error
    async def sell_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}sell (item)`")


def setup(bot):
    bot.add_cog(Shop(bot))
