import discord, platform, logging, random, os, time, asyncio
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate

def is_dev():
    def predictate(ctx):
        devs = utils.json.read_json("devs")
        if ctx.author.id in devs:
            return ctx.author.id
    return commands.check(predictate)

class Profiles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Profiles Cog loaded")

    @commands.command()
    @is_dev()
    async def pfsetup(self, ctx):
        await ctx.send("Please confirm.")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        message = await self.bot.wait_for('message', check=check)
        if message.content.lower() == "confirm" or message.content.lower() == "yes":
            pass
        else:
            return await ctx.send("Aborted.")

        msg = await ctx.send(embed=discord.Embed(title="Loading <a:loading:733746914109161542>"))
        data = await self.bot.inventories.get_all()
        for i in data:
            try:
                del i["beta"]
            except KeyError:
                pass
            i["titles"] = ['✪ Beta Player']
            await self.bot.inventories.delete(ctx.author.id)
            await self.bot.inventories.upsert({"_id": i["_id"], "balance": i["balance"]})
            await self.bot.inventories.upsert({"_id": i["_id"], "bankbalance": i["bankbalance"]})
            await self.bot.inventories.upsert({"_id": i["_id"], "banklimit": i["banklimit"]})
            await self.bot.inventories.upsert({"_id": i["_id"], "job": i["job"]})
            await self.bot.inventories.upsert({"_id": i["_id"], "inventory": i["inventory"]})
            await self.bot.inventories.upsert({"_id": i["_id"], "titles": i["titles"]})
        await msg.edit(embed=discord.Embed(title="Done."))

    @commands.command(aliases=['title'])
    async def titles(self, ctx, arg=None, title=None):
        data = await self.bot.inventories.find(ctx.author.id)
        titles = data["titles"]
        if arg is None:
            message = []
            n = '\n'
            for i in titles:
                message.append(i)
            embed = discord.Embed(title=f"**{ctx.author.name}**'s titles:", description=n.join(message))
            await ctx.send(embed=embed)

        elif arg.lower() == "set":
            if title is None:
                return await ctx.send("no title spec.")
            index = 0
            found = False

            if title == "mod" or title == "moderator":
                title = "✦ Moderator"
            elif title == "dev" or title == "developer":
                title = "✚ Developer"
            elif "beta" in title:
                title = "✪ Beta Player"
            else:
                return await ctx.send("Not a valid title.")

            for i in titles:
                if title == i:
                    index = titles.index(i)
                    found = True

            if not found:
                return await ctx.send("not found")

            titles[index], titles[0] = titles[0], titles[index]
            await ctx.send(f"Title set to {titles[0]}")
            await self.bot.inventories.upsert({"_id": ctx.author.id, "titles": titles})

    @commands.command()
    @is_dev()
    async def addtitle(self, ctx, user, title):
        if len(ctx.message.mentions) == 0:
            if user is None:
                page = 1
                user = ctx.author
            else:
                try:
                    if self.bot.get_user(int(user)) == None:
                        return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
                    else:
                        user = self.bot.get_user(int(user))
                except ValueError:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        title.lower()
        data = await self.bot.inventories.find(user.id)
        titles = data["titles"]

        if title == "mod" or title == "moderator":
            titles.append("✦ Moderator")
        elif title == "dev" or title == "developer":
            titles.append("✚ Developer")
        elif "beta" in title:
            titles.append("✪ Beta Player")
        else:
            return await ctx.send("Not a valid title.")

        await self.bot.inventories.upsert({"_id": user.id, "titles": titles})
        await ctx.send("Added")

    @addtitle.error
    async def addtitle_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}addtitle (user) (title)`")


    @commands.command()
    @is_dev()
    async def removetitle(self, ctx, user, title):
        if len(ctx.message.mentions) == 0:
            if user is None:
                page = 1
                user = ctx.author
            else:
                try:
                    if self.bot.get_user(int(user)) == None:
                        return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
                    else:
                        user = self.bot.get_user(int(user))
                except ValueError:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        title.lower()
        data = await self.bot.inventories.find(user.id)
        titles = data["titles"]

        if title == "mod" or title == "moderator":
            title = "✦ Moderator"
        elif title == "dev" or title == "developer":
            title = "✚ Developer"
        elif "beta" in title:
            title = "✪ Beta Player"
        else:
            return await ctx.send("Not a valid title.")

        for i in titles:
            if i == title:
                titles.remove(i)

        await ctx.send("Done")
        await self.bot.inventories.upsert({"_id": user.id, "titles": titles})

    @removetitle.error
    async def removetitle_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}removetitle (user) (title)`")


def setup(bot):
    bot.add_cog(Profiles(bot))
