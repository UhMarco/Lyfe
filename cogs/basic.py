import discord, platform, datetime, logging
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        data = utils.json.read_json("blacklist")
        for item in data["blacklistedUsers"]:
            self.bot.blacklisted_users.append(item)
        print("- Basic Cog loaded")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- BLACKLIST ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, member: discord.Member):
        if ctx.message.author.id == member.id:
            return await ctx.send("You can't blacklist yourself.")

        data = utils.json.read_json("blacklist")

        if member.id in data["blacklistedUsers"]:
            return await ctx.send("This user is already blacklisted.")

        data["blacklistedUsers"].append(member.id)
        self.bot.blacklisted_users.append(member.id)
        utils.json.write_json(data, "blacklist")
        await ctx.send(f"Blacklisted **{member.name}**.")

    # ----- ERROR HANDLER ------------------------------------------------------

    @blacklist.error
    async def blacklist_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}blacklist (user)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- UNBLACKLIST --------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, member: discord.Member):
        data = utils.json.read_json("blacklist")

        if member.id not in data["blacklistedUsers"]:
            return await ctx.send("That user isn't blacklisted.")

        data["blacklistedUsers"].remove(member.id)
        self.bot.blacklisted_users.remove(member.id)
        utils.json.write_json(data, "blacklist")
        await ctx.send(f"Unblacklisted **{member.name}**.")

    # ----- ERROR HANDLER ------------------------------------------------------

    @unblacklist.error
    async def unblacklist_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Usage: `.unblacklist (user)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- LOGOUT -------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['disconnect', 'stop', 's'])
    @commands.is_owner()
    async def logout(self, ctx):
        if self.bot.maintenancemode:
            return
        await ctx.send("Stopping.")
        await self.bot.logout()

def setup(bot):
    bot.add_cog(Basic(bot))
