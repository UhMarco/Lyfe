import discord, platform, datetime, logging
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Locking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Locking Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- ITEM INFO ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def lock(self, ctx, item):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")
        elif item.lower() == "lock":
            return await ctx.send("You can't lock this item.")

        inventory = data["inventory"]
        # Check if a lock is owned
        found = False
        for i in inventory:
            if i["name"] == "Lock":
                found = True
                break
        if not found:
            return await ctx.send("You don't have **:lock: Lock** in your inventory.")

        # Check if you own the item
        name, emoji = items[item.replace(" ", "").lower()]["name"], items[item.replace(" ", "").lower()]["emoji"]
        found = False
        for i in inventory:
            if i["name"].replace(" ", "").lower() == item: # If found, check if locked.
                found = True
                if i["locked"]:
                    return await ctx.send(f"{emoji} {name} already locked.")
                else:
                    i["locked"] = True
                break
        if not found:
            return await ctx.send(f"You don't own a **{emoji} {name}**.")

        # Remove lock from inventory
        for i in inventory:
            if i["name"] == "Lock":
                if i["quantity"] == 1:
                    inventory.remove(i)
                else:
                    i["quantity"] -= 1

        embed = discord.Embed(title=f"**{emoji} {name}** locked.\n**:lock: Lock** used.", color=discord.Color.blue())
        await ctx.send(embed=embed)
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})

    # ----- ERROR HANDLER ------------------------------------------------------

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.lock (item)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- ITEM INFO ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def unlock(self, ctx, item):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]
        if item.lower() not in items:
            return await ctx.send("That item does not exist.")

        inventory = data["inventory"]
        # Check if a unlock is owned
        found = False
        for i in inventory:
            if i["name"] == "Key":
                found = True
                break
        if not found:
            return await ctx.send("You don't have **:key: Key** in your inventory.")

        # Check if you own the item
        name, emoji = items[item.replace(" ", "").lower()]["name"], items[item.replace(" ", "").lower()]["emoji"]
        found = False
        for i in inventory:
            if i["name"].replace(" ", "").lower() == item: # If found, check if locked.
                found = True
                if not i["locked"]:
                    return await ctx.send(f"{emoji} {name} is not locked.")
                else:
                    i["locked"] = False
                break
        if not found:
            return await ctx.send(f"You don't own a **{emoji} {name}**.")

        # Remove lock from inventory
        for i in inventory:
            if i["name"] == "Key":
                if i["quantity"] == 1:
                    inventory.remove(i)
                else:
                    i["quantity"] -= 1

        embed = discord.Embed(title=f"**{emoji} {name}** unlocked.\n**:key: Key** used.", color=discord.Color.blue())
        await ctx.send(embed=embed)
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})

    # ----- ERROR HANDLER ------------------------------------------------------

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.unlock (item)`")


def setup(bot):
    bot.add_cog(Locking(bot))
