import discord, platform, datetime, logging
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate

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
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def sell(self, ctx, item, quantity="1"):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        try:
            quantity = int(quantity)
        except Exception:
            return await ctx.send("Please enter a valid quantity.\n**Tip:** Items in commands generally don't contain spaces!")

        item = item.replace(" ", "").lower()
        items = await self.bot.items.find("items")
        items = items["items"]
        if item not in items:
            return await ctx.send("That item does not exist.")

        inventory = data["inventory"]
        item = items[item.lower()]
        name, emoji = item["name"], item["emoji"]

        change = False
        for i in inventory:
            if i["name"] == name:
                if i["quantity"] < quantity:
                    return await ctx.send(f"You don't have that many **{emoji} {name}s**")

                if i["locked"]:
                    return await ctx.send(f"**{emoji} {name}** is locked in your inventory.")

                if i["quantity"] == 1:
                    inventory.remove(i)
                    change = True
                else:
                    i["quantity"] -= quantity
                    if i["quantity"] == 0:
                        inventory.remove(i)
                    change = True

        if not change:
            return await ctx.send(f"You don't have a **{emoji} {name}**.")

        value = item["value"]
        balance = data["balance"]
        value = int(value * 0.75)
        balance += int(value * quantity)
        if quantity == 1:
            await ctx.send(f"You sold **{emoji} {name}** for $`{value}`. Your balance is now $`{balance}`.")
        else:
            await ctx.send(f"You sold **{quantity} {emoji} {name}s** for $`{value}` each. Your balance is now $`{balance}`.")
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
        await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

    # ----- ERROR HANDLER ------------------------------------------------------

    @sell.error
    async def sell_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}sell (item)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- SHOP ---------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def shop(self, ctx):
        entries = [
            ["Sponge", "$10", f"{self.bot.prefix}buy sponge"],
            ["ID", "$500", f"{self.bot.prefix}buy id"],
            ["Crystal", "$500", f"{self.bot.prefix}buy crystal"],
            ["Key", "$500", f"{self.bot.prefix}buy key"],
            ["Dynamite", "$1,000", f"{self.bot.prefix}buy dynamite"],
            ["Hammer", "$1,500", f"{self.bot.prefix}buy hammer"],
            ["Lock", "$2,000", f"{self.bot.prefix}buy lock"]
        ]

        output = ("The place to buy useful items\n```" + tabulate(entries, tablefmt="simple", headers=["Item", "Cost", "Command"]) + "```")
        embed = discord.Embed(title=":shopping_cart: Item Shop:", description=output, color=discord.Color.gold())
        await ctx.send(embed=embed)

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- BUY ----------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def buy(self, ctx, item, quantity="1"):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        try:
            quantity = int(quantity)
        except Exception:
            return await ctx.send("Please enter a valid quantity.\n**Tip:** Items in commands generally don't contain spaces!")

        inventory = data["inventory"]
        bal = data["balance"]
        item = item.replace(" ", "").lower()
        items = await self.bot.items.find("items")
        items = items["items"]

        # ITEMS
        if item == "sponge":
            item = items["sponge"]
            name, emoji, cost = item["name"], item["emoji"], item["value"]

            cost = int(cost * quantity)

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost

            for i in range(quantity):
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

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nQuantity: `{quantity}`\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})

        elif item == "id" or item == "idcard":
            item = items["id"]
            name, emoji, cost = item["name"], item["emoji"], item["value"]

            cost = int(cost * quantity)

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost

            for i in range(quantity):
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

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nQuantity: `{quantity}`\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})

        elif item == "crystal" or item == "gem":
            item = items["crystal"]
            name, emoji, cost = item["name"], item["emoji"], item["value"]

            cost = int(cost * quantity)

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost

            for i in range(quantity):
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

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nQuantity: `{quantity}`\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})

        elif item == "key":
            item = items["key"]
            name, emoji, cost = item["name"], item["emoji"], item["value"]

            cost = int(cost * quantity)

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost

            for i in range(quantity):
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

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nQuantity: `{quantity}`\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})

        elif item == "boomstick" or item == "dynamite":
            item = items["dynamite"]
            name, emoji, cost = item["name"], item["emoji"], item["value"]

            cost = int(cost * quantity)

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost

            for i in range(quantity):
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

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nQuantity: `{quantity}`\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})

        elif item == "hammer" or item == "sledgehammer":
            item = items["hammer"]
            name, emoji, cost = item["name"], item["emoji"], item["value"]

            cost = int(cost * quantity)

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost

            for i in range(quantity):
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

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nQuantity: `{quantity}`\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})

        elif item == "lock" or item == "Lock":
            item = items["lock"]
            name, emoji, cost = item["name"], item["emoji"], item["value"]

            cost = int(cost * quantity)

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost

            for i in range(quantity):
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

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nQuantity: `{quantity}`\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})

        else:
            await ctx.send("I couldn't find that item in the shop.")

    # ----- ERROR HANDLER ------------------------------------------------------

    @buy.error
    async def buy_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: `{self.bot.prefix}buy (item)`")

def setup(bot):
    bot.add_cog(Shop(bot))
