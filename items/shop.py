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
    async def sell(self, ctx, *, item):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

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

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- SHOP ---------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def shop(self, ctx, *, section=None):
        if not section:
            pass

        elif section.lower() == "bank" or section.lower() == "banking" or section.lower() == "banks":
            embed = discord.Embed(title=":bank: Banks", description="Protects your money from theives", color=discord.Color.gold())
            embed.add_field(name=":bank: Small Bank Slot", value=f"Store $`500` in the bank.\nCosts $`150`\n`{self.bot.prefix}buy small bank slot`", inline=False)
            embed.add_field(name=":bank: Medium Bank Slot", value=f"Store $`1000` in the bank.\nCosts $`300`\n`{self.bot.prefix}buy medium bank slot`", inline=False)
            embed.add_field(name=":bank: Large Bank Slot", value=f"Store $`10000` in the bank.\nCosts $`2500`\n`{self.bot.prefix}buy large bank slot`", inline=False)
            return await ctx.send(embed=embed)

        elif section.lower() == "item" or section.lower() == "items":
            embed = discord.Embed(title=":shopping_cart: Items", description="The place to buy your useful items", color=discord.Color.gold())
            embed.add_field(name=":card_index: ID", value=f"Prove you're almost human with one of these.\nCosts $`500`\n`{self.bot.prefix}buy id`", inline=False)
            return await ctx.send(embed=embed)

        embed = discord.Embed(title=":shopping_cart: Shop", color=discord.Color.gold())
        embed.add_field(name=":bank: Bank", value=f"`{self.bot.prefix}shop banks`", inline=False)
        embed.add_field(name=":shopping_cart: Items", value=f"`{self.bot.prefix}shop items`", inline=False)
        await ctx.send(embed=embed)

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- BUY ----------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def buy(self, ctx, *, item):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        inventory = data["inventory"]
        bal = data["balance"]
        banklimit = data["banklimit"]
        item = item.replace(" ", "").lower()
        items = await self.bot.items.find("items")
        items = items["items"]

        # BANKS

        if item == "smallbankslot" or item == "smallbank":
            cost = 150
            if banklimit != 0:
                return await ctx.send("A bank slot of greater or equal value has already been purchased.")

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost
            banklimit = 500
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "banklimit": banklimit})
            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: :bank: **Small Bank Slot**\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)

        elif item == "mediumbankslot" or item == "mediumbank":
            cost = 300
            if banklimit > 500:
                return await ctx.send("A bank slot of greater or equal value has already been purchased.")

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost
            banklimit = 1000
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "banklimit": banklimit})
            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: :bank: **Medium Bank Slot**\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)

        elif item == "largebankslot" or item == "largebank":
            cost = 2500
            if banklimit > 1000:
                return await ctx.send("A bank slot of greater or equal value has already been purchased.")

            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost
            banklimit = 10000
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "banklimit": banklimit})
            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: :bank: **Large Bank Slot**\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
            await ctx.send(embed=embed)

        # ITEMS

        elif item == "id" or item == "idcard":
            cost = 500
            if bal < cost:
                return await ctx.send(f"$`{cost}` is required to purchase this. You only have $`{bal}` and need another $`{cost - bal}` to afford this.")

            bal -= cost

            item = items["id"]
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

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nMoney spent: $`{cost}`\nNew balance: $`{bal}`", color=discord.Color.gold())
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
