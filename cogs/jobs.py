import discord, platform, logging, random, os, time, asyncio
from discord.ext import commands
import platform
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate
from datetime import datetime, timedelta

def is_dev():
    def predictate(ctx):
        devs = utils.json.read_json("devs")
        if any(ctx.author.id for ele in devs):
            return ctx.author.id
    return commands.check(predictate)

# Custom cooldown variables
on_cooldown = {}
last_command = {}
cooldown = {"fastfoodworker": 600, "janitor": 1800, "mage": 3600}

class Jobs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Jobs Cog loaded")

    @commands.command(aliases=['job'])
    async def jobs(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is not None:
            job = data["job"]
        else:
            job = "none"
        embed = discord.Embed(
            title=":card_box: **Jobs List**",
            description=f"**Current Job:** `{job}`\nEarn varying amounts of money every certain amount of time\nEach job is different so take your pick!\n**Note:** Every job requires an :card_index: **ID**",
            color=discord.Color.greyple(),
        )
        embed.add_field(name=":hamburger: Fast Food Worker", value=f"Just repeat the ice cream machine is broken and you'll do great\n**Earns:** $`20` every `10 minutes`\n`{self.bot.prefix}apply fast food worker`", inline=False)
        embed.add_field(name=":broom: Janitor", value=f"Make some floors shiny\n**Earns:** $`100` every `30 minutes`\n`{self.bot.prefix}apply janitor`", inline=False)
        embed.add_field(name=":mage: Mage", value=f"You'll encounter many weird words called spells\n**Earns:** $`150` every `1 hour`.\n`{self.bot.prefix}apply mage`", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def apply(self, ctx, *, job):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You haven't initialized your inventory yet.")
        check = data["job"]
        if check is not None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Please resign from your current job before applying elsewhere.")

        inventory = data["inventory"]
        found = False
        for i in inventory:
            if i["name"] == "ID":
                found = True

        if not found:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You need :card_index: **ID** to get a job.")

        job = job.replace(" ", "").lower()

        if "fastfood" in job or "worker" in job:
            embed = discord.Embed(title="You successfully became a :hamburger: **Fast Food Worker**", description="**Earns:** $`20` every `10 minutes`", color=discord.Color.greyple())
            await self.bot.inventories.upsert({"_id": ctx.author.id, "job": "fastfoodworker"})
            await ctx.send(embed=embed)

        elif job == "janitor":
            embed = discord.Embed(title="You successfully became a :broom: **Janitor**", description="**Earns:** $`100` every `1 hour`", color=discord.Color.greyple())
            await self.bot.inventories.upsert({"_id": ctx.author.id, "job": "janitor"})
            await ctx.send(embed=embed)

        elif job == "mage":
            embed = discord.Embed(title="You successfully became a :mage: **Mage**", description="**Earns:** $`150` every `45 minutes`", color=discord.Color.greyple())
            await self.bot.inventories.upsert({"_id": ctx.author.id, "job": "mage"})
            await ctx.send(embed=embed)

        else:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("That's not a job.")

    @apply.error
    async def apply_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"Usage: `{self.bot.prefix}apply (job)`")

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def resign(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You haven't initialized your inventory yet.")
        job = data["job"]
        if job is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("You're not currently employed anywhere.")

        await self.bot.inventories.upsert({"_id": ctx.author.id, "job": None})

        if job == "fastfoodworker":
            job = "Fast Food Worker"
            emoji = ":hamburger:"
        elif job == "janitor":
            job = "Janitor"
            emoji = ":broom:"
        elif job == "mage":
            job = "Mage"
            emoji = ":mage:"
        else:
            emoji = ":question:"

        author = ctx.author.id
        try:
            del last_command[author]
        except KeyError:
            pass

        embed = discord.Embed(title=f"You quit your job as a {emoji} **{job}**", color=discord.Color.greyple())
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def work(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")
        job = data["job"]
        if job is None:
            return await ctx.send(f"You're not currently employed anywhere. Do `{self.bot.prefix}jobs`")

        balance = data["balance"]

        author = ctx.author.id
        try:
            last_command[author] = datetime.now() - on_cooldown[author]
        except KeyError:
            last_command[author] = None
            on_cooldown[author] = datetime.now()

        if job == "fastfoodworker":
            localcooldown = cooldown["fastfoodworker"]

            if last_command[author] is None or last_command[author].seconds > localcooldown:
                on_cooldown[author] = datetime.now()
                job = "Fast Food Worker"
                emoji = ":hamburger:"
                pay = 20

                # WORK
                work = utils.json.read_json("fastfoodwork")
                word = random.choice(list(work))
                embed = discord.Embed(title=f"Name the emoji {word}", description="You will be rewarded double if you name it within 3 seconds.", color=discord.Color.greyple())
                await ctx.send(embed=embed)
                timer = time.time()

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author
                try:
                    message = await self.bot.wait_for('message', check=check, timeout=20)

                    words = work[word]
                    if any(ele in message.content.replace(" ", "").lower() for ele in words):
                        if time.time() - timer <= 3:
                            pay = int(pay * 2)
                            await ctx.send(f"**Correct!** You were paid $`{pay}` as you named the emoji within 3 seconds")
                        else:
                            await ctx.send(f"**Correct!** You were paid $`{pay}`")
                    else:
                        pay = int(pay * 0.8)
                        await ctx.send(f"**Incorrect!** The manager doesn't seem happy - You were only paid $`{pay}`")

                except asyncio.TimeoutError:
                    pay = int(pay * 0.8)
                    await ctx.send(f"**Disappointing!** You took too long - You were only paid $`{pay}`")

                # PAY
                balance += pay
                await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

            else:
                m, s = divmod(localcooldown - last_command[author].seconds, 60)
                h, m = divmod(m, 60)
                if int(h) == 0 and int(m) == 0:
                    await ctx.send(f':card_box: You must wait **{int(s)} seconds** to work again.')
                elif int(h) == 0 and int(m) != 0:
                    await ctx.send(f':card_box: You must wait **{int(m)} minutes and {int(s)} seconds** to work again.')
                else:
                    await ctx.send(f':card_box: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to work again.')
                return

        elif job == "janitor":
            localcooldown = cooldown["janitor"]

            if last_command[author] is None or last_command[author].seconds > localcooldown:
                on_cooldown[author] = datetime.now()
                job = "Janitor"
                emoji = ":broom:"
                pay = 100

                # WORK
                emojis = ['\ud83e\uddf9', '\ud83d\udca1', '\ud83e\uddfd', "\ud83e\uddfb", "\ud83e\uddfc", "\ud83e\uddef", "\ud83d\udeb0", "\ud83d\udebd", "\ud83d\udd11"]
                emoji = random.choice(emojis)
                embed = discord.Embed(title=f"Send a message containing this emoji: {emoji}", description="You will be paid 20% more if you do so within 5 seconds.", color=discord.Color.greyple())
                await ctx.send(embed=embed)
                timer = time.time()

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author
                try:
                    message = await self.bot.wait_for('message', check=check, timeout=20)

                    emoji = emoji.encode('utf-16','surrogatepass').decode('utf-16')

                    if emoji in message.content:
                        if time.time() - timer <= 5:
                            pay = int(pay * 1.2)
                            await ctx.send(f"**Correct!** You were paid $`{pay}`")
                        else:
                            await ctx.send(f"**Correct!** You were paid $`{pay}`")
                    else:
                        pay = int(pay * 0.8)
                        await ctx.send(f"**Incorrect!** Your boss looks angry - You were paid $`{pay}`")

                except asyncio.TimeoutError:
                    pay = int(pay * 0.8)
                    await ctx.send(f"**Disappointing!** You took too long - You were paid $`{pay}`")

                # PAY
                balance += pay
                await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

            else:
                m, s = divmod(localcooldown - last_command[author].seconds, 60)
                h, m = divmod(m, 60)
                if int(h) == 0 and int(m) == 0:
                    await ctx.send(f':card_box: You must wait **{int(s)} seconds** to work again.')
                elif int(h) == 0 and int(m) != 0:
                    await ctx.send(f':card_box: You must wait **{int(m)} minutes and {int(s)} seconds** to work again.')
                else:
                    await ctx.send(f':card_box: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to work again.')
                return

        elif job == "mage":
            localcooldown = cooldown["mage"]

            if last_command[author] is None or last_command[author].seconds > localcooldown:
                on_cooldown[author] = datetime.now()
                job = "Mage"
                emoji = ":mage:"
                pay = 150

                # WORK
                spells = utils.json.read_json("spells")
                spell = random.choice(spells["spells"])
                embed = discord.Embed(title=f"Type the spell `{spell}`", description="You will be rewarded 20% more if you spell it within 5 seconds.", color=discord.Color.greyple())
                await ctx.send(embed=embed)
                timer = time.time()

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author
                try:
                    message = await self.bot.wait_for('message', check=check, timeout=20)

                    if spell.replace(" ", "") in message.content.replace(" ", "").lower():
                        if time.time() - timer <= 5:
                            pay = int(pay * 1.2)
                            await ctx.send(f"**Correct!** You were paid $`{pay}`")
                        else:
                            await ctx.send(f"**Correct!** You were paid $`{pay}`")
                    else:
                        pay = int(pay * 0.5)
                        await ctx.send(f"**Incorrect!** The lead mage looks upon you with distaste - You were only paid $`{pay}`")

                except asyncio.TimeoutError:
                    pay = int(pay * 0.5)
                    await ctx.send(f"**Disappointing!** You took too long - You were only paid $`{pay}`")

                # PAY
                balance += pay
                await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

            else:
                m, s = divmod(localcooldown - last_command[author].seconds, 60)
                h, m = divmod(m, 60)
                if int(h) == 0 and int(m) == 0:
                    await ctx.send(f':card_box: You must wait **{int(s)} seconds** to work again.')
                elif int(h) == 0 and int(m) != 0:
                    await ctx.send(f':card_box: You must wait **{int(m)} minutes and {int(s)} seconds** to work again.')
                else:
                    await ctx.send(f':card_box: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to work again.')
                return

        else:
            return await ctx.send("Error: Job not null but not found.")

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send("You just did that.")

    @commands.command()
    async def beg(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        user = ctx.author
        if data["job"] is None:
            nojob = discord.Embed(title=f":dollar:  {user.name} is begging for money!", description=f"I think {user.name} should get a job! Do `,jobs` for more infortmation!", color=discord.Color.gold())
            await ctx.send(embed=nojob)
        else:
            hasjob = discord.Embed(title=f":dollar:  {user.name} is begging for money!", description=f"I think {user.name} should do their job! Do `,work` to work!", color=discord.Color.gold())
            await ctx.send(embed=hasjob)

def setup(bot):
    bot.add_cog(Jobs(bot))
