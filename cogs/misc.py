import discord, platform, logging, random, os, time, asyncio
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate
from datetime import datetime, timedelta

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Misc Cog loaded")

    @commands.command()
    async def avatar(self, ctx, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        embed = discord.Embed(title=f"**{user.name}'s** Avatar", color=discord.Color.dark_blue())
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title=f"**{ctx.author.name}'s** Avatar", color=discord.Color.dark_blue())
            embed.set_image(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def _8Ball(self, ctx, *, question=None):
        if not question:
            return await ctx.send(":8ball: **8Ball:** Well that's cool but you actually have to ask something.")
        responses = ["Outlook unclear, try again later", "Sorry m8, try again", "mhm", "I don't know, you tell me", "lol", "Absolutely!", "Absolutely not!", "It's a yes from me", "It's a no from me", "Do what Jesus would do", "Nahhhh", "Sure I guess...", "It's plausible", "I don't think you'll like the answer...", "I think it's best I spare you of the truth."]
        wisdom = random.choice(responses)
        await ctx.send(f":8ball: **8Ball:** {wisdom}")

    @commands.command()
    async def feed(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        inventory = data["inventory"]

        found = False
        for i in inventory:
            if i["name"] == "Dragon":
                found = True

        if not found:
            return await ctx.send("You don't have a :dragon: **Dragon** in your inventory.")

        found = False
        for i in inventory:
            if i["name"] == "Frog":
                found = True
                if i["quantity"] == 1:
                    inventory.remove(i)
                else:
                    i["quantity"] -= 1

        if not found:
            return await ctx.send("You don't have a :frog: **Frog** in your inventory.")

        if random.randint(0, 100) != 50:
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            return await ctx.send("You fed a :frog: **Frog** to your :dragon: **Dragon**.")

        embed = discord.Embed(title=":tada: Your :dragon: **Dragon** evolved into an <:reddragon:733766679036952646> **Evolved Dragon**", description="The chances of this event occuring are 1% - Well done!", color=discord.Color.green())
        await ctx.send(embed=embed)

        locked = False

        for i in inventory:
            if i["name"] == "Dragon":
                if ["locked"]:
                    locked = True
                if i["quantity"] == 1:
                    inventory.remove(i)
                else:
                    i["quantity"] -= 1

        items = await self.bot.items.find("items")
        items = items["items"]
        item = items["evolveddragon"]

        name, emoji = item["name"], item["emoji"]

        given = False
        for i in inventory:
            if i["name"] == name:
                i["quantity"] += 1
                given = True

        if not given:
            del item["emoji"], item["value"], item["description"], item["rarity"]
            item["locked"] = locked
            item["quantity"] = 1
            inventory.append(item)

        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})

    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def cookie(self, ctx, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id")
        else:
            user = ctx.message.mentions[0]

        if user.id == ctx.author.id:
            return await ctx.send("You gave yourself a :cookie: **Cookie**!")

        await ctx.send(f"You gave **{user.name}** a :cookie: **Cookie**!")
        try:
            await user.send(f"**{ctx.author}** gave you a :cookie: **Cookie** from the server: {ctx.author.guild}")
        except discord.Forbidden:
            pass

    @cookie.error
    async def cookie_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Usage: `{self.bot.prefix}cookie (user)`")

    @commands.command()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def flower(self, ctx, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    ctx.command.reset_cooldown(ctx)
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                ctx.command.reset_cooldown(ctx)
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        if user.id == ctx.author.id:
            return await ctx.send(f"You gave yourself a :rose: **Flower**!")

        await ctx.send(f"You gave **{user.name}** a :rose: **Flower**!")
        try:
            await user.send(f"**{ctx.author}** gave you a :rose: **Rose** from the server: {ctx.author.guild}")
        except discord.Forbidden:
            pass

    @flower.error
    async def flower_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Usage: `{self.bot.prefix}flower (user)`")

def setup(bot):
    bot.add_cog(Misc(bot))
