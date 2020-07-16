import discord, platform, datetime, logging, random, time
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

# Custom cooldown variables
on_cooldown = {}
cooldown = {"fastfoodworker": 600, "janitor": 3600, "thief": 3600, "mage": 2700}

class Jobs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Jobs Cog loaded")

    # Abandoning formatting for this as I honestly can't be bothered

    @commands.command(aliases=['job'])
    async def jobs(self, ctx):
        embed = discord.Embed(
            title=":card_box: **Jobs List**",
            description="Earn varying amounts of money every certain amount of time\nEach job is different so take your pick!\n**Note:** Every job requires an :card_index: **ID**",
            color=discord.Color.greyple(),
        )
        embed.add_field(name=":hamburger: Fast Food Worker", value=f"Just repeat the ice cream machine is broken and you'll do great\n**Earns:** $`20` every `10 minutes`\n`{self.bot.prefix}apply fast food worker`", inline=False)
        embed.add_field(name=":broom: Janitor", value=f"Make some floors shiny\n**Earns:** $`100` every `1 hour`\n`{self.bot.prefix}apply janitor`", inline=False)
        embed.add_field(name=":gun: Thief", value=f"Borrowing without permission for a living\n**Earns:** $`10-200` every `1 hour`\n`{self.bot.prefix}apply thief`", inline=False)
        embed.add_field(name=":mage: Mage", value=f"You'll encounter many weird words called spells\n**Earns:** $`150` every `45 minutes`.\n`{self.bot.prefix}apply mage`", inline=False)
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
        if not any("ID" for ele in inventory):
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

        elif job == "thief":
            embed = discord.Embed(title="You successfully became a :gun: **Thief**", description="**Earns:** $`10-200` every `1 hour`", color=discord.Color.greyple())
            await self.bot.inventories.upsert({"_id": ctx.author.id, "job": "thief"})
            await ctx.send(embed=embed)

        elif job == "mage":
            embed = discord.Embed(title="You successfully became a :mage: **Mage**", description="**Earns:** $`150` every `45 minutes`", color=discord.Color.greyple())
            await self.bot.inventories.upsert({"_id": ctx.author.id, "job": "mage"})
            await ctx.send(embed=embed)

        else:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("That's not a job.")

    @commands.command()
    async def resign(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")
        job = data["job"]
        if job is None:
            return await ctx.send("You're not currently employed anywhere.")

        await self.bot.inventories.upsert({"_id": ctx.author.id, "job": None})

        if job == "fastfoodworker":
            job = "Fast Food Worker"
            emoji = ":hamburger:"
        elif job == "janitor":
            job = "Janitor"
            emoji = ":broom:"
        elif job == "thief":
            job = "Thief"
            emoji = ":gun:"
        elif job == "mage":
            job = "Mage"
            emoji = ":mage:"
        else:
            emoji = ":question:"

        embed = discord.Embed(title=f"You quit your job as a {emoji} **{job}**", color=discord.Color.greyple())
        await ctx.send(embed=embed)

    @commands.command()
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
            last_command = time.time() - on_cooldown[author]
        except KeyError:
            last_command = None
            on_cooldown[author] = time.time()

        if job == "fastfoodworker":
            localcooldown = cooldown["fastfoodworker"]

            if last_command is None or last_command > localcooldown:
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
                message = await self.bot.wait_for('message', check=check)

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

                # PAY
                balance += pay
                await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

            else:
                m, s = divmod(localcooldown - last_command, 60)
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

            if last_command is None or last_command > localcooldown:
                job = "Janitor"
                emoji = ":broom:"

                # WORK

                # PAY
                balance += 100
                embed = discord.Embed(title=f"You went to work as a {emoji} **{job}** and earned $`100`", color=discord.Color.greyple())
                await ctx.send(embed=embed)
                await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

            else:
                m, s = divmod(localcooldown - last_command, 60)
                h, m = divmod(m, 60)
                if int(h) == 0 and int(m) == 0:
                    await ctx.send(f':card_box: You must wait **{int(s)} seconds** to work again.')
                elif int(h) == 0 and int(m) != 0:
                    await ctx.send(f':card_box: You must wait **{int(m)} minutes and {int(s)} seconds** to work again.')
                else:
                    await ctx.send(f':card_box: You must wait **{int(h)} hours, {int(m)} minutes and {int(s)} seconds** to work again.')
                return

        elif job == "thief":
            job = "Thief"
            emoji = ":gun:"

            # WORK

            # PAY
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

        elif job == "mage":
            localcooldown = cooldown["mage"]

            if last_command is None or last_command > localcooldown:
                job = "Mage"
                emoji = ":mage:"
                pay = 150

                # WORK
                spells = utils.json.read_json("spells")
                spell = random.choice(spells["spells"])
                embed = discord.Embed(title=f"Type the spell `{spell}`", description="You will be rewarded 20% more if you spell it within 3 seconds.", color=discord.Color.greyple())
                await ctx.send(embed=embed)
                timer = time.time()

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author
                message = await self.bot.wait_for('message', check=check)

                if message.content.replace(" ", "").lower() == spell.replace(" ", ""):
                    if time.time() - timer <= 3:
                        pay = int(pay * 1.2)
                        await ctx.send(f"**Correct!** It took you less than 3 seconds to type the spell so you were paid extra and got $`{pay}`")
                    else:
                        await ctx.send(f"**Correct!** However you were paid the normal $`{pay} as it took you more than 3 seconds to type the spell")
                else:
                    pay = int(pay * 0.5)
                    await ctx.send(f"**Incorrect!** The lead mage looks upon you with distaste - You were only paid $`{pay}`")

                # PAY
                balance += pay
                await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

            else:
                m, s = divmod(localcooldown - last_command, 60)
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


def setup(bot):
    bot.add_cog(Jobs(bot))
