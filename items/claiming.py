import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Claiming(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Claiming Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- CLAIM --------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def claim(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        inventory = data["inventory"]
        items = await self.bot.items.find("items")
        items = items["items"]

        rand = random.randint(1, len(items) - 1)

        c = 0
        confirm = False
        for item in items:
            item = items[item]
            c += 1
            if c == rand:
                daily = item
                confirm = True
                break

        if not confirm:
            return await ctx.send("Something went wrong.")

        name, emoji = daily["name"], daily["emoji"]

        given = False
        for i in inventory:
            if i["name"] == name:
                i["quantity"] += 1
                given = True

        if not given:
            del daily["emoji"], daily["value"], daily["description"]
            daily["locked"] = False
            daily["quantity"] = 1
            inventory.append(daily)

        await ctx.send(f":mailbox_with_mail: You got **{emoji} {name}**.")
        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})

    # ----- ERROR HANDLER ------------------------------------------------------

    @claim.error
    async def claim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f':mailbox_with_no_mail: You must wait **{int(s)} seconds** to claim again.')
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(f':mailbox_with_no_mail: You must wait **{int(m)} minutes and {int(s)} seconds** to claim again.')
            else:
                await ctx.send(f':mailbox_with_no_mail: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to claim again.')
            return

def setup(bot):
    bot.add_cog(Claiming(bot))