import discord, platform, datetime, logging, os
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

        try:
            data = utils.json.read_json("whitelist")
            for item in data["whitelist"]:
                self.bot.whitelisted.append(item)
        except Exception:
            pass

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
            return await ctx.send(f"Usage: `{self.bot.prefix}unblacklist (user)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- WHITELIST ----------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def whitelist(self, ctx, member: discord.Member):
        data = utils.json.read_json("whitelist")

        if member.id in data["whitelist"]:
            return await ctx.send("This user is already whitelisted.")

        data["whitelist"].append(member.id)
        self.bot.whitelisted.append(member.id)
        utils.json.write_json(data, "whitelist")
        await ctx.send(f"Whitelisted **{member.name}**.")

    # ----- ERROR HANDLER ------------------------------------------------------

    @whitelist.error
    async def whitelist_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}whitelist (user)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- UNWHITELIST --------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def unwhitelist(self, ctx, member: discord.Member):
        data = utils.json.read_json("whitelist")

        if member.id not in data["whitelist"]:
            return await ctx.send("That user isn't whitelisted.")

        data["whitelist"].remove(member.id)
        self.bot.whitelisted.remove(member.id)
        utils.json.write_json(data, "whitelist")
        await ctx.send(f"Unwhitelist **{member.name}**.")

    # ----- ERROR HANDLER ------------------------------------------------------

    @unwhitelist.error
    async def unwhitelist_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}whitelist (user)`")

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- LOGOUT -------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['disconnect', 'stop', 's'])
    @commands.is_owner()
    async def logout(self, ctx):
        if self.bot.maintenancemode:
            return

        await ctx.send("Please confirm.")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        message = await self.bot.wait_for('message', check=check)
        if message.content.lower() == "confirm" or message.content.lower() == "yes":
            pass
        else:
            return await ctx.send("Aborted.")

        await ctx.send("Stopping.")
        await self.bot.logout()

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- DIAGNOSE ------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command(aliases=['diagnosis'])
    async def diagnose(self, ctx):
        modules = []
        items = []
        message = "\n"
        count = 0
        icount = 0

        for file in os.listdir(cwd+"/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                done = False
                try:
                    self.bot.load_extension(f"cogs.{file[:-3]}")
                    self.bot.unload_extension(f"cogs.{file[:-3]}")
                except commands.ExtensionAlreadyLoaded:
                    name = file[:-3]
                    name = f"`✔ {name[:1].upper()}{name[1:]}`"
                    modules.append(name)
                    count += 1
                    done = True

                if not done:
                    name = file[:-3]
                    name = f"`✘ {name[:1].upper()}{name[1:]}`"
                    modules.append(name)


        for file in os.listdir(cwd+"/items"):
            if file.endswith(".py") and not file.startswith("_"):
                done = False
                try:
                    self.bot.load_extension(f"items.{file[:-3]}")
                    self.bot.unload_extension(f"items.{file[:-3]}")
                except commands.ExtensionAlreadyLoaded:
                    name = file[:-3]
                    name = f"`✔ {name[:1].upper()}{name[1:]}`"
                    items.append(name)
                    icount += 1
                    done = True

                if not done:
                    name = file[:-3]
                    name = f"`✘ {name[:1].upper()}{name[1:]}`"
                    items.append(name)

        embed = discord.Embed(title="Diagnosis", description=f"**Extensions:**\n{message.join(modules)}\n**Modules:**\n{message.join(items)}\n**Errors since startup:** `{self.bot.important_errors}/{self.bot.errors}`", color=discord.Color.blue())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Basic(bot))
