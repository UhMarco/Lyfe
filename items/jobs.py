import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

# Custom cooldown variables
on_cooldown = {}
cooldown = {"jobtype": 5}

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
            description="Earn varying amounts of money every certain amount of time.\nEach job is different so take your pick!\n**Note:** Every job requires an :card_index: **ID**",
            color=discord.Color.greyple(),
        )
        embed.add_field(name=":hamburger: Fast Food Worker", value="Just repeat the ice cream machine is broken and you'll do great.\n**Earns:** $`20` every `10 minutes`\n**Requires:** `nothing`\n`,apply fast food worker`", inline=False)
        embed.add_field(name=":broom: Janitor", value="Make some floors shiny.\n**Earns:** $`100` every `1 hour`\n**Requires:** `nothing`\n`,apply janitor`", inline=False)
        embed.add_field(name=":gun: Thief", value="Borrowing without permission for a living.\n**Earns:** $`10-200` every `1 hour`\n**Requires:** `nothing`\n`,apply thief`", inline=False)
        embed.add_field(name=":mage: Mage", value="You'll encounter many weird words called spells.\n**Earns:** $`150` every `45 minutes`.\n**Requires:** `nothing`\n`,apply mage`", inline=False)
        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(Jobs(bot))
