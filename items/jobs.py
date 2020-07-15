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
    async def apply(self, ctx, *, job):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")
        check = data["job"]
        if check is not None:
            return await ctx.send("Please resign from your current job before applying elsewhere.")

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
            job = "Fast Food Worker"
            emoji = ":hamburger:"

            # WORK

            # PAY
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

        elif job == "janitor":
            job = "Janitor"
            emoji = ":broom:"

            # WORK

            # PAY
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": balance})

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

                # WORK

                # PAY
                balance += 150
                embed = discord.Embed(title=f"You went to work as a {emoji} **{job}** and earned $`150`", color=discord.Color.greyple())
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

        else:
            return await ctx.send("Error: Job not null but not found.")


def setup(bot):
    bot.add_cog(Jobs(bot))
