import discord, platform, datetime, logging
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

        item = items[item]
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

def setup(bot):
    bot.add_cog(Trading(bot))
