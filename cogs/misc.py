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

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def welcome(self, ctx):
        welcomebed = discord.Embed(
            title="Thank you for inviting me!",
            description=f"A few things about myself: \n \nMy prefix is `{self.bot.prefix}`\nYou can find help by doing `{self.bot.prefix}help`\nYou can join the support server by doing `{self.bot.prefix}invite`\nTo start your epic adventure, do `{self.bot.prefix}inv`\nTo view this message again, do `{self.bot.prefix}welcome`",
            color=discord.Color.green()
        )
        welcomebed.set_thumbnail(url=self.bot.user.avatar_url)
        return await ctx.send(embed=welcomebed)

    @commands.command()
    async def cooldowns(self, ctx, section=None):
        if section is None:
            cooldowns = discord.Embed(title=":herb: Lyfé Cooldowns List", color=discord.Color.purple())
            cooldowns.add_field(name=":page_facing_up: Inventory", value=f"`{self.bot.prefix}cooldowns inventory`", inline=False)
            cooldowns.add_field(name=":credit_card: Economy", value=f"`{self.bot.prefix}cooldowns economy`", inline=False)
            cooldowns.add_field(name=":bust_in_silhouette: Profiles", value=f"`{self.bot.prefix}cooldowns profiles`", inline=False)
            cooldowns.add_field(name=":moneybag: Crime", value=f"`{self.bot.prefix}cooldowns crime`", inline=False)
            cooldowns.add_field(name=":card_box: Jobs", value=f"`{self.bot.prefix}cooldowns jobs`", inline=False)
            cooldowns.add_field(name=":scales: Trading", value=f"`{self.bot.prefix}cooldowns trading`", inline=False)
            cooldowns.add_field(name=":microscope: Research", value=f"`{self.bot.prefix}cooldowns research`", inline=False)
            cooldowns.add_field(name=":game_die: Misc", value=f"`{self.bot.prefix}cooldowns misc`", inline=False)
            cooldowns.add_field(name=":medal: Leaderboards", value=f"`{self.bot.prefix}cooldowns leaderboards`", inline=False)
            cooldowns.add_field(name=":robot: Bot", value=f"`{self.bot.prefix}cooldowns bot`", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "inventory":
            cooldowns = discord.Embed(title=":page_facing_up: Inventory Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            cooldowns.set_footer(text="Inventory cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}inv [page]/[user] [page]`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}claim`", value="1 Hour Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}daily`", value="Daily Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}lock (item)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}unlock (item)`", value="No cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "economy":
            cooldowns = discord.Embed(title=":credit_card: Economy Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            cooldowns.set_footer(text="Economy cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}balance [user]`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}gamble`", value="20 times every hour", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}shop`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}buy`", value="2 times every 5 seconds", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}sell`", value="2 times every 5 seconds", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}give (user) (item)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}pay (user) (amount)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}pshop`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}pshop show (user)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}pshop buy (user) (item)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}pshop add (item) (price) [quantity]`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}pshop remove (item) [quantity]`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}banks`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}bank (bank slot)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}deposit (amount)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}withdraw (amoint)`", value="No cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "profiles" or section.lower() == "profile":
            cooldowns = discord.Embed(title=":bust_in_silhouette: Profile Commands", color=discord.Color.purple())
            cooldowns.set_footer(text="Profile cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}profile [user]`", value="3 Second Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}titles`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}title set [title]`", value="No cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "crime" or section.lower() == "robbery":
            cooldowns = discord.Embed(title=":moneybag: Crime Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            cooldowns.set_footer(text="Crime cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}rob (user) (tool) (desired item)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}steal (user) (amount)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}dynamite (user)`", value="15 Minute Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}bomb (user)`", value="15 Minute Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}burn (user) (item)`", value="15 Minute Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}axe (user)`", value="15 Minute Cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "jobs":
            cooldowns = discord.Embed(title=":card_box: Job Commands", color=discord.Color.purple())
            cooldowns.set_footer(text="Job cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}jobs`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}apply (job)`", value="You can run this command every day", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}work`", value=f"Depends on the job type. Do {self.bot.prefix}jobs", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}resign`", value="You can run this command every day", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}beg`", value="No cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "trading":
            cooldowns = discord.Embed(title=":scales: Trading Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            cooldowns.set_footer(text="Trading cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}trade (user) (owned item) (desired item)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}taccept (tradeid)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}tcancel (tradeid)`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}give (user) (item) [quantity]`", value="No cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "research":
            cooldowns = discord.Embed(title=":microscope: Research Commands", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            cooldowns.set_footer(text="Research cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}iteminfo (item)`", value="3 Second Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}find (item)`", value="1 Minute Cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "misc":
            cooldowns = discord.Embed(title=":game_die: Misc Commands", color=discord.Color.purple())
            cooldowns.set_footer(text="Misc cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}feed`", value="No Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}avatar [user]`", value="No Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}8ball (question)`", value="No Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}cookie (user)`", value="15 Minute Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}flower (user)`", value="15 Minute Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}cooldowns (category)`", value="No cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "leaderboards" or section.lower() == "leaders":
            cooldowns = discord.Embed(title=":medal: Leaderboards", description="**Note:** Items in these commands don't contain spaces", color=discord.Color.purple())
            cooldowns.set_footer(text="Leaderboards cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}leaderboard`", value="3 Second Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}baltop`", value="3 Second Cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}frogtop`", value="3 Second Cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

        elif section.lower() == "bot":
            cooldowns = discord.Embed(title=":robot: Bot", color=discord.Color.purple())
            cooldowns.set_footer(text="Bot cooldowns list")
            cooldowns.add_field(name=f"`{self.bot.prefix}info`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}diagnose`", value="No cooldown", inline=False)
            cooldowns.add_field(name=f"`{self.bot.prefix}ping`", value="No cooldown", inline=False)
            return await ctx.send(embed=cooldowns)

def setup(bot):
    bot.add_cog(Misc(bot))
