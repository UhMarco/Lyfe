import discord, platform, datetime, logging
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

def is_dev():
    def predictate(ctx):
        devs = utils.json.read_json("devs")
        if any(ctx.author.id for ele in devs):
            return ctx.author.id
    return commands.check(predictate)

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
    @is_dev()
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
    @is_dev()
    async def spawnitem(self, ctx, item, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

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

        found = False
        for i in inventory:
            if i["name"] == name:
                i["quantity"] += 1
                found = True

        if not found:
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
            return await ctx.send(f"Usage: `{self.bot.prefix}spawnitem (item) (user)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- REMOVE ITEM --------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['ri'])
    @is_dev()
    async def removeitem(self, ctx, item, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

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
    async def removeitem_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}removeitem (item) (user)`")

    # Abandoning format for this as I honestly can't be bothered

    @commands.command(aliases=['sb'])
    @is_dev()
    async def setbalance(self, ctx, user, amount="n"):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        data = await self.bot.inventories.find(user.id)
        if data is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")

        try:
            amount = int(amount)
        except Exception:
            return await ctx.send("Enter a valid amount")

        await self.bot.inventories.upsert({"_id": user.id, "balance": amount})
        await ctx.send(f"Set **{user.name}'s** balance to $`{amount}`")

    @setbalance.error
    async def setbalance_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}setbalance (user) (amount)`")

    @commands.command(aliases=['reset'])
    @is_dev()
    async def resetdata(self, ctx, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        await ctx.send("Please confirm.")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        message = await self.bot.wait_for('message', check=check)
        if message.content.lower() == "confirm" or message.content.lower() == "yes":
            pass
        else:
            return await ctx.send("Aborted.")

        items = await self.bot.items.find("items")
        items = items["items"]
        data = []
        message = await ctx.send(f"Resetting **{user.name}'s** data... <a:loading:733746914109161542>")
        item = items["shoppingcart"]
        del item["emoji"], item["value"], item["description"], item["rarity"]
        item["locked"] = False
        item["quantity"] = 1
        data.append(item)
        await self.bot.inventories.upsert({"_id": user.id, "balance": 100})
        await self.bot.inventories.upsert({"_id": user.id, "bankbalance": 0})
        await self.bot.inventories.upsert({"_id": user.id, "banklimit": 0})
        await self.bot.inventories.upsert({"_id": user.id, "job": None})
        await self.bot.inventories.upsert({"_id": user.id, "inventory": data})
        await message.edit(content=f"Resetting **{user.name}'s** data... **Done!**")

    @resetdata.error
    async def resetdata_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}reset (user)`")


def setup(bot):
    bot.add_cog(Admin(bot))
