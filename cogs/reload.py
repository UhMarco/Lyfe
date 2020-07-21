import discord, platform, asyncio, os, time
from discord.ext import commands
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Reload(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Reload Cog loaded")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, module):
        if self.bot.maintenancemode:
            return

        try:
            self.bot.load_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been loaded.")
        except Exception as e:
            files =  os.listdir(cwd+"/items")
            check = str(e).split("'")
            check = check[1].replace("cogs.", "")
            if any(ele in f"{check}.py" for ele in files):
                pass
            else:
                return await ctx.send(e)

        try:
            self.bot.load_extension(f"items.{module.lower()}")
            name = module.lower()
            await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been loaded.")
        except Exception as e:
            await ctx.send(e)

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}load (module)`")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, module):
        if self.bot.maintenancemode:
            return
        if module == "all":
            start = time.time()
            for file in os.listdir(cwd+"/cogs"):
                if file.endswith(".py") and not file.startswith("_"):
                    self.bot.reload_extension(f"cogs.{file[:-3]}")
                    name = file[:-3].lower()

            for file in os.listdir(cwd+"/items"):
                if file.endswith(".py") and not file.startswith("_"):
                    self.bot.reload_extension(f"items.{file[:-3]}")
                    name = file[:-3].lower()

            end = time.time()
            return await ctx.send("Operation took: `{:.5f}` seconds".format(end - start))

        try:
            self.bot.reload_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been reloaded.")
        except Exception as e:
            files =  os.listdir(cwd+"/items")
            check = str(e).split("'")
            check = check[1].replace("cogs.", "")
            if any(ele in f"{check}.py" for ele in files):
                pass
            else:
                return await ctx.send(e)

        try:
            self.bot.reload_extension(f"items.{module.lower()}")
            name = module.lower()
            await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been reloaded.")
        except Exception as e:
            await ctx.send(e)

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}reload (module/all)`")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, module):
        if self.bot.maintenancemode:
            return
        if module.lower() == "reload":
            return await ctx.send("That's not a good idea...")

        try:
            self.bot.unload_extension(f"cogs.{module.lower()}")
            name = module.lower()
            return await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been unloaded.")
        except Exception as e:
            files =  os.listdir(cwd+"/items")
            check = str(e).split("'")
            check = check[1].replace("cogs.", "")
            if any(ele in f"{check}.py" for ele in files):
                pass
            else:
                return await ctx.send(e)

        try:
            self.bot.unload_extension(f"items.{module.lower()}")
            name = module.lower()
            await ctx.send(f"**{name[:1].upper()}{name[1:]}** has been unloaded.")
        except Exception as e:
            await ctx.send(e)

    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}unload (module)`")

    @commands.command()
    @commands.is_owner()
    async def maintenance(self, ctx):
        self.bot.maintenancemode = not self.bot.maintenancemode
        await ctx.send(f"Maintenance-Mode set to **{self.bot.maintenancemode}**.")

#if __name__ == '__main__':
#    for file in os.listdir(cwd+"/cogs"):
#        if file.endswith(".py") and not file.startswith("_"):
#            bot.load_extension(f"cogs.{file[:-3]}")


def setup(bot):
    bot.add_cog(Reload(bot))
