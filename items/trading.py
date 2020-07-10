import discord, platform, datetime, logging, random, asyncio
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Trading(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Trading Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- GIVE ---------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['donate'])
    async def give(self, ctx, user: discord.Member, item):
        mydata = await self.bot.inventories.find(ctx.author.id)
        if mydata is None:
            return await ctx.send("You haven't initialized your inventory yet.")
        myinventory = mydata["inventory"]

        items = await self.bot.items.find("items")
        items = items["items"]

        yourdata = await self.bot.inventories.find(user.id)
        if yourdata is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")
        yourinventory = yourdata["inventory"]

        if user.id == ctx.author.id:
            return await ctx.send("That's pointless.")

        if item.lower() not in items:
            return await ctx.send("That item does not exist.")
        item = items[item.lower()]
        name, emoji = item["name"], item["emoji"]

        found = False
        for i in myinventory:
            if i["name"] == name:
                if i["locked"]:
                    return await ctx.send(f"**{emoji} {name}** is locked in your inventory.")

                if i["quantity"] == 1:
                    myinventory.remove(i)
                else:
                    i["quantity"] -= 1

                found = True
                break

        if not found:
            return await ctx.send(f"You don't own a **{emoji} {name}**.")

        given = False
        for i in yourinventory:
            if i["name"] == name:
                i["quantity"] += 1
                given = True

        if not given:
            del item["emoji"], item["value"], item["description"]
            item["locked"] = False
            item["quantity"] = 1
            yourinventory.append(item)

        await ctx.send(f"**{emoji} {name}** transferred from **{ctx.author.name}** to **{user.name}**.")
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": myinventory})
        await self.bot.inventories.upsert({"_id": user.id, "inventory": yourinventory})

    # ----- ERROR HANDLER ------------------------------------------------------

    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}give (user) (item)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- TRADE --------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def trade(self, ctx, user: discord.Member, item1, item2):
        mydata = await self.bot.inventories.find(ctx.author.id)
        if mydata is None:
            return await ctx.send("You haven't initialized your inventory yet.")
        myinventory = mydata["inventory"]

        items = await self.bot.items.find("items")
        items = items["items"]

        yourdata = await self.bot.inventories.find(user.id)
        if yourdata is None:
            return await ctx.send("This user hasn't initialized their inventory yet.")
        yourinventory = yourdata["inventory"]

        if user.id == ctx.author.id or item1 == item2:
            return await ctx.send("That's pointless.")

        if item1.lower() not in items:
            return await ctx.send("That item does not exist.")
        if item2.lower() not in items:
            return await ctx.send("That item does not exist.")

        item1 = items[item1.lower()]
        name1, emoji1 = item1["name"], item1["emoji"]
        item2 = items[item2.lower()]
        name2, emoji2 = item2["name"], item2["emoji"]
        myinventory = mydata["inventory"]
        yourinventory = yourdata["inventory"]

        found = False
        for i in myinventory:
            if i["name"] == name1:
                if i["locked"]:
                    return await ctx.send(f"**{emoji1} {name1}** is locked in your inventory.")
                found = True
        if not found:
            return await ctx.send(f"You don't have a **{emoji1} {name1}** in your inventory.")

        found = False
        for i in yourinventory:
            if i["name"] == name2:
                if i["locked"]:
                    return await ctx.send(f"**{emoji2} {name2}** is locked in {user.name}'s inventory.")
                found = True
        if not found:
            return await ctx.send(f"{user.name} doesn't have a **{emoji2} {name2}** in their inventory.")

        created = False
        while not created:
            tradeid = random.randint(100, 999)
            trade = await self.bot.trades.find(tradeid)
            if trade is None:
                created = True

        dict = {}
        offered = item1["name"].replace(" ", "").lower()
        desired = item2["name"].replace(" ", "").lower()
        dict["offerer"], dict["offereditem"], dict["desireditem"], dict["receiver"], dict["completed"] = ctx.author.id, offered, desired, user.id, False
        await self.bot.trades.upsert({"_id": tradeid, "trade": dict})

        embed = discord.Embed(
                    title=f"Trade Request for **{user.name}** from **{ctx.author.name}**",
                    description=f"TradeID: `{tradeid}`\n\n**Offering: {emoji1} {name1}**\n**For: {emoji2} {name2}**\n\nTo accept: `{self.bot.prefix}tradeaccept {tradeid}`",
                    color=discord.Color.gold()
                )
        await ctx.send(embed=embed)

    # ----- ERROR HANDLER ------------------------------------------------------

    @trade.error
    async def trade_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}trade (user) (owened item) (desired item)`")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- TRADE --------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['accepttrade'])
    async def tradeaccept(self, ctx, tradeid):
        trade = await self.bot.trades.find(int(tradeid))

        if trade is None:
            return await ctx.send("That is not a valid TradeID.")

        trade = trade["trade"]
        if trade["completed"]:
            return await ctx.send("Trade has already been completed or it was cancelled by the offerer.")

        items = await self.bot.items.find("items")
        items = items["items"]

        if ctx.author.id != trade["receiver"]:
            return await ctx.send("This trade isn't meant for you.")

        offererid = trade["offerer"]
        try:
            offerer = self.bot.get_user(offererid)
        except Exception:
            trade["completed"] = True
            await self.bot.trades.upsert({"_id": int(tradeid), "trade": trade})
            return await ctx.send("Something went wrong when trying to find offerer, cancelling trade...")

        rdata = await self.bot.inventories.find(ctx.author.id)
        if rdata is None:
            trade["completed"] = True
            await self.bot.trades.upsert({"_id": int(tradeid), "trade": trade})
            return await ctx.send("Database error")
        rinventory = rdata["inventory"]

        odata = await self.bot.inventories.find(offererid)
        if odata is None:
            trade["completed"] = True
            await self.bot.trades.upsert({"_id": int(tradeid), "trade": trade})
            return await ctx.send("Database error")
        oinventory = odata["inventory"]

        oitem = items[trade["offereditem"]]
        oname, oemoji = oitem["name"], oitem["emoji"]
        ditem = items[trade["desireditem"]]
        dname, demoji = ditem["name"], ditem["emoji"]

        found = False
        for i in oinventory:
            if i["name"] == oname:
                if i["locked"]:
                    trade["completed"] = True
                    await self.bot.trades.upsert({"_id": int(tradeid), "trade": trade})
                    return await ctx.send(f"**{oemoji} {oname}** has been locked in their inventory.")
                elif i["quantity"] != 1:
                    i["quantity"] -= 1
                else:
                    oinventory.remove(i)
                found = True
        if not found:
            trade["completed"] = True
            await self.bot.trades.upsert({"_id": int(tradeid), "trade": trade})
            return await ctx.send(f"Trader doesn't have **{oemoji} {oname}** anymore.")

        found = False
        for i in rinventory:
            if i["name"] == dname:
                if i["locked"]:
                    trade["completed"] = True
                    await self.bot.trades.upsert({"_id": int(tradeid), "trade": trade})
                    return await ctx.send(f"**{demoji} {dname}** has been locked in your inventory.")
                elif i["quantity"] != 1:
                    i["quantity"] -= 1
                else:
                    rinventory.remove(i)
                found = True
        if not found:
            trade["completed"] = True
            await self.bot.trades.upsert({"_id": int(tradeid), "trade": trade})
            return await ctx.send(f"You don't have a **{demoji} {dname}** anymore.")

        # Give ditem to oinventory
        item = items[dname.replace(" ", "").lower()]
        given = False
        for i in oinventory:
            if i["name"] == dname:
                i["quantity"] += 1
                given = True

        if not given:
            del item["emoji"], item["value"]
            item["locked"] = False
            item["quantity"] = 1
            oinventory.append(item)

        # Give oitem to rinventory
        item = items[oname.replace(" ", "").lower()]
        given = False
        for i in rinventory:
            if i["name"] == oitem:
                i["quantity"] += 1
                given = True

        if not given:
            del item["emoji"], item["value"]
            item["locked"] = False
            item["quantity"] = 1
            rinventory.append(item)

        await self.bot.inventories.upsert({"_id": offererid, "inventory": oinventory})
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": rinventory})
        trade["completed"] = True
        await self.bot.trades.upsert({"_id": int(tradeid), "trade": trade})
        embed = discord.Embed(
            title=f"Trade {tradeid} Accepted",
            description=f"**{ctx.author.name}** gained **{oemoji} {oname}** from **{offerer.name}**\n**{offerer.name}** gained **{demoji} {dname}** from **{ctx.author.name}**",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Trading(bot))
