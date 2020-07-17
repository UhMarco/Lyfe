import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json

class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("- Utilities Cog loaded")

    @commands.command()
    async def avatar(self, ctx, user:discord.Member):
        embed = discord.Embed(title=f"**{user.name}'s** Avatar", color=discord.Color.dark_blue())
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title=f"**{ctx.author.name}'s** Avatar", color=discord.Color.dark_blue())
            embed.set_image(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("I couldn't find that user.")

    @commands.command(name="8ball")
    async def _8Ball(self, ctx, *, question):
        responses = ["Outlook not clear, try again later", "Sorry m8, try again", "mhm", "idk, u tell me", "lol", "Absolutely!", "Absolutely not.", "It is yes.", "It is no.", "Do what Jesus would do", "Nahhhh", "Sure I guess...", ]
        wisdom = random.choice(responses)
        embed = discord.Embed(title=f'**{ctx.author.name}** asked: "{question}"', description=f'**8ball says:** {wisdom}', color=discord.Color.dark_blue())
        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Utilities(bot))
