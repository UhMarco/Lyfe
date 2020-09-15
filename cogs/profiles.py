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

    @commands.command(aliases=['title'])
    async def titles(self, ctx, arg=None, title=None):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")
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
                title = "》Moderator"
            elif title == "dev" or title == "developer":
                title = "✦ Developer"
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
            titles.append("》Moderator")
        elif title == "dev" or title == "developer":
            titles.append("✦ Developer")
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
            title = "》Moderator"
        elif title == "dev" or title == "developer":
            title = "✦ Developer"
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


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def profile(self, ctx, user=None):
        if len(ctx.message.mentions) == 0:
            if user is None:
                user = ctx.author
            else:
                try:
                    if self.bot.get_user(int(user)) == None:
                        user = ctx.author
                    else:
                        user = self.bot.get_user(int(user))
                except ValueError:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        data = await self.bot.inventories.find(user.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        items = await self.bot.items.find("items")
        items = items["items"]

        description = []
        # Profile title
        title = f"{user.name}'s Profile"
        # Custom title
        color = discord.Color.green()
        try:
            insert = data["titles"][0]
            description.append(f"**{insert}**")
            if "beta" in insert.lower():
                color = discord.Color.dark_green()
            elif "mod" in insert.lower():
                color = discord.Color.red()
            else:
                color = discord.Color.red()
        except IndexError:
            description.append("**Player**")
        # Leaderboard position
        all = await self.bot.inventories.get_all()
        lb = []
        for i in all:
            inv = i["inventory"]
            value = 0
            for x in inv:
                value += x["quantity"] * items[x["name"].replace(" ", "").lower()]["value"]
            total = i["balance"] + i["bankbalance"] + value
            lb.append({"id": i['_id'], "total": total})

        sort = sorted(lb, key=lambda k: k['total'], reverse=True)
        count, lbpos = 0, 0
        for i in sort:
            count += 1
            if i["id"] == user.id:
                description.append(f"**#{count}** in leaderboard")
                break

        # Total inventory value
        inventory = data["inventory"]
        value = 0
        for i in inventory:
            value += i["quantity"] * items[i["name"].replace(" ", "").lower()]["value"]
        description.append("Inventory value of $`{:,}`".format(value))

        # Highest value item
        highest_item = None
        highest_emoji = None
        highest_value = 0
        for i in inventory:
            item = items[i["name"].replace(" ", "").lower()]
            val = item["value"]
            if val > highest_value:
                highest_value = val
                highest_item = item["name"]
                highest_emoji = item["emoji"]

        description.append(f"Best item is {highest_emoji} **{highest_item}**")

        n = '\n'
        embed = discord.Embed(title=title, description=n.join(description), color=color)
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Profiles(bot))
