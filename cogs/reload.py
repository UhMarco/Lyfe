import discord, os, time, asyncio, utils.json, utils.functions
from discord.ext import commands
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
from classes.user import User
from classes.phrases import Phrases
phrases = Phrases()

def is_dev():
    def predictate(ctx):
        devs = utils.json.read_json("devs")
        if ctx.author.id in devs:
            return ctx.author.id
    return commands.check(predictate)

class Reload(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Reload Cog loaded")

    @commands.command()
    @is_dev()
    async def load(self, ctx, module):
        if self.bot.maintenancemode:
            return

        try:
            self.bot.load_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been loaded.")
        except Exception as e:
            return await ctx.send(e)

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}load (module)`")


    @commands.command()
    @is_dev()
    async def reload(self, ctx, module):
        if self.bot.maintenancemode:
            return
        if module == "all":
            start = time.time()
            for file in os.listdir(cwd+"/cogs"):
                if file.endswith(".py") and not file.startswith("_"):
                    self.bot.reload_extension(f"cogs.{file[:-3]}")
                    name = file[:-3].lower()

            end = time.time()
            return await ctx.send("Operation took: `{:.5f}` seconds".format(end - start))
        try:
            self.bot.reload_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been reloaded.")
        except Exception as e:
            return await ctx.send(e)

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}reload (module/all)`")


    @commands.command()
    @is_dev()
    async def unload(self, ctx, module):
        if self.bot.maintenancemode:
            return
        if module.lower() == "admin":
            return await ctx.send("That's not a good idea...")

        try:
            self.bot.unload_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been unloaded.")
        except Exception as e:
            return await ctx.send(e)

    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}unload (module)`")

def setup(bot):
    bot.add_cog(Reload(bot))
