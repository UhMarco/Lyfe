import discord, platform, logging, random, os, asyncio, math
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate
from datetime import datetime, timedelta

class Inventory(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Inventory Cog loaded")


    @commands.command(aliases=['inv', 'inventorysee', 'invsee'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def inventory(self, ctx, user=None, page="1"):
        if len(ctx.message.mentions) == 0:
            if user is None:
                page = 1
                user = ctx.author
            else:
                try:
                    if self.bot.get_user(int(user)) == None:
                        page = user
                        user = ctx.author
                    else:
                        user = self.bot.get_user(int(user))
                except ValueError:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        try:
            page = int(page)
            if page < 1:
                page = 1
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
                page = 1
            else:
                return await ctx.send(f"**{user.name}** hasn't initialized their inventory yet.")

        data = await self.bot.inventories.find(user.id)
        items = await self.bot.items.find("items")
        items = items["items"]
        inventory = data["inventory"]
        bal = data["balance"]
        bankbal = data["bankbalance"]
        banklimit = data["banklimit"]
        ## Peanut Allergy
        if user == ctx.author:
            peanut = "Peanut"
            money = random.randint(50, 120)
            has_allergy = random.choice([1, 2])
            if has_allergy == 1:
                for i in inventory:
                    if i["name"] == peanut:
                            if bal > 120:
                                bal -= money
                                nutembed = discord.Embed(
                                    title=":peanuts: Peanut Allergy",
                                    description=f"Oh no! You had an allergic reaction to some peanuts in your inventory.\nYou had to pay $`{money}` for treatment.",
                                    color=discord.Color.red()
                                )
                                await ctx.send(embed=nutembed)
                                await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": bal})

        pagelimit = 5 * round(len(inventory) / 5)
        if pagelimit < len(inventory): pagelimit += 5
        pagelimit = int(pagelimit / 5)

        titles = data["titles"]
        title = ""
        try:
            title = f"**{titles[0]}**\n"
        except KeyError:
            pass

        if page > pagelimit:
            if page == 1:
                emptyembed = discord.Embed(
                    title=":wastebasket: Empty Inventory",
                    description=f"**{user.name}'s** inventory is empty!\n**Balance:** $`{bal}`\n**Bank:** $`{bankbal}`/`{banklimit}`",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=emptyembed)
            return await ctx.send(f"**{user.name}** doesn't have that many pages!")

        if user == ctx.author:
            color = discord.Color.blue()
        else:
            color = discord.Color.red()

        embed = discord.Embed(title=f":desktop: **{user.name}'s Inventory**", description=f"{title}**Balance:** $`{bal}`\n**Bank:** $`{bankbal}`/`{banklimit}`", color=color)
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

    @commands.command()
    async def claim(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You haven't initialized your inventory yet.")

        cooldowns = await self.bot.cooldowns.find(ctx.author.id)
        try:
            if cooldowns is None or cooldowns["claim"] < datetime.now() - timedelta(hours=1):
                await self.bot.cooldowns.upsert({"_id": ctx.author.id, "claim": datetime.now()})
            else:
                difference = datetime.now() - cooldowns["claim"]
                retry_after = 3600 - difference.total_seconds()
                m, s = divmod(retry_after, 60)
                h, m = divmod(m, 60)
                if int(h) == 0 and int(m) == 0:
                    await ctx.send(f':mailbox_with_no_mail: You must wait **{int(s)} seconds** to claim again.')
                elif int(h) == 0 and int(m) != 0:
                    await ctx.send(f':mailbox_with_no_mail: You must wait **{int(m)} minutes and {int(s)} seconds** to claim again.')
                else:
                    await ctx.send(f':mailbox_with_no_mail: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to claim again.')

                return

        except (KeyError, IndexError):
            await self.bot.cooldowns.upsert({"_id": ctx.author.id, "claim": datetime.now()})

        inventory = data["inventory"]
        items = await self.bot.items.find("items")
        items = items["items"]

        randomrarity = random.randint(1, 100)
        if 0 < randomrarity <= 50:
            randomrarity = "common"
        elif 50 < randomrarity <= 80:
            randomrarity = "uncommon"
        elif 80 < randomrarity <= 99:
            randomrarity = "rare"
        else:
            randomrarity = "ultra rare"

        while True:
            item = items[random.choice(list(items))]
            if item["rarity"] == randomrarity:
                daily = item
                break

        name, emoji = daily["name"], daily["emoji"]

        given = False
        for i in inventory:
            if i["name"] == name:
                i["quantity"] += 1
                given = True

        if not given:
            del daily["emoji"], daily["value"], daily["description"], daily["rarity"]
            daily["locked"] = False
            daily["quantity"] = 1
            inventory.append(daily)

        await ctx.send(f":mailbox_with_mail: You got **{emoji} {name}**.")
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})

    @commands.command()
    async def daily(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You haven't initialized your inventory yet.")

        streak = 1
        try:
            cooldowns = await self.bot.cooldowns.find(ctx.author.id)
            if cooldowns is None or cooldowns["daily"] < datetime.now() - timedelta(days=1):
                await self.bot.cooldowns.upsert({"_id": ctx.author.id, "daily": datetime.now()})
                if cooldowns != None: # If it's not the first time
                    if not cooldowns["daily"] < datetime.now() - timedelta(days=2): # If it hasn't been more than 2 days
                        try:
                            streak = cooldowns["dailystreak"]
                            streak += 1
                            await self.bot.cooldowns.upsert({"_id": ctx.author.id, "dailystreak": streak})
                        except (KeyError, IndexError):
                            await self.bot.cooldowns.upsert({"_id": ctx.author.id, "dailystreak": 1})
                    else:
                        await self.bot.cooldowns.upsert({"_id": ctx.author.id, "dailystreak": 1})
                else:
                    await self.bot.cooldowns.upsert({"_id": ctx.author.id, "dailystreak": 1})
            else:
                difference = datetime.now() - cooldowns["daily"]
                retry_after = 86400 - difference.total_seconds()
                m, s = divmod(retry_after, 60)
                h, m = divmod(m, 60)
                if int(h) == 0 and int(m) == 0:
                    await ctx.send(f':mailbox_with_no_mail: You must wait **{int(s)} seconds** to claim again.')
                elif int(h) == 0 and int(m) != 0:
                    await ctx.send(f':mailbox_with_no_mail: You must wait **{int(m)} minutes and {int(s)} seconds** to claim again.')
                else:
                    await ctx.send(f':mailbox_with_no_mail: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to claim again.')
                return
        except (KeyError, IndexError):
            await self.bot.cooldowns.upsert({"_id": ctx.author.id, "daily": datetime.now()})

        inventory = data["inventory"]
        items = await self.bot.items.find("items")
        items = items["items"]

        #min = int(170 / math.pi * math.atan(1/15 * (streak - 1)))
        a = 1.356248795
        try:
            min = int(85 / a * (a - 1 / (a ** (streak / 7 - 8 / 7))))
        except ZeroDivisionError:
            min = 0
        randomrarity = random.randint(min, 100)

        if 0 < randomrarity <= 30:
            randomrarity = "common"
        elif 30 < randomrarity <= 80:
            randomrarity = "uncommon"
        elif 80 < randomrarity <= 95:
            randomrarity = "rare"
        else:
            randomrarity = "ultra rare"

        while True:
            item = items[random.choice(list(items))]
            if item["rarity"] == randomrarity:
                daily = item
                break

        name, emoji = daily["name"], daily["emoji"]

        given = False
        for i in inventory:
            if i["name"] == name:
                i["quantity"] += 1
                given = True

        if not given:
            del daily["emoji"], daily["value"], daily["description"], daily["rarity"]
            daily["locked"] = False
            daily["quantity"] = 1
            inventory.append(daily)

        balance = data["balance"]
        amount = random.randint(100 + min * 5, 500 + min * 5)
        balance += amount

        if streak is None or streak == 1:
            await ctx.send(f":mailbox_with_mail: You got **{emoji} {name}** and $`{amount}`")
        else:
            await ctx.send(f":mailbox_with_mail: You got **{emoji} {name}** and $`{amount}` - You're on a streak of :fire: **{streak}**!")
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
        await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

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

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}lock (item)`")


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

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}unlock (item)`")

def setup(bot):
    bot.add_cog(Inventory(bot))
